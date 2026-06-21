#!/usr/bin/env python3
"""
apply-seo.py — ensure the crawler-facing SEO layer on a Claude Design bundle export.

index.html is a single-file bundle exported from Claude Design. Depending on the
export, the outer shell <head> may already contain SEO (newer exports) or may be a
bare bundler wrapper with "<title>Bundled Page</title>" (older ones). This script is
GAP-FILLING and idempotent: it adds only what is missing and never duplicates tags
that are already present. Run it after every export:

    python3 scripts/apply-seo.py

Edit the CONFIG block if brand copy / GA id / canonical URL change.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "index.html")
MARKER = "<!-- seo-shell:applied -->"

# ---------------------------------------------------------------- CONFIG ----
CANONICAL   = "https://amorecreatives.com/"
GA_ID       = "G-QZ5SEZVZBH"
OG_IMAGE    = "https://amorecreatives.com/og-image.png"
TITLE       = "Amore Creatives — Fully Managed Influencer Marketing for DTC Brands"
DESCRIPTION = ("Amore Creatives runs end-to-end influencer campaigns for DTC and growing "
               "brands. You approve the strategy — we handle sourcing, outreach, contracts, "
               "coordination and reporting.")
OG_TITLE    = "Fully Managed Influencer Marketing for DTC Brands"
OG_DESC     = ("We run your influencer campaigns so your team doesn't have to — sourcing, "
               "outreach, contracts, coordination and reporting, end to end.")
CONTACT_EMAIL = "contact@amorecreatives.com"

CHARSET = '<meta charset="utf-8">'
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'

# Full head block — only injected when the shell has NO real SEO (bare bundler export)
HEAD_BLOCK = f"""
  <!-- Primary SEO -->
  <title>{TITLE}</title>
  <meta name="description" content="{DESCRIPTION}">
  <link rel="canonical" href="{CANONICAL}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="author" content="Amore Creatives">
  <meta name="theme-color" content="#0b1a2e">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Amore Creatives">
  <meta property="og:title" content="{OG_TITLE}">
  <meta property="og:description" content="{OG_DESC}">
  <meta property="og:url" content="{CANONICAL}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Amore Creatives — fully managed influencer marketing">
  <meta property="og:locale" content="en_US">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{OG_TITLE}">
  <meta name="twitter:description" content="{OG_DESC}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Organization","name":"Amore Creatives","url":"{CANONICAL}","logo":"https://amorecreatives.com/assets/favicon-180.png","image":"{OG_IMAGE}","description":"Full-service influencer marketing management for DTC brands and growing companies. Amore Creatives handles sourcing, outreach, contracts, coordination and reporting end to end.","email":"{CONTACT_EMAIL}","contactPoint":{{"@type":"ContactPoint","email":"{CONTACT_EMAIL}","contactType":"Sales"}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"ProfessionalService","name":"Amore Creatives","url":"{CANONICAL}","image":"{OG_IMAGE}","description":"Fully managed influencer marketing for DTC and growing brands. Amore Creatives handles sourcing, outreach, contracts, coordination and reporting end to end — the brand approves the strategy, we execute the campaign.","slogan":"We run your influencer campaigns so your team doesn't have to.","areaServed":"Worldwide","serviceType":"Influencer marketing campaign management","knowsAbout":["Influencer marketing","Creator sourcing and outreach","Campaign management","DTC brand marketing","Influencer contracts and coordination","Campaign reporting"],"offers":{{"@type":"Offer","description":"Done-for-you influencer campaign management: brief approval, creator briefing, live campaign tracking and a single final report."}}}}
  </script>
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
"""

FAVICON_BLOCK = """  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon-180.png">
"""

NOSCRIPT_BLOCK = """  <noscript>
    <style>
      #__bundler_loading, #__bundler_thumbnail { display: none !important; }
      .ac-fallback { max-width: 720px; margin: 0 auto; padding: 48px 24px; color: #0b1a2e; line-height: 1.6; }
      .ac-fallback h1 { font-family: Georgia, serif; font-size: 2rem; margin-bottom: .5rem; }
      .ac-fallback h2 { font-size: 1.1rem; margin: 1.5rem 0 .5rem; }
      .ac-fallback p { margin-bottom: 1rem; }
      .ac-fallback ol { margin: 0 0 1rem 1.25rem; }
    </style>
    <main class="ac-fallback">
      <h1>Amore Creatives — Fully Managed Influencer Marketing</h1>
      <p>We run your influencer campaigns so your team doesn't have to. Amore Creatives
      offers full-service campaign management for DTC brands and growing companies.
      You approve the strategy — we handle sourcing, outreach, contracts, coordination
      and reporting.</p>
      <h2>What we handle</h2>
      <p>Everything from the first shortlist to the closing report. Your only job is
      approval. We operate as your outsourced influencer team with one point of contact
      and one final report per campaign.</p>
      <h2>How a campaign flows</h2>
      <ol>
        <li><strong>Brief approved</strong> — you sign off the strategy and shortlist.</li>
        <li><strong>Creators briefed</strong> — we coordinate content, product and timing.</li>
        <li><strong>Campaign live</strong> — posts go out and we track every one.</li>
        <li><strong>Report delivered</strong> — one clear summary of what the campaign did.</li>
      </ol>
      <h2>Our network</h2>
      <p>A curated network of trusted influencers across key niches. We hold direct
      relationships as community moderators — warm reach, not cold outreach. Named
      profiles and rate cards are shared with qualified brands under NDA.</p>
      <p>This site requires JavaScript for the full interactive experience.</p>
    </main>
  </noscript>"""

# Standalone Organization JSON-LD — gap-filled when an export already has SEO but no
# Organization block (detected by the absence of '"@type":"Organization"').
ORG_BLOCK = (
    '  <script type="application/ld+json">\n'
    '  {"@context":"https://schema.org","@type":"Organization","name":"Amore Creatives",'
    f'"url":"{CANONICAL}","logo":"https://amorecreatives.com/assets/favicon-180.png",'
    f'"image":"{OG_IMAGE}","description":"Full-service influencer marketing management for '
    'DTC brands and growing companies. Amore Creatives handles sourcing, outreach, contracts, '
    f'coordination and reporting end to end.","email":"{CONTACT_EMAIL}",'
    f'"contactPoint":{{"@type":"ContactPoint","email":"{CONTACT_EMAIL}","contactType":"Sales"}}}}\n'
    '  </script>\n'
)

# Pre-JS crawlable body content. Sits behind the full-screen #__bundler_thumbnail overlay
# (z-index:9999) so real users never see it, and the bundle's JS replaces the whole
# document on load. Guarantees crawlers reading the raw body get real content, not just
# the "Unpacking..." preloader. Marked by id="__ac_seo".
BODY_SEO_BLOCK = (
    '\n  <main id="__ac_seo" style="position:absolute;left:0;top:0;z-index:1;max-width:720px;'
    'padding:48px 24px;color:#0b1a2e;font-family:Georgia,serif;line-height:1.6">\n'
    '    <h1>Amore Creatives — Fully Managed Influencer Marketing</h1>\n'
    "    <p>We run your influencer campaigns so your team doesn't have to. Amore Creatives "
    'offers full-service campaign management for DTC brands and growing companies. You approve '
    'the strategy — we handle sourcing, outreach, contracts, coordination and reporting.</p>\n'
    '    <h2>What we handle</h2>\n'
    '    <p>Everything from the first shortlist to the closing report. Your only job is approval. '
    'We operate as your outsourced influencer team with one point of contact and one final report '
    'per campaign.</p>\n'
    '    <h2>How a campaign flows</h2>\n'
    '    <ol>\n'
    '      <li><strong>Brief approved</strong> — you sign off the strategy and shortlist.</li>\n'
    '      <li><strong>Creators briefed</strong> — we coordinate content, product and timing.</li>\n'
    '      <li><strong>Campaign live</strong> — posts go out and we track every one.</li>\n'
    '      <li><strong>Report delivered</strong> — one clear summary of what the campaign did.</li>\n'
    '    </ol>\n'
    '    <h2>Our network</h2>\n'
    '    <p>A curated network of trusted influencers across key niches. We hold direct relationships '
    'as community moderators — warm reach, not cold outreach. Named profiles and rate cards are '
    'shared with qualified brands under NDA.</p>\n'
    f'    <p>Contact: {CONTACT_EMAIL}</p>\n'
    '  </main>\n'
)

# Template-head injection (Google's JS render). Stored JSON-escaped: \" and \/.
TPL_ANCHOR = r'<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">'
TPL_INJECT = (r'\n<title>' + TITLE + r'<\/title>'
              r'\n<meta name=\"description\" content=\"' + DESCRIPTION + r'\">'
              r'\n<link rel=\"canonical\" href=\"' + CANONICAL + r'\">')


def insert_after(s, anchor, block):
    i = s.find(anchor)
    if i == -1:
        return s, False
    i += len(anchor)
    return s[:i] + "\n" + block + s[i:], True


def main():
    if not os.path.exists(FILE):
        sys.exit(f"ERROR: {FILE} not found")
    s = open(FILE, encoding="utf-8").read()
    notes = []

    shell = s[:s.find('<script type="__bundler/template"') or len(s)]

    # 1) lang ------------------------------------------------------------------
    if "<html lang=" not in shell and "<html>" in shell:
        s = s.replace("<html>", '<html lang="en">', 1); notes.append("added <html lang>")

    # 2) full SEO head block — only if the shell has no real SEO yet ------------
    has_seo = ('rel="canonical"' in shell) or ("<title>Amore Creatives" in shell)
    if not has_seo:
        s = re.sub(r"\s*<title>Bundled Page</title>", "", s, count=1)
        s, ok = insert_after(s, CHARSET, HEAD_BLOCK.lstrip("\n"))
        notes.append("injected full SEO head block (bare export)" if ok
                     else "WARN charset anchor not found — SEO block not injected")
    else:
        notes.append("SEO head already present — not re-injecting")

    # 3) favicons (check the SHELL only — CD may embed favicons as UUID blobs in
    #    the template, which don't help the static tab icon or crawlers) ---------
    shell_now = s[:s.find('<script type="__bundler/template"') or len(s)]
    if "apple-touch-icon" not in shell_now:
        anchor = VIEWPORT if VIEWPORT in shell_now else CHARSET
        s, ok = insert_after(s, anchor, FAVICON_BLOCK)
        notes.append("added favicons" if ok else "WARN no anchor for favicons")
    else:
        notes.append("favicons already present")

    # 4) rich noscript ---------------------------------------------------------
    if "ac-fallback" not in s:
        new = re.sub(r"<noscript>\s*<style>#__bundler_loading.*?</noscript>",
                     NOSCRIPT_BLOCK, s, count=1, flags=re.S)
        if new == s:
            new = re.sub(r"<noscript>.*?requires JavaScript.*?</noscript>",
                         NOSCRIPT_BLOCK, s, count=1, flags=re.S)
        if new != s:
            s = new; notes.append("replaced stock noscript with rich fallback")
        else:
            s = s.replace("</head>", NOSCRIPT_BLOCK + "\n</head>", 1)
            notes.append("injected rich noscript before </head>")
    else:
        notes.append("rich noscript already present")

    # 4b) Organization schema (gap-fill if SEO present but no Organization block) ---
    if '"@type":"Organization"' not in s:
        anchor = '<meta name="twitter:image" content="' + OG_IMAGE + '">'
        if anchor in s:
            s, ok = insert_after(s, anchor, ORG_BLOCK)
            notes.append("added Organization schema" if ok else "WARN org anchor failed")
        else:
            notes.append("WARN no twitter:image anchor — Organization schema not added")
    else:
        notes.append("Organization schema already present")

    # 4c) pre-JS crawlable body content (mirrors noscript, behind the preloader) -----
    if 'id="__ac_seo"' not in s:
        anchor = '<div id="__bundler_loading">Unpacking...</div>'
        if anchor in s:
            s, ok = insert_after(s, anchor, BODY_SEO_BLOCK)
            notes.append("added pre-JS body content" if ok else "WARN body anchor failed")
        else:
            # fall back to just after <body>
            m = re.search(r"<body[^>]*>", s)
            if m:
                i = m.end(); s = s[:i] + BODY_SEO_BLOCK + s[i:]
                notes.append("added pre-JS body content (after <body>)")
            else:
                notes.append("WARN no <body> anchor — body content not added")
    else:
        notes.append("pre-JS body content already present")

    # 5) template head SEO (Google JS render) ----------------------------------
    ti = s.find('type="__bundler/template">')
    if ti == -1:
        notes.append("WARN bundle template tag not found")
    elif "<title>" in s[ti:ti + 6000]:
        notes.append("template title already present")
    elif TPL_ANCHOR in s:
        pos = s.find(TPL_ANCHOR) + len(TPL_ANCHOR)
        s = s[:pos] + TPL_INJECT + s[pos:]; notes.append("injected template head SEO")
    else:
        notes.append("WARN template viewport anchor not found")

    # 6) idempotency marker ----------------------------------------------------
    if MARKER not in s:
        s, _ = insert_after(s, CHARSET, "  " + MARKER); notes.append("added marker")

    open(FILE, "w", encoding="utf-8").write(s)

    for rel in ["og-image.png", "robots.txt", "sitemap.xml",
                "assets/favicon-16.png", "assets/favicon-32.png", "assets/favicon-180.png"]:
        if not os.path.exists(os.path.join(ROOT, rel)):
            notes.append(f"asset MISSING: {rel}")

    print("apply-seo.py:")
    for n in notes:
        print("  -", n)


if __name__ == "__main__":
    main()
