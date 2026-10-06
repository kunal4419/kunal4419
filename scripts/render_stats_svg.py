#!/usr/bin/env python3
"""
Render the streak / stats card for kunal4419 from data/contributions.json.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "stats.svg")

BG = "#0d1117"
BG2 = "#111722"
TILE = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
GREEN = "#39d353"
BAR = "#26a641"

W, H = 840, 480
PAD = 20
TITLEBAR_H = 30
COLS, ROWS = 3, 2
GAP = 14
TILE_W = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
TILE_H = 130
TILES_TOP = TITLEBAR_H + PAD + 4
CHART_TOP = TILES_TOP + ROWS * TILE_H + (ROWS - 1) * GAP + GAP

TILE_STAGGER = 0.12
SLIDE_DUR = 0.4
COUNT_DUR = 1.0
FRAMES = 14


def short(d):
    if not d:
        return "—"
    return datetime.date.fromisoformat(d).strftime("%b %-d")


def span(s):
    return f'{short(s["start"])} – {short(s["end"])}' if s["length"] else "—"


if not os.path.exists(SRC):
    print(f"Data file not found at {SRC}", file=sys.stderr)
    sys.exit(0)

with open(SRC) as f:
    data = json.load(f)

cur, lng, best = data.get("current_streak", {}), data.get("longest_streak", {}), data.get("best_day", {})
n_days = len(data.get("days", [])) or 365

tiles = [
    ("current streak", cur.get("length", 0), " days", span(cur), GREEN),
    ("longest streak", lng.get("length", 0), " days", span(lng), INK),
    ("total contributions", data.get("total_contributions", 0), "", "in the last year", INK),
    ("active days", data.get("active_days", 0), f" / {n_days}", f'{data.get("active_days", 0) / n_days:.0%} of the year', INK),
    ("best day", best.get("count", 0), "", short(best.get("date")), INK),
    ("avg / active day", data.get("avg_per_active_day", 0), "", "contributions", INK),
]


def fmt(v, like):
    return f"{v:,.1f}" if isinstance(like, float) else f"{int(round(v)):,}"


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<style>'
    f'.t{{opacity:0;animation:in {SLIDE_DUR}s ease-out both}}'
    '@keyframes in{0%{opacity:0;transform:translateY(12px)}100%{opacity:1;transform:translateY(0)}}'
    '@media (prefers-reduced-motion: reduce){.t{opacity:1!important;transform:none!important;animation:none!important}}'
    '</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">kunal@github: ~$ ./stats.sh</text>')

for i, (label, value, suffix, caption, accent) in enumerate(tiles):
    col, row = i % COLS, i // COLS
    x = PAD + col * (TILE_W + GAP)
    y = TILES_TOP + row * (TILE_H + GAP)
    start = i * TILE_STAGGER
    count_start = start + SLIDE_DUR * 0.6

    parts.append(f'<g class="t" style="animation-delay:{start:.2f}s">')
    parts.append(f'<rect x="{x:.1f}" y="{y}" width="{TILE_W:.1f}" height="{TILE_H}" rx="10" '
                 f'fill="{TILE}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{x+18:.1f}" y="{y+32}" fill="{MUTED}" font-size="16">$ {label}</text>')

    num_y = y + 78
    for k in range(1, FRAMES + 1):
        p = k / FRAMES
        v = value * (1 - (1 - p) ** 3)
        t_on = count_start + COUNT_DUR * (k - 1) / FRAMES
        t_off = count_start + COUNT_DUR * k / FRAMES
        anim = f'<set attributeName="opacity" to="1" begin="{t_on:.3f}s"/>'
        if k < FRAMES:
            anim += f'<set attributeName="opacity" to="0" begin="{t_off:.3f}s"/>'
        parts.append(
            f'<text x="{x+18:.1f}" y="{num_y}" opacity="0" font-size="36" font-weight="700" fill="{accent}">'
            f'{fmt(v, value)}<tspan font-size="18" font-weight="400" fill="{MUTED}">{suffix}</tspan>'
            f'{anim}</text>'
        )
    parts.append(f'<text x="{x+18:.1f}" y="{y+108}" fill="{MUTED}" font-size="14">{caption}</text>')
    parts.append('</g>')

parts.append('</svg>')
svg = "".join(parts)
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT}: {W} x {H}")
