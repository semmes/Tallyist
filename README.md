# Tallyist: the public site

This repository is Tallyist's public website: the product pages, and the two
documents the App Store requires, its **privacy policy** and its **support
page**. It is served at **<https://semmes.github.io/Tallyist/>**, and will be at
**<https://tallyist.co/>** once that domain is attached. From then on GitHub
answers every `semmes.github.io/Tallyist/...` address with a permanent redirect
to the same path on tallyist.co, so the links already inside shipped copies of
the app keep working.

It is a separate repository so that these pages stay publicly readable, with
their full history, whatever happens to the app's source repository. The privacy
policy says every change to it is visible in a public history, and this
repository is where that stays true.

| Page | Source | Published at |
| --- | --- | --- |
| Privacy Policy | `privacy-policy.md` (generated) | `/privacy/` |
| Support | `support.md` (generated) | `/support/` |
| Home | `index.md`, to be replaced by the site's `index.html` | `/` |

## The two generated documents

**`privacy-policy.md` and `support.md` are generated. Do not edit them here.**

The app's source repository, `semmes/DrinkTracker`, holds the canonical copies
under `docs/`, because the policy's claims are written to be checkable against the
app's privacy manifest and entitlements, and the support page's answers describe
shipping behaviour. On merge there, a workflow renders these two files (the same
bodies with Jekyll front matter added) and pushes them here. A daily check fails
if what is published here has drifted from what the app repository says it should
be, so a hand-edit here is reported rather than quietly kept (ADR-0024 in that
repository).

The privacy policy also ships inside the app, so a policy change touches three
copies: `docs/privacy-policy.md` and `PrivacyPolicyView.swift` in the app
repository, and `privacy-policy.md` here. All three carry the same "Last updated"
date.

## The pages

Plain HTML and CSS, written by hand, with no framework and no build step to run
locally. The rules for every page: a `<meta name="apple-itunes-app">` line, no
`<script>`, nothing loaded from any other origin, and the system font.

Jekyll stays on, which is why there is no `.nojekyll` file: the two generated
documents are Markdown, rendered through `_layouts/default.html`. A page without
front matter is copied through untouched, so the HTML pages never meet a
template unless they ask for one.

- `css/tokens.css` is the app's palette, type, spacing and radii, from
  `docs/design-system.md` and `IntensityPalette` in the app repository. Colour
  pairs are declared in the stylesheet as `/* @contrast --ink on --ground: text */`
  and measured in both schemes on every build.
- `img/icon/` and `favicon.ico` are downscales of the app icon, never redrawn.
- `img/badges/app-store-black.svg` is Apple's badge artwork, unmodified, from the
  App Store Marketing Tools page for this app. One badge per layout, at least
  40 px tall, clear space of a quarter of its height, per Apple's guidelines.
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
python3 scripts/contrast.py css/tokens.css
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
