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
`<script>` but one (below), nothing loaded from any other origin, and the
system font. The one script is the home page film's scroll trigger, inline at
the end of `_includes/film.html`: it starts the film from its first frame once
half of it is on screen, stores nothing and sends nothing, and the privacy
page's "This website" note says so. The link check allows it by the hash of
its text, so any other script, or a change to this one, fails until it is
reviewed and its new hash recorded.

Jekyll stays on, which is why there is no `.nojekyll` file. The two generated
documents are Markdown, and every page, theirs and the site's own, renders
through the one layout, `_layouts/default.html`, so the head, header and footer
exist once. A site page is hand-written HTML with a few lines of front matter
naming that layout; `bare: true` keeps the layout from wrapping it in the
document column.

**Platform state.** `platform_state` in `_config.yml` is the switch for the
Apple apps: `1` while only the iPhone app is live, `2` once the watch app is.
The layout writes it to `<html data-state>` for the stylesheet, and
`support.md` reads it through Liquid, so each page carries only its own state's
answers. Change it on the day a platform goes live, and nowhere else.

Its `3` was to mean Android, on the assumption that the watch app would come
first. Android went live on Google Play first, and a `3` would also have said
the watch app was out. So Android has its own switch,
`android_live`, which the site's own pages read: the Google Play badge, the
Android section and storage line, the closing links and platform list, the
footer, and the press page's first line. `support.md` still gives its Android
answers only at `platform_state` 3, and until the mirror in `semmes/DrinkTracker`
reads `android_live` instead, its "Is there an Android app?" answer says not
yet. That change belongs in that repository, not here.

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
- `video/film-*` is the home page's film, under the hero: 30 seconds rendered by
  code from the app's own screens, colours and measurements, in light and
  dark, 1080p and 720p, HEVC and H.264, with a poster and a still for each
  appearance (and `film-clear.png`, a transparent poster;
  `_includes/film.html` says why). It is the film's page cut: every frame
  meets the page's own colour exactly at its edges, and the loop wraps with
  a fade, so the film plays straight on the page with no box around it. The
  loop is cut to start 0.8 seconds in, so its first frame is its poster.
  `_includes/film.html` picks one file per reader with media queries on its
  sources (appearance, width, and reduced motion, which gets a player that
  waits to be pressed instead of the loop), with no script; the site's one
  script only decides when the loop plays. The film downloads with the page,
  a few megabytes, which is the price of a film that is ready when a reader
  reaches it.
- `video/press-film.mp4` is the press page's film, a different one: the
  30-second product film, as a 1080p copy at 8 Mbps with its sound untouched,
  and `video/press-film-poster.jpg`, its frame at 12.8 seconds. Nothing but the
  poster loads until the reader presses play. The 4K master (175.6 MB) is not
  kept here, because GitHub refuses any file over 100 MB in a repository: it is
  attached to the release `press-film-2026-09-27`, the press page links to it
  there, and the page says the file downloads from GitHub.
- `img/icon/` and `favicon.ico` are downscales of the app icon, never redrawn.
- `img/badges/` is Apple's badge artwork, unmodified, from the App Store
  Marketing Tools page for this app: black, and white for dark pages while it is
  the only store badge on the page. One badge per layout, at least 40 px tall,
  clear space of a quarter of its height, per Apple's guidelines; the home page's
  closing section says "Available on the App Store" as a link instead.
- `img/badges/google-play.png` is Google's "Get it on Google Play" badge,
  unmodified, as Google serves it at
  `play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png`.
  One black badge for both appearances, with its clear space built in as a
  transparent margin; `css/site.css` takes that margin back and sizes the
  visible badge to 50.4 px, because Google asks that its badge be no smaller
  than another store's beside it. Where the two sit together, Apple's badge
  stays black in dark mode too (`beside_play` in
  `_includes/app-store-badge.html`). The footer carries Google's trademark
  line. The vector version is on Google's Partner Marketing Hub, behind its
  usage terms; swapping it in means a new `width`, `height` and margin, since
  it has no transparent edge.
- Copy follows the app's tone rules (report, never instruct) and goes through
  the same 1.4.3 review log as the app's own strings, in the app repository.

## Checks and deploy

`.github/workflows/site.yml` builds the site with GitHub's own Jekyll and fails
on any of:

- a link or image that resolves to nothing, or a `#fragment` with no target;
- anything a page loads from another origin, and any `<script>` but the
  film's scroll trigger, which is allowed by the hash of its text;
- an image without `alt`;
- a declared colour pair under its contrast floor, in either scheme.

Outbound links (the App Store, Google Play, GitHub, Apple's EULA) are fetched
in a separate job, on every change and daily, so a store link that stops
answering is found without holding up a policy change.

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
