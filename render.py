"""Activity card. Rank on the left, stat rows on the right. A glyph shows the rank."""

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
EXTRA = ROWS + (
    ("reviews", "Reviews"),
    ("followers", "Followers"),
)
RANKS = ("S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C")


def render(mode, size, data):
    colors = theme(mode)
    if size == "mini":
        return _mini(mode, colors, data)
    if size == "wide":
        return _wide(mode, colors, data)
    if size == "regular":
        return _sheet(mode, colors, data, EXTRA)
    return _sheet(mode, colors, data, ROWS)


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


def _sheet(mode, colors, data, rows):
    tall = len(rows) > 5
    width, height = 495, 248 if tall else 212
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [
        open_svg(mode, width, height, f"{data['login']} activity"),
        name,
        label(20, 118 if tall else 108, data["rank"], colors["figure"], 44, -1.2),
        label(20, 146 if tall else 134, "Rank", colors["muted"], 12, 0.3),
        _ladder(108, 78, data["rank"], colors, cell=8, gap=6, across=False),
    ]
    pitch = 22
    for index, (key, title) in enumerate(rows):
        y = 72 + index * pitch
        parts.append(_stat(156, y, title, data[key], colors, width - 20))
    return "\n".join(parts + ["</svg>"])


def _wide(mode, colors, data):
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [
        open_svg(mode, 896, 220, f"{data['login']} activity"),
        name,
        label(876, 36, f"@{data['login']}", colors["muted"], 12, 0.2, anchor="end"),
        label(20, 108, data["rank"], colors["figure"], 48, -1.2),
        label(20, 136, "Rank", colors["muted"], 12, 0.3),
        _ladder(20, 158, data["rank"], colors, cell=16, gap=10, labels=True),
    ]
    for index, (key, title) in enumerate(EXTRA):
        column = index // 4
        row = index % 4
        x = 300 + column * 300
        y = 78 + row * 28
        parts.append(_stat(x, y, title, data[key], colors, x + 180))
    return "\n".join(parts + ["</svg>"])


def _variant(card, login, mode, size, filename):
    url = f"https://github.com/itsrealkaran/{card}?username={login}&theme={mode}&size={size}"
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
        "The rank sits on the left with a glyph of nine equal squares. The stat rows sit on the right.",
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
