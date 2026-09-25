# Tallyist: the public site

This repository is Tallyist's public website: the product pages, and the two
documents the App Store requires, its **privacy policy** and its **support
page**. It is served at **<https://tallyist.co/>**. GitHub answers every
`semmes.github.io/Tallyist/...` address with a permanent redirect to the same
path on tallyist.co, so the links already inside shipped copies of the app keep
working.

It is a separate repository so that these pages stay publicly readable, with
their full history, whatever happens to the app's source repository. The copy of
the privacy policy inside the app says every change to it is visible in this
repository's history, and this repository is where that stays true.

| Page | Source | Published at |
| --- | --- | --- |
| Home | `index.html` | `/` |
| Apple Watch | `watch/index.html` | `/watch/` |
| Privacy Policy | `privacy-policy.md` (generated) | `/privacy/` |
| Support | `support.md` (generated) | `/support/` |
| Press | `press/index.html` | `/press/` |
| Not found | `404.html` | any other address |

## The two generated documents

**`privacy-policy.md` and `support.md` are generated. Do not edit them here.**

The app's source repository, `semmes/DrinkTracker`, holds the canonical copies
under `docs/`, because the policy's claims are written to be checkable against the
app's privacy manifest and entitlements, and the support page's answers describe
shipping behaviour. On merge there, a workflow renders these two files and pushes
them here: the same bodies with Jekyll front matter added, and with the policy's
two web-only lines (an email address for questions, no pointer to a repository)
in place of the canonical ones. A daily check fails if what is published here has
drifted from what the app repository says it should be, so a hand-edit here is
reported rather than quietly kept (ADR-0024 in that repository).

The privacy policy also ships inside the app, so a policy change touches three
copies: `docs/privacy-policy.md` and `PrivacyPolicyView.swift` in the app
repository, and `privacy-policy.md` here. All three carry the same "Last updated"
date.

## The pages

Plain HTML and CSS, written by hand, with no framework and no build step to run
locally. The rules for every page: a `<meta name="apple-itunes-app">` line, no
`<script>`, nothing loaded from any other origin, and the system font.

Jekyll stays on, which is why there is no `.nojekyll` file. The two generated
documents are Markdown, and every page, theirs and the site's own, renders
through the one layout, `_layouts/default.html`, so the head, header and footer
exist once. A site page is hand-written HTML with a few lines of front matter
naming that layout; `bare: true` keeps the layout from wrapping it in the
document column.

**Platform state.** `platform_state` in `_config.yml` is the site's one switch:
`1` while only the iPhone app is live, `2` once the watch app is, `3` once
Android is. The layout writes it to `<html data-state>` for the stylesheet, and
`support.md` reads it through Liquid, so each page carries only its own state's
answers. Change it on the day a platform goes live, and nowhere else.

- `css/site.css` is the site design's tokens (which mirror the app's
  `docs/design-system.md`) and every rule. Colour pairs are declared in the
  stylesheet as `/* @contrast --label on --surface: text */` and measured in
  both schemes on every build.
- `_includes/` holds the markup for a device picture, a close-up, and the App
  Store badge, so a page names a screen and its description and nothing else.
- `img/screens/` is the app inside Apple's own device images, one flattened
  picture per screen, in WebP at 1x and 2x with a PNG for browsers without WebP.
  `scripts/make-images.py` makes them, the link preview (`img/og/home.png`) and
  the press kit (`img/press/`) from the site design's screenshots and Apple's
  Product Bezels. The bezels open only after agreeing to Apple's License
  Agreement for Apple Design Resources (the owner agreed on 2026-09-24), and
  they are never committed here: the license allows images of the app shown in
  the device, not the device art passed on by itself. Apple's marketing
  guidelines add the rest: a device used whole, with nothing cropped, tilted or
  drawn over it and no shadow; one App Store badge per page; and the credit line
  for Apple's trademarks, which is in the footer. Close-ups are crops of a
  screenshot with no device in them.
- `img/icon/` and `favicon.ico` are downscales of the app icon, never redrawn.
- `img/badges/` is Apple's badge artwork, unmodified, from the App Store
  Marketing Tools page for this app: black, and white for dark pages while it is
  the only store badge on the page. One badge per layout, at least 40 px tall,
  clear space of a quarter of its height, per Apple's guidelines; the home page's
  closing section says "Available on the App Store" as a link instead.
- Copy follows the app's tone rules (report, never instruct) and goes through
  the same 1.4.3 review log as the app's own strings, in the app repository.

## Checks and deploy

`.github/workflows/site.yml` builds the site with GitHub's own Jekyll and fails
on any of:

- a link or image that resolves to nothing, or a `#fragment` with no target;
- anything a page loads from another origin, and any `<script>`;
- an image without `alt`;
- a declared colour pair under its contrast floor, in either scheme.

Outbound links (the App Store, GitHub, Apple's EULA) are fetched in a separate
job, on every change and daily, so a store link that stops answering is found
without holding up a policy change.

```
python3 scripts/check-links.py _site
python3 scripts/contrast.py css/site.css
```

**Launch, in this order:** set Settings, Pages, Source to "GitHub Actions"; then
set the repository variable `DEPLOY_FROM_ACTIONS` to `true`. Until both are done,
Pages keeps building from the main branch as it always has and the workflow only
checks.

## The domain

`tallyist.co` is the canonical address. It is set in Settings, Pages, Custom
domain, not in a `CNAME` file, which GitHub ignores for sites deployed by a
workflow. The same commit that attaches it changes `url` and `baseurl` in
`_config.yml`. `www.tallyist.co` redirects to it; `tallyist.net`, `.org` and
`.info` are registrar forwards and are never linked or listed in the sitemap.

## Questions

Questions about the app, or about these pages, belong in
[Issues](https://github.com/semmes/Tallyist/issues).
