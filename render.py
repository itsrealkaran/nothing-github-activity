"""Activity card. Compact is this year. Regular is a fitted bar row. Wide gives the bars room."""

import sys
from pathlib import Path

from frame import dots, label, open_svg
from github_user import activity
from nothing import MODES, SIZES, theme

ROOT = Path(__file__).resolve().parent


def render(mode, size, data):
    colors = theme(mode)
    if size == "mini":
        return _mini(mode, colors, data)
    if size == "compact":
        return _compact(mode, colors, data)
    if size == "wide":
        return _bars(mode, colors, data, 896, 240, 140)
    return _bars(mode, colors, data, 495, 210, 100)


def _mini(mode, colors, data):
    year, count = data["years"][-1]
    name, _ = dots("ACTIVITY", 28, 12, colors["fg"], scale=1.15)
    return "\n".join([
        open_svg(mode, 220, 148, f"{data['login']} activity", mark=6, margin=14),
        name,
        label(16, 108, f"{count:,}", colors["figure"], 28, -0.8),
        label(16, 130, year, colors["muted"], 12, 0.2),
        "</svg>",
    ])


def _compact(mode, colors, data):
    year, count = data["years"][-1]
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    return "\n".join([
        open_svg(mode, 495, 132, f"{data['login']} activity"),
        name,
        label(20, 108, f"{count:,}", colors["figure"], 36, -1),
        label(250, 92, year, colors["fg"], 20, 0.2),
        label(250, 114, f"@{data['login']}", colors["muted"], 13, 0.3),
        "</svg>",
    ])


def _bars(mode, colors, data, width, height, bar_max):
    years = data["years"] or [["—", 0]]
    peak = max(count for _, count in years) or 1
    name, _ = dots("ACTIVITY", 40, 16, colors["fg"], scale=1.8)
    parts = [open_svg(mode, width, height, f"{data['login']} activity"), name]
    slot = (width - 40) / len(years)
    baseline = height - 52
    for index, (year, count) in enumerate(years):
        x = 20 + index * slot
        bar = max(4, bar_max * (count / peak))
        parts.append(f'<rect x="{x:.1f}" y="{baseline - bar:.1f}" width="18" height="{bar:.1f}" fill="{colors["figure"]}"/>')
        parts.append(label(x, baseline + 18, year, colors["muted"], 11, 0.2))
        parts.append(label(x, baseline + 34, f"{count:,}", colors["fg"], 11, 0.1))
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
    lines = [f"# {login}", "", "Compact is this year. Regular and wide are bar widgets at GitHub widths.", ""]
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
