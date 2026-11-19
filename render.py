"""Year activity card. Five Nothing modes."""

import json
from pathlib import Path

from frame import dots, label, open_svg
from nothing import MODES, theme

ROOT = Path(__file__).resolve().parent


def render(mode, data):
    colors = theme(mode)
    years = data["years"]
    peak = max(count for _, count in years) or 1
    name, _ = dots("ACTIVITY", 46, 22, colors["fg"], scale=2.2)
    parts = [
        open_svg(mode, 640, 280, "Contributions by year, including private counts"),
        name,
    ]
    for index, (year, count) in enumerate(years):
        x = 36 + index * 120
        bar = max(4, 120 * (count / peak))
        y = 210 - bar
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="36" height="{bar:.1f}" fill="{colors["figure"]}"/>')
        parts.append(label(x, 232, year, colors["muted"], 12, 0.4))
        parts.append(label(x, 252, f"{count:,}", colors["fg"], 12, 0.2))
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    data = json.loads((ROOT / "sample.json").read_text())
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    for mode in MODES:
        (out / f"{mode}.svg").write_text(render(mode, data))
        print(mode)


if __name__ == "__main__":
    main()
