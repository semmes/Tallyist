#!/usr/bin/env python3
"""Measure the contrast pairs a stylesheet declares, in both colour schemes.

    python3 contrast.py css/site.css          # prints a Markdown table
    python3 contrast.py css/site.css --quiet  # exit status only (1 on a failure)

Dependency-free, so it can run in the site's deploy workflow unchanged.

A pair is declared next to the tokens it measures, as a CSS comment:

    /* @contrast --ink on --ground: text */
    /* @contrast --accent on --ground-grouped: text */
    /* @contrast --band-high on --ground: ui */
    /* @contrast --ink-secondary on --surface over --ground-grouped: text */

`text` is 4.5:1 (WCAG 1.4.3, normal text), `large` is 3:1 (large text),
`ui` is 3:1 (WCAG 1.4.11, graphics and the parts of a control), and a bare
number sets its own floor. Each pair is measured twice: once with the light
values (every `:root` block outside a media query) and once with those
overridden by the dark block (`@media (prefers-color-scheme: dark)`).

Translucent colours are composited before measuring, the way a browser draws
them: the background over `over` (default `--ground`), then the foreground over
that result. This is what makes an rgba() secondary ink measurable at all.
"""

import re
import sys

NAMED = {"white": (255, 255, 255, 1.0), "black": (0, 0, 0, 1.0),
         "transparent": (0, 0, 0, 0.0)}
KINDS = {"text": 4.5, "large": 3.0, "ui": 3.0}


def parse_color(value):
    v = value.strip().lower()
    if v in NAMED:
        return NAMED[v]
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            raise ValueError(f"bad hex colour: {value}")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return (r, g, b, a)
    m = re.fullmatch(r"rgba?\((.*)\)", v)
    if m:
        parts = re.split(r"[\s,/]+", m.group(1).strip())
        parts = [p for p in parts if p]
        if len(parts) not in (3, 4):
            raise ValueError(f"bad rgb() colour: {value}")

        def channel(p):
            return round(float(p[:-1]) * 2.55) if p.endswith("%") else float(p)

        r, g, b = (channel(p) for p in parts[:3])
        a = 1.0
        if len(parts) == 4:
            p = parts[3]
            a = float(p[:-1]) / 100 if p.endswith("%") else float(p)
        return (r, g, b, a)
    raise ValueError(f"unsupported colour: {value}")


def over(fg, bg):
    """Composite fg over an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def luminance(c):
    def lin(x):
        x /= 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexify(c):
    return "#" + "".join(f"{round(x):02x}" for x in c[:3])


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def blocks(css):
    """(light, dark) dicts of custom properties.

    Light is every :root block outside a media query. Dark is the :root blocks
    inside `@media (prefers-color-scheme: dark)`. Any other media query is
    conditional on something this script cannot know, so it is set aside.
    """
    body = strip_comments(css)
    dark, rest, i = {}, [], 0
    for m in re.finditer(r"@media[^{]*\{", body):
        if m.start() < i:
            continue  # nested inside a block already consumed
        depth, j = 1, m.end()
        while depth and j < len(body):
            depth += {"{": 1, "}": -1}.get(body[j], 0)
            j += 1
        if re.search(r"prefers-color-scheme\s*:\s*dark", m.group(0)):
            dark.update(props(body[m.end():j - 1]))
        rest.append(body[i:m.start()])
        i = j
    rest.append(body[i:])
    return props("".join(rest)), dark


def props(css):
    out = {}
    for sel in re.finditer(r":root[^{]*\{([^}]*)\}", css):
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);?", sel.group(1)):
            out[name] = value.strip()
    return out


def resolve(name, table, seen=()):
    if name in seen:
        raise ValueError(f"var() cycle through {name}")
    if name not in table:
        raise KeyError(name)
    value = table[name]
    m = re.fullmatch(r"var\((--[\w-]+)\)", value)
    return resolve(m.group(1), table, seen + (name,)) if m else value


PAIR = re.compile(
    r"@contrast\s+(--[\w-]+)\s+on\s+(--[\w-]+)(?:\s+over\s+(--[\w-]+))?\s*:\s*([\w.]+)")


def measure(fg, bg, base, table, page):
    """Composite bg over its base (only matters when bg is translucent), then
    fg over bg. `page` is the scheme's own page colour when no --ground is
    declared: white in light, black in dark."""
    b = parse_color(resolve(bg, table))
    if b[3] < 1:
        g = parse_color(resolve(base, table)) if base in table else page
        b = over(b, over(g, page))
    f = over(parse_color(resolve(fg, table)), b)
    return ratio(f, b), hexify(f), hexify(b)


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    css = open(argv[1], encoding="utf-8").read()
    quiet = "--quiet" in argv
    light, dark_only = blocks(css)
    dark = {**light, **dark_only}
    pairs = PAIR.findall(css)
    if not pairs:
        print("no @contrast pairs declared", file=sys.stderr)
        return 2
    failures = 0
    rows = ["| Pair | Needs | Light | Dark |", "|---|---|---|---|"]
    for fg, bg, base, kind in pairs:
        need = KINDS.get(kind) or float(kind)
        cells = []
        for table, page in ((light, NAMED["white"]), (dark, NAMED["black"])):
            try:
                r, f, b = measure(fg, bg, base or "--ground", table, page)
            except KeyError as e:
                print(f"{fg} on {bg}: {e.args[0]} is not declared", file=sys.stderr)
                return 2
            ok = r + 1e-9 >= need
            failures += not ok
            cells.append(f"{r:.2f}:1 {'' if ok else '**FAIL** '}({f} on {b})")
        label = f"`{fg}` on `{bg}`" + (f" over `{base}`" if base else "")
        rows.append(f"| {label} | {need:g}:1 {kind if kind in KINDS else ''} | {cells[0]} | {cells[1]} |")
    if not quiet:
        print("\n".join(rows))
        print(f"\n{len(pairs)} pairs, {failures} failing measurement(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
