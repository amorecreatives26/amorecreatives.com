# Amore Creatives — site repo

Static one-page marketing site for **amorecreatives.com**, deployed via **GitHub Pages**
on a custom domain (see `CNAME`). No framework, no build server.

## Architecture (important)
`index.html` is **not** hand-written — it is a **single-file bundle exported from
Claude Design**. The real page (HTML/CSS, content, fonts, images) lives gzip+base64
encoded inside `<script type="__bundler/template">` and is assembled in the browser by
JavaScript. The editable source is the Claude Design project (locally:
`*.dc.html` + `support.js` + `image-slot.js`, which are git-ignored — see below).

Consequence: **you cannot meaningfully edit the page's design or content by editing
`index.html`.** Layout/content/responsiveness changes must be made in **Claude Design**
and re-exported.

## MANDATORY after every Claude Design re-export
The bundler wraps the page in an outer shell whose `<head>` only says
`<title>Bundled Page</title>` — the part crawlers (and non-JS AI bots) read first, and
which Claude Design does not control. So **every time `index.html` is replaced with a
fresh export, run:**

```bash
python3 scripts/apply-seo.py
```

This idempotently injects the real title, meta description, canonical, robots, Open
Graph, Twitter, JSON-LD, favicons, Google Analytics (gtag `G-QZ5SEZVZBH`) and a readable
`<noscript>` fallback into the outer shell, plus title/description/canonical into the
template `<head>` for Google's JS-rendered pass. A `<!-- seo-shell:applied -->` marker
makes re-runs safe. Edit the CONFIG block in the script if brand copy / GA id / URL change.

After running, verify mobile + crawlability (see "Verifying" below).

## Rules
- **Never run `git commit` or `git push`.** Committing is the user's job (also hard-blocked
  by a deny rule in `~/.claude/settings.json`). Stage/prepare only.
- Keep the deploy clean: only these are served publicly — `index.html`, `CNAME`,
  `robots.txt`, `sitemap.xml`, `og-image.png`, `assets/`, and `scripts/`. Design/process
  files (`uploads/`, `screenshots/`, `*.dc.html`, `support.js`, `image-slot.js`) are
  git-ignored so they never reach the public site.

## Verifying
- **SEO/crawlability:** confirm `<title>Amore Creatives` appears in the static shell head
  (not "Bundled Page"), JSON-LD parses, and `og-image.png` / `robots.txt` / `sitemap.xml`
  exist.
- **Mobile:** the Claude Design source historically had *no* `@media` queries; render the
  bundle at phone width to catch overflow before deploying:
  ```bash
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
    --disable-gpu --hide-scrollbars --window-size=390,11000 --virtual-time-budget=9000 \
    --screenshot=/tmp/m.png "file://$PWD/index.html"
  ```
  Known historical breaks to check: hero device mockup overflowing the right edge, and the
  "two ways to run a campaign" comparison cards not stacking.

## Discoverability — manual steps (cannot be automated here)
In **Google Search Console**: add `amorecreatives.com`, verify, submit
`https://amorecreatives.com/sitemap.xml`, then Request Indexing on the homepage.
