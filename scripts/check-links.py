#!/usr/bin/env python3
"""Check the built site before it deploys.

    python3 scripts/check-links.py _site
    python3 scripts/check-links.py _site --external   # also fetch outbound links

Reads every .html file in the build and fails (exit 1) on:

- an internal link or resource that resolves to no file in the build;
- a #fragment that names no id on the page it points at;
- anything a page loads from another origin: a script, a stylesheet, an icon,
  an image, a frame, media. The site says it loads nothing from anyone else,
  and this is what keeps that true;
- any <script> at all, inline or not. The site has no JavaScript;
- an <img> without an alt attribute (alt="" is fine for decoration).

Links to other sites (<a href>) are allowed. With --external each one is
fetched once and must answer 2xx or 3xx, so a store link that 404s fails the
deploy rather than a visitor.

The site's own addresses count as internal wherever they appear, so a canonical
link or an og:image written as https://tallyist.co/... is checked against the
build too. The base path (the /Tallyist the site is served under before its
domain is attached) is read from _config.yml; --base overrides it.

Dependency-free, so the deploy workflow can run it without installing anything.
"""

import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

OWN_ORIGINS = ("https://tallyist.co", "https://www.tallyist.co",
               "http://tallyist.co", "http://www.tallyist.co")
GITHUB_IO = ("https://semmes.github.io", "http://semmes.github.io")

# Elements whose URL the browser fetches as part of drawing the page.
LOADS = {
    ("script", "src"), ("link", "href"), ("img", "src"), ("img", "srcset"),
    ("source", "src"), ("source", "srcset"), ("iframe", "src"),
    ("video", "src"), ("video", "poster"), ("audio", "src"),
    ("embed", "src"), ("object", "data"), ("track", "src"),
}
# <link> relations that are navigation rather than a fetch.
LINK_NAVIGATION = {"canonical", "alternate", "prev", "next", "author", "license"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []      # (kind, url, line): kind is "load" or "link"
        self.scripts = []   # line numbers
        self.no_alt = []    # (src, line)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        if tag == "script":
            self.scripts.append(line)
        if tag == "img" and "alt" not in a:
            self.no_alt.append((a.get("src", "?"), line))
        if tag == "a" and a.get("href"):
            self.refs.append(("link", a["href"], line))
        if tag == "meta" and a.get("property") in ("og:image", "og:url") and a.get("content"):
            kind = "load" if a["property"] == "og:image" else "link"
            self.refs.append((kind, a["content"], line))
        for (t, attr) in LOADS:
            if tag != t or not a.get(attr):
                continue
            if tag == "link":
                rels = set((a.get("rel") or "").lower().split())
                if rels & LINK_NAVIGATION:
                    self.refs.append(("link", a[attr], line))
                    continue
            if attr == "srcset":
                for part in a[attr].split(","):
                    if part.strip():
                        self.refs.append(("load", part.strip().split()[0], line))
            else:
                self.refs.append(("load", a[attr], line))


def read_base(root):
    try:
        text = open(os.path.join(root, "_config.yml"), encoding="utf-8").read()
    except OSError:
        return ""
    m = re.search(r"^baseurl:\s*[\"']?([^\"'\s#]*)", text, re.M)
    return (m.group(1) if m else "").rstrip("/")


def page_url(site, path, base):
    rel = os.path.relpath(path, site).replace(os.sep, "/")
    if rel == "index.html":
        return base + "/"
    if rel.endswith("/index.html"):
        return base + "/" + rel[: -len("index.html")]
    return base + "/" + rel


def target_file(site, url_path, base):
    """The build file a same-site path resolves to, or None."""
    if base and not (url_path == base or url_path.startswith(base + "/")):
        return None
    rel = urllib.parse.unquote(url_path[len(base):].lstrip("/"))
    candidate = os.path.join(site, rel)
    if url_path.endswith("/") or rel == "":
        candidate = os.path.join(candidate, "index.html")
    elif os.path.isdir(candidate):
        candidate = os.path.join(candidate, "index.html")
    return candidate if os.path.isfile(candidate) else None


def own_path(url, base):
    """The site path for an absolute URL on one of the site's own origins."""
    for origin in OWN_ORIGINS:
        if url == origin or url.startswith(origin + "/"):
            return base + (url[len(origin):] or "/")
    for origin in GITHUB_IO:
        prefix = origin + base
        if base and (url == prefix or url.startswith(prefix + "/")):
            return base + (url[len(prefix):] or "/")
    return None


def fetch_status(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tallyist-site-check"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # DNS, TLS, timeout: all mean a visitor cannot reach it
        return f"unreachable ({e.__class__.__name__})"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    site = args[0]
    external = "--external" in argv
    base = read_base(".")
    if "--base" in argv:
        i = argv.index("--base")
        base = argv[i + 1].rstrip("/") if i + 1 < len(argv) else ""

    pages = {}
    for dirpath, _, files in os.walk(site):
        for name in files:
            if name.endswith(".html"):
                path = os.path.join(dirpath, name)
                p = Page()
                p.feed(open(path, encoding="utf-8").read())
                pages[path] = p

    failures, outbound = [], {}
    for path, p in sorted(pages.items()):
        here = page_url(site, path, base)
        where = os.path.relpath(path, site)
        for line in p.scripts:
            failures.append(f"{where}:{line}: <script> (the site has no JavaScript)")
        for src, line in p.no_alt:
            failures.append(f"{where}:{line}: <img src=\"{src}\"> has no alt attribute")
        for kind, raw, line in p.refs:
            url = raw.strip()
            scheme = urllib.parse.urlsplit(url).scheme.lower()
            if scheme in ("mailto", "tel", "data"):
                continue
            if scheme == "javascript":
                failures.append(f"{where}:{line}: javascript: URL")
                continue
            if url.startswith("//"):
                url = "https:" + url
                scheme = "https"
            if scheme in ("http", "https"):
                path_on_site = own_path(url.split("#")[0], base)
                if path_on_site is None:
                    if kind == "load":
                        failures.append(f"{where}:{line}: loads {url} from another origin")
                    else:
                        outbound.setdefault(url.split("#")[0], []).append(f"{where}:{line}")
                    continue
                target_path, fragment = path_on_site, urllib.parse.urlsplit(url).fragment
            else:
                joined = urllib.parse.urljoin(here, url)
                parts = urllib.parse.urlsplit(joined)
                target_path, fragment = parts.path, parts.fragment
            if target_path == here.split("#")[0] and not url.split("#")[0]:
                target = path  # a bare #fragment on this page
            else:
                target = target_file(site, target_path, base)
            if target is None:
                outside = base and not (target_path == base or target_path.startswith(base + "/"))
                failures.append(f"{where}:{line}: {raw} "
                                + (f"is outside the site's base path {base}" if outside
                                   else "resolves to nothing in the build"))
                continue
            if fragment and target.endswith(".html") and fragment not in pages[target].ids:
                failures.append(f"{where}:{line}: {raw}: no id \"{fragment}\" on that page")

    if external:
        for url, places in sorted(outbound.items()):
            status = fetch_status(url)
            if not (isinstance(status, int) and 200 <= status < 400):
                failures.append(f"{url} answered {status} (linked from {', '.join(places)})")

    checked = sum(len(p.refs) for p in pages.values())
    if failures:
        print(f"{len(failures)} problem(s) in {len(pages)} page(s):\n")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"{len(pages)} page(s), {checked} reference(s)"
          + (f", {len(outbound)} outbound link(s) fetched" if external else "")
          + ": all resolve, nothing loads from another origin, no scripts.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
