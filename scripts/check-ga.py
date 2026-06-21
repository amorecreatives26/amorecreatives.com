#!/usr/bin/env python3
"""
check-ga.py — verify Google Analytics actually fires for the built index.html.

It serves the repo over real HTTP (GA can behave oddly on file://), loads the page
in headless Chrome via the DevTools protocol, and confirms that:
  - gtag.js loads from googletagmanager.com
  - window.gtag / window.dataLayer initialise
  - a real GA4 measurement hit is sent to google-analytics.com/g/collect

WHY LOCAL, NOT THE LIVE URL: hitting https://amorecreatives.com/ repeatedly with an
automated browser triggers GitHub's anti-bot challenge ("Are you sure you want to do
this?" / HTTP 403), which is a testing artifact, NOT a problem for real visitors.
Testing the local file proves the deployed artifact is correct.

Requires: macOS Google Chrome + `pip install websocket-client`.
Usage: python3 scripts/check-ga.py
"""
import json, os, signal, subprocess, sys, time, urllib.request

GA_ID = "G-QZ5SEZVZBH"
PORT = 8771
DEBUG_PORT = 9227
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

try:
    import websocket  # websocket-client
except ImportError:
    sys.exit("Missing dependency: pip install websocket-client")
if not os.path.exists(CHROME):
    sys.exit(f"Chrome not found at {CHROME}")

srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--directory", ROOT],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
chrome = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu",
    f"--remote-debugging-port={DEBUG_PORT}", "--user-data-dir=/tmp/ga-check",
    "--no-first-run", "--no-default-browser-check", "--remote-allow-origins=*",
    f"http://localhost:{PORT}/index.html"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    ws_url = None
    for _ in range(40):
        try:
            data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json/list"))
            pages = [t for t in data if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]
            if pages:
                ws_url = pages[0]["webSocketDebuggerUrl"]; break
        except Exception:
            pass
        time.sleep(0.25)
    assert ws_url, "could not reach Chrome DevTools"
    ws = websocket.create_connection(ws_url, max_size=None)
    _id = 0; reqs = []

    def send(method, params=None):
        global _id; _id += 1; mid = _id
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}})); return mid

    send("Network.enable"); send("Page.enable"); send("Runtime.enable")
    send("Page.reload", {"ignoreCache": True})
    t0 = time.time()
    while time.time() - t0 < 12:
        try:
            ws.settimeout(2); m = json.loads(ws.recv())
        except Exception:
            continue
        if m.get("method") == "Network.requestWillBeSent":
            u = m["params"]["request"]["url"]
            if any(k in u for k in ("google-analytics", "googletagmanager", "/collect")):
                reqs.append(u)

    def ev(expr):
        i = send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == i:
                return m.get("result", {}).get("result", {}).get("value")

    gtag = ev("typeof window.gtag")
    dl = ev("Array.isArray(window.dataLayer)?window.dataLayer.length:0")
    loaded = any("gtag/js" in u for u in reqs)
    hit = any("/collect" in u for u in reqs)
    print(f"gtag function   : {gtag}")
    print(f"dataLayer       : {dl} events")
    print(f"gtag.js request : {'YES' if loaded else 'no (served from cache — not decisive)'}")
    print(f"GA4 /collect hit: {'YES' if hit else 'NO'}")
    for u in reqs:
        print("   ", u[:140])
    # The /collect beacon is the authoritative signal — it cannot fire unless gtag.js
    # loaded and initialised. The gtag/js library request itself is cache-dependent on
    # reload, so it is NOT part of the pass condition.
    ok = gtag == "function" and hit
    print("\nRESULT:", "PASS — Google Analytics is firing ✓" if ok else "FAIL — GA not firing")
    sys.exit(0 if ok else 1)
finally:
    for p in (chrome, srv):
        p.send_signal(signal.SIGTERM); p.wait()
