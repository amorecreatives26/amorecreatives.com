# Amore Creatives — site repo (Claude handoff & instructions)

Static one-page marketing site for **amorecreatives.com**, deployed via **GitHub Pages**
on a custom domain (`CNAME`). No framework, no build server. This file auto-loads at the
start of every Claude Code session — read it first.

---

## Current status (last updated 2026-06-21)
- ✅ **Live & deployed.** Latest changes are committed and pushed to `origin/main`; GitHub
  Pages has rebuilt. (`git diff` looking empty just means work is committed, not missing.)
- ✅ **SEO complete.** Shell `<head>` has real title, meta description, canonical, robots,
  Open Graph, Twitter, two JSON-LD blocks (`Organization` + `ProfessionalService`),
  `lang="en"`, theme-color, and 3 real favicon links. Template `<head>` also has
  title/description/canonical for Google's JS render. Verified valid + no duplicate tags.
- ✅ **Pre-JS crawlable body.** The bundle assembles the whole page from a JS blob, so the
  raw body is otherwise just an "Unpacking..." preloader. We inject a hidden
  `<main id="__ac_seo">` (real h1 + service summary + contact) that sits *behind* the
  full-screen `#__bundler_thumbnail` overlay and is replaced when JS runs — so real users
  never see it, but every crawler (JS or not, noscript-aware or not) reads real content.
  This is the mitigation for the inherent JS-render indexing risk (see "Known limitation").
- ✅ **robots.txt + sitemap.xml live** (HTTP 200). Sitemap is a single URL — the site is
  **single-page**; `/services`, `/network`, `/contact` are nav views, NOT crawlable routes
  (they 404). Do not add them to the sitemap. Contact email is `contact@amorecreatives.com`.
- ✅ **Google Analytics working** (GA4 `G-QZ5SEZVZBH`). Verified a real `/g/collect` hit is
  sent — run `python3 scripts/check-ga.py` to re-confirm (PASS).
- ✅ **Mobile responsive.** No horizontal overflow at 360/390px — run
  `python3 scripts/verify-mobile.py` (PASS). The hero was redesigned to a
  "Connecting Brands With Creators" / "Influencer Marketing Agency" concept; the site is
  now effectively single-page (older multi-view Network/Services table pages consolidated).

---

## Architecture (important)
`index.html` is **not** hand-written — it is a **single-file bundle exported from
Claude Design**. The real page (HTML/CSS, content, fonts, images) lives gzip+base64
encoded inside `<script type="__bundler/template">` and is assembled in the browser by
JavaScript on load (it replaces `document.documentElement`). Editable source is the
Claude Design project (locally: `*.dc.html` + `support.js` + `image-slot.js`, git-ignored).

**Consequence:** you cannot meaningfully edit the page's design, content, or
responsiveness by hand-editing `index.html`. Those changes are made in **Claude Design**
and re-exported. Only the SEO/analytics shell layer is patched locally (see below).

---

## MANDATORY workflow after every Claude Design re-export
A fresh export may or may not include SEO, and embeds favicons as JS-only blob UUIDs that
don't help the static tab icon or crawlers. So after replacing `index.html`:

```bash
python3 scripts/apply-seo.py
```

`apply-seo.py` is **idempotent and gap-filling** — it adds only what's missing and never
duplicates tags Claude Design already emitted. It ensures: `lang="en"`, full SEO head
(only if the export lacks it), `Organization` + `ProfessionalService` JSON-LD, 3 real
favicon links in the shell, a readable `<noscript>` fallback, the pre-JS crawlable body
block (`id="__ac_seo"`), gtag (`G-QZ5SEZVZBH`), and title/description/canonical in the
template head. Per-feature presence checks make re-runs safe (zero changes on re-run).
Edit the CONFIG block at the top if brand copy / GA id / canonical URL / contact email change.

Then verify before deploying:
```bash
python3 scripts/verify-mobile.py   # PASS = no horizontal overflow at 360/390px
python3 scripts/check-ga.py        # PASS = GA4 hit fires
```

---

## Verification notes (avoid these traps)
- **Mobile:** do NOT judge mobile from `chrome --headless --window-size=390,...`
  screenshots — headless clamps the layout viewport to ~500px min, so a 390px screenshot
  is a crop of a 500px layout and shows *fake* clipping. Use `scripts/verify-mobile.py`,
  which uses CDP device emulation (the only reliable method). It also saves
  `/tmp/mobile-390.png` for a real full-page mobile screenshot.
- **GA:** test the LOCAL file (`scripts/check-ga.py` serves it over HTTP), not the live
  URL. Hitting `https://amorecreatives.com/` repeatedly with an automated browser triggers
  GitHub's anti-bot page ("Are you sure you want to do this?" / HTTP 403) — a testing
  artifact only; real visitors are unaffected. `curl` of the live HTML still works for
  spot-checking that a deploy went out.

---

## Known limitation — JS rendering (inherent to Claude Design)
The page is assembled client-side from a gzip+base64 blob; the bundle replaces
`document.documentElement` on load. So the *primary* content is JS-gated, which is a real
(not fatal) indexing risk for a new domain — Google renders JS but queues it slower than
static HTML. We mitigate as far as the architecture allows: full `<head>` SEO + two JSON-LD
blocks + `<noscript>` fallback + the hidden `#__ac_seo` body block all live in the raw HTML.
The only way to fully remove the risk is to abandon the Claude Design bundle for genuine
static HTML — a large change the owner has chosen not to make. A periodic SEO audit
(e.g. claude.ai) may flag "body shows only 'Unpacking...'" — that audit reads the rendered
body and ignores `<noscript>` and the hidden block; treat such findings against the
verified raw-HTML facts before acting. Past audits have also assumed a 4-page site and
suggested `/services /network /contact` sitemap entries and a `hello@` email — both wrong
for this site (single-page; `contact@amorecreatives.com`).

## Rules
- **Never run `git commit` or `git push`.** Committing/pushing is the user's job (also
  hard-blocked by a deny rule in `~/.claude/settings.json`). Stage/prepare only.
- **Deploy-clean:** only these are served publicly — `index.html`, `CNAME`, `robots.txt`,
  `sitemap.xml`, `og-image.png`, `assets/`, `scripts/`, `CLAUDE.md`. Design/process files
  (`uploads/`, `screenshots/`, `*.dc.html`, `support.js`, `image-slot.js`) are git-ignored.
- `.claude/` is tracked in this repo (a `.gitignore` negation re-includes
  `settings.local.json`, which your global gitignore would otherwise hide). Note that
  `settings.local.json` is a personal/local permission cache and changes often.

---

## Open items / backlog
- **Google Search Console (manual, do once):** add `amorecreatives.com`, verify, submit
  `https://amorecreatives.com/sitemap.xml`, then Request Indexing on the homepage. This is
  what gets the site crawled in days rather than weeks. (Cannot be automated here.)
- **Optional copy alignment:** the live `<title>`/meta still say "Fully Managed Influencer
  Marketing" while the redesigned hero leads with "Influencer Marketing Agency /
  Connecting Brands With Creators." Still accurate, but if you want them to match, edit
  `TITLE`/`OG_TITLE`/`DESCRIPTION` in `scripts/apply-seo.py` and re-run it.
- **Confirm GA in the dashboard:** open the live site in a normal browser and check
  GA4 → Reports → Realtime (should show 1 active user). If empty despite the hit firing,
  it's GA-account-side (data stream / internal-traffic filter), not the site.

---

## File map
- `index.html` — the deployed bundle (Claude Design export + SEO shell patch).
- `scripts/apply-seo.py` — idempotent SEO/analytics shell patcher (run after every export).
- `scripts/check-ga.py` — verify GA4 actually fires (serves locally + CDP network capture).
- `scripts/verify-mobile.py` — verify no mobile horizontal overflow (CDP device emulation).
- `og-image.png` — 1200×630 social share image (referenced by OG/Twitter meta).
- `robots.txt`, `sitemap.xml` — crawler directives.
- `assets/favicon-{16,32,180}.png` — favicons referenced by the shell head.
