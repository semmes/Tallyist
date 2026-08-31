# Tallyist — public documents

This repository is the public home of the two documents Tallyist must publish
at a stable address: its **privacy policy** and its **support page**. They are
served as a site at **<https://semmes.github.io/Tallyist/>**, and those URLs are
the ones registered in App Store Connect.

It exists as a separate repository so that these documents stay publicly
readable — with their full revision history — independently of the app's source
repository. The privacy policy claims that every change to it is visible in a
public history; keeping that claim true is this repository's only job.

| Document | Source file | Published at |
| --- | --- | --- |
| Privacy Policy | `privacy-policy.md` | `/Tallyist/privacy/` |
| Support | `support.md` | `/Tallyist/support/` |

## Editing

The app's source repository holds the canonical copies under `docs/`, because
the policy's claims are written to be checkable against the app's privacy
manifest and entitlements, and the support page's answers describe shipping
behaviour. Changes are made there first and mirrored here; the two must not
drift, since one of them is what App Review and users actually read.

The privacy policy additionally ships *inside* the app, so a policy change
touches three copies: `docs/privacy-policy.md` and `PrivacyPolicyView.swift` in
the app repository, and `privacy-policy.md` here. All three carry the same
"Last updated" date.

## Questions

Questions about the app, or about these documents, belong in
[Issues](https://github.com/semmes/Tallyist/issues).
