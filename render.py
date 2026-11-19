"""Activity card. Mini keeps the glyph. The other sizes put the rank in a ring."""

import math
import sys
from pathlib import Path

from frame import dots, label, open_svg
from github_user import activity
from nothing import MODES, SIZES, theme

ROOT = Path(__file__).resolve().parent

ROWS = (
    ("stars", "Stars"),
    ("commits", "Commits"),
    ("pulls", "Pulls"),
    ("issues", "Issues"),
    ("contributed", "Contributed"),
)
RANKS = ("S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C")


def render(mode, size, data):
    colors = theme(mode)
    if size == "mini":
        return _mini(mode, colors, data)
    if size == "wide":
        return _wide(mode, colors, data)
    if size == "regular":
        return _regular(mode, colors, data)
    return _compact(mode, colors, data)


def _mark(x, y, colors, size=6):
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{colors["mark"]}"/>'


def _ladder(x, y, rank, colors, cell=8, gap=4, across=True, labels=False):
    """Nine equal squares. Lit from S through the current rank. Not a value chart."""
    level = RANKS.index(rank) if rank in RANKS else len(RANKS) - 1
    parts = []
    step = cell + gap
    for index, name in enumerate(RANKS):
        px = x + index * step if across else x
        py = y if across else y + index * step
        if index < level:
            fill = colors["figure"]
        elif index == level:
            fill = colors["mark"]
        else:
            fill = colors["rule"]
        parts.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{cell}" height="{cell}" fill="{fill}"/>')
        if labels:
            parts.append(label(px + cell / 2, py + cell + 13, name, colors["muted"], 10, 0, anchor="middle"))
    return "\n".join(parts)


def _stat(x, y, title, value, colors, number_x):
    return "\n".join([
        _mark(x, y - 10, colors),
        label(x + 14, y, title, colors["fg"], 13, 0.15),
        label(number_x, y, f"{value:,}", colors["figure"], 13, 0.1, anchor="end"),
    ])


def _mini(mode, colors, data):
    name, _ = dots("ACTIVITY", 28, 12, colors["fg"], scale=1.15)
    return "\n".join([
        open_svg(mode, 220, 168, f"{data['login']} activity", mark=6, margin=14),
        name,
        label(16, 88, data["rank"], colors["figure"], 32, -1),
        label(16, 108, "Rank", colors["muted"], 11, 0.3),
        _ladder(16, 122, data["rank"], colors, cell=12, gap=6),
        _stat(16, 156, "Stars", data["stars"], colors, 204),
        "</svg>",
    ])


def _share(rank):
    """How full the ring is. S closes it. C is the first step."""
    if rank not in RANKS:
        return 0
    return (len(RANKS) - RANKS.index(rank)) / len(RANKS)


def _end_dot(cx, cy, radius, angle, fill, stroke):
    """A dot on the ring, at the end of the arc."""
    x = cx + radius * math.cos(angle)
    y = cy + radius * math.sin(angle)
    return (
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{stroke + 2}" fill="{fill}"/>'
    )


def _dot_fill(mode, colors):
    """The arc stays white or black. Only classic-r and white-r turn the end dot red."""
    if mode.endswith("-r"):
        return colors["mark"]
    return colors["figure"]


def _ring(cx, cy, radius, rank, colors, dot, stroke=3):
    """A track, then an arc for the rank. A dot marks the end. The rank sits in the middle."""
    ink = colors["figure"]
    parts = [
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius}" fill="none" '
        f'stroke="{colors["rule"]}" stroke-width="{stroke}"/>'
    ]
    share = _share(rank)
    start = -math.pi / 2
    if share >= 1:
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius}" fill="none" '
            f'stroke="{ink}" stroke-width="{stroke}"/>'
        )
        parts.append(_end_dot(cx, cy, radius, start, dot, stroke))
    elif share > 0:
        end = start + 2 * math.pi * share
        x1 = cx + radius * math.cos(start)
        y1 = cy + radius * math.sin(start)
        x2 = cx + radius * math.cos(end)
        y2 = cy + radius * math.sin(end)
        large = 1 if share > 0.5 else 0
        parts.append(
            f'<path d="M {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f}" '
            f'fill="none" stroke="{ink}" stroke-width="{stroke}"/>'
        )
        parts.append(_end_dot(cx, cy, radius, end, dot, stroke))
    return "".join(parts)


def _compact(mode, colors, data):
    width, height = 495, 212
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    cy = 118
    parts = [
        open_svg(mode, width, height, f"{data['login']} activity"),
        name,
        _ring(86, cy, 36, data["rank"], colors, _dot_fill(mode, colors)),
        label(86, cy + 8, data["rank"], colors["figure"], 26, -0.8, anchor="middle"),
    ]
    for index, (key, title) in enumerate(ROWS):
        parts.append(_stat(168, 72 + index * 22, title, data[key], colors, width - 20))
    return "\n".join(parts + ["</svg>"])


def _regular(mode, colors, data):
    """Same five counts as compact, split into two columns."""
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    cy = 118
    parts = [
        open_svg(mode, 495, 212, f"{data['login']} activity"),
        name,
        _ring(86, cy, 36, data["rank"], colors, _dot_fill(mode, colors)),
        label(86, cy + 8, data["rank"], colors["figure"], 26, -0.8, anchor="middle"),
    ]
    columns = (ROWS[:3], ROWS[3:])
    xs = (168, 340)
    numbers = (322, 475)
    ys = (86, 118, 150)
    for column, rows in enumerate(columns):
        for row, (key, title) in enumerate(rows):
            parts.append(_stat(xs[column], ys[row], title, data[key], colors, numbers[column]))
    return "\n".join(parts + ["</svg>"])


def _wide(mode, colors, data):
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [
        open_svg(mode, 896, 220, f"{data['login']} activity"),
        name,
        label(876, 36, f"@{data['login']}", colors["muted"], 12, 0.2, anchor="end"),
        _ring(100, 124, 46, data["rank"], colors, _dot_fill(mode, colors), stroke=4),
        label(100, 132, data["rank"], colors["figure"], 28, -0.8, anchor="middle"),
    ]
    columns = (ROWS[:3], ROWS[3:])
    xs = (300, 600)
    ys = (88, 124, 160)
    for column, rows in enumerate(columns):
        for row, (key, title) in enumerate(rows):
            x = xs[column]
            parts.append(_stat(x, ys[row], title, data[key], colors, x + 180))
    return "\n".join(parts + ["</svg>"])


def _variant(card, login, mode, size, filename):
    url = f"https://github.com/itsrealkaran/nothing-github-activity?username={login}&theme={mode}&size={size}"
    return [
        f"**{card}** · {mode} · {size}",
        "",
        f"`{url}`",
        "",
        f"![{card} {mode} {size}](dist/{login}/{filename})",
        "",
    ]


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "itsrealkaran"
    data = activity(login)
    out = ROOT / "dist" / data["login"]
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {login}",
        "",
        "Mini keeps the glyph of nine squares. Compact, regular, and wide put the rank inside a ring. The arc stays white or black. On classic-r and white-r the end dot is red. S closes the ring.",
        "",
    ]
    for mode in MODES:
        lines += [f"## {mode}", ""]
        for size in SIZES:
            filename = f"{mode}-{size}.svg"
            (out / filename).write_text(render(mode, size, data))
            lines += _variant("activity", data["login"], mode, size, filename)
            print(data["login"], mode, size)
    (ROOT / "DUMMY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
