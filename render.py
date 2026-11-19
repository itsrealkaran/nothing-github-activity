"""Year activity card for any GitHub username."""

import sys
from pathlib import Path

from frame import dots, label, open_svg
from github_user import activity
from nothing import MODES, SCALE, SIZES, theme

ROOT = Path(__file__).resolve().parent


def render(mode, size, data):
    scale = SCALE[size]
    colors = theme(mode)
    years = data["years"] or [["None", 0]]
    peak = max(count for _, count in years) or 1
    width = int(max(640, 48 + len(years) * 78) * scale)
    height = int(280 * scale)

    def n(value):
        return round(value * scale, 1)

    name, _ = dots("ACTIVITY", n(46), n(22), colors["fg"], scale=2.2 * scale)
    parts = [open_svg(mode, width, height, f"{data['login']} activity"), name]
    slot = (width - n(56)) / len(years)
    for index, (year, count) in enumerate(years):
        x = n(28) + index * slot
        bar = max(n(4), n(120) * (count / peak))
        y = n(200) - bar
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{n(28)}" height="{bar:.1f}" fill="{colors["figure"]}"/>')
        parts.append(label(x, n(224), year, colors["muted"], n(12), 0.3))
        parts.append(label(x, n(246), f"{count:,}", colors["fg"], n(12), 0.2))
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "itsrealkaran"
    data = activity(login)
    out = ROOT / "dist" / data["login"]
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"# {data['login']}", "", "Username, mode, and size.", ""]
    for mode in MODES:
        lines += [f"## {mode}", ""]
        for size in SIZES:
            filename = f"{mode}-{size}.svg"
            (out / filename).write_text(render(mode, size, data))
            lines += [f"### {size}", "", f"![{mode} {size}](dist/{data['login']}/{filename})", ""]
            print(data["login"], mode, size)
    (ROOT / "DUMMY.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
