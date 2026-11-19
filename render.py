"""Activity card. Rank on the left, the stat rows on the right. Wide adds the year bars."""

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


def render(mode, size, data):
    colors = theme(mode)
    if size == "mini":
        return _mini(mode, colors, data)
    if size == "wide":
        return _wide(mode, colors, data)
    if size == "regular":
        return _sheet(mode, colors, data, 495, 248, EXTRA)
    return _sheet(mode, colors, data, 495, 195, ROWS)


def _mark(x, y, colors, size=6):
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{colors["mark"]}"/>'


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
        label(16, 96, data["rank"], colors["figure"], 36, -1),
        label(16, 118, "Rank", colors["muted"], 11, 0.3),
        _stat(16, 148, "Stars", data["stars"], colors, 204),
        "</svg>",
    ])


def _sheet(mode, colors, data, width, height, rows):
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [
        open_svg(mode, width, height, f"{data['login']} activity"),
        name,
        label(20, height - 72, data["rank"], colors["figure"], 44, -1.2),
        label(20, height - 42, "Rank", colors["muted"], 12, 0.3),
    ]
    pitch = 22 if len(rows) <= 5 else 24
    for index, (key, title) in enumerate(rows):
        y = 70 + index * pitch
        parts.append(_stat(160, y, title, data[key], colors, width - 20))
    return "\n".join(parts + ["</svg>"])


def _wide(mode, colors, data):
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [
        open_svg(mode, 896, 292, f"{data['login']} activity"),
        name,
        label(876, 36, f"@{data['login']}", colors["muted"], 12, 0.2, anchor="end"),
        label(20, 128, data["rank"], colors["figure"], 48, -1.2),
        label(20, 156, "Rank", colors["muted"], 12, 0.3),
    ]
    for index, (key, title) in enumerate(EXTRA):
        column = index // 4
        row = index % 4
        x = 148 + column * 400
        y = 78 + row * 26
        parts.append(_stat(x, y, title, data[key], colors, x + 210))
    years = data["years"] or [["—", 0]]
    peak = max(count for _, count in years) or 1
    slot = 840 / len(years)
    baseline = 236
    for index, (year, count) in enumerate(years):
        x = 28 + index * slot
        bar = max(3, 48 * (count / peak))
        parts.append(
            f'<rect x="{x:.1f}" y="{baseline - bar:.1f}" width="28" height="{bar:.1f}" fill="{colors["figure"]}"/>'
        )
        parts.append(label(x, baseline + 16, year, colors["muted"], 11, 0.15))
        parts.append(label(x, baseline + 32, f"{count:,}", colors["fg"], 11, 0.1))
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
        "Mini is the rank. Compact and regular are the stat sheet. Wide adds the year bars.",
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
