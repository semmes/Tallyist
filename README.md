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

**`privacy-policy.md` and `support.md` in this repository are generated. Do not
edit them here.**

The app's source repository holds the canonical copies under `docs/`, because
the policy's claims are written to be checkable against the app's privacy
manifest and entitlements, and the support page's answers describe shipping
behaviour. Edits are made there. On merge, a workflow in that repository renders
these two files — the same bodies with the front matter above added — and pushes
them here. A separate check runs daily and fails if what is published here has
drifted from what the app repository says it should be, so a hand-edit here will
be reported rather than quietly kept.

The privacy policy additionally ships *inside* the app, so a policy change
touches three copies: `docs/privacy-policy.md` and `PrivacyPolicyView.swift` in
the app repository, and `privacy-policy.md` here. All three carry the same
"Last updated" date, and CI fails a change that lets the first two disagree.

## Questions

Questions about the app, or about these documents, belong in
[Issues](https://github.com/semmes/Tallyist/issues).
