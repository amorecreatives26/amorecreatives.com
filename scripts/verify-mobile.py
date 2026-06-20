#!/usr/bin/env python3
"""
verify-mobile.py — check index.html for horizontal overflow on real phone viewports.

IMPORTANT: do NOT trust `chrome --headless --window-size=390,...` screenshots for this.
Headless clamps the layout viewport to a ~500px minimum, so a 390px screenshot is just a
crop of a 500px layout and shows fake "clipping". The only reliable method is CDP device
emulation (Emulation.setDeviceMetricsOverride), which this script uses.

It loads the local file at 360px and 390px, reports scrollWidth vs innerWidth (overflow =
scrollWidth > innerWidth), and saves a full-page screenshot to /tmp/mobile-390.png.

Requires: macOS Google Chrome + `pip install websocket-client`.
Usage: python3 scripts/verify-mobile.py
"""
import base64, json, os, signal, subprocess, sys, time, urllib.request

DEBUG_PORT = 9228
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL = "file://" + os.path.join(ROOT, "index.html")

try:
    import websocket  # websocket-client
except ImportError:
    sys.exit("Missing dependency: pip install websocket-client")
if not os.path.exists(CHROME):
    sys.exit(f"Chrome not found at {CHROME}")

chrome = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu",
    f"--remote-debugging-port={DEBUG_PORT}", "--user-data-dir=/tmp/mobile-check",
    "--no-first-run", "--no-default-browser-check", "--remote-allow-origins=*", URL],
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
    _id = 0

    def cmd(method, params=None):
        global _id; _id += 1; mid = _id
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == mid:
                return m.get("result", {})

    cmd("Page.enable"); cmd("Runtime.enable")
    any_overflow = False
    for w in (360, 390):
        cmd("Emulation.setDeviceMetricsOverride",
            {"width": w, "height": 844, "deviceScaleFactor": 2, "mobile": True})
        cmd("Page.reload", {"ignoreCache": True}); time.sleep(7)
        r = cmd("Runtime.evaluate", {"returnByValue": True, "expression":
            "JSON.stringify({sw:document.documentElement.scrollWidth,iw:window.innerWidth})"})
        v = json.loads(r["result"]["value"])
        over = v["sw"] > v["iw"]
        any_overflow = any_overflow or over
        print(f"width={w}: scrollWidth={v['sw']} innerWidth={v['iw']} "
              f"{'OVERFLOW ✗' if over else 'no overflow ✓'}")

    cmd("Emulation.setDeviceMetricsOverride",
        {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True})
    cmd("Page.reload", {"ignoreCache": True}); time.sleep(7)
    shot = cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
    open("/tmp/mobile-390.png", "wb").write(base64.b64decode(shot["data"]))
    print("screenshot -> /tmp/mobile-390.png")
    print("\nRESULT:", "FAIL — horizontal overflow on mobile" if any_overflow
          else "PASS — no horizontal overflow ✓")
    sys.exit(1 if any_overflow else 0)
finally:
    chrome.send_signal(signal.SIGTERM); chrome.wait()
