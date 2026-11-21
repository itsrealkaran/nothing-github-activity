"use strict";

const { dots, label, openSvg } = require("./frame");
const { theme } = require("./nothing");
const { commas, fixed } = require("./format");

const ROWS = [
  ["stars", "Stars"],
  ["commits", "Commits"],
  ["pulls", "Pulls"],
  ["issues", "Issues"],
  ["contributed", "Contributed"],
];
const RANKS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"];

function render(mode, size, data, border = true) {
  const colors = theme(mode);
  if (size === "mini") return mini(mode, colors, data, border);
  if (size === "wide") return wide(mode, colors, data, border);
  if (size === "regular") return regular(mode, colors, data, border);
  return compact(mode, colors, data, border);
}

function mark(x, y, colors, size = 6) {
  return `<rect x="${x}" y="${y}" width="${size}" height="${size}" fill="${colors.mark}"/>`;
}

function ladder(x, y, rank, colors, cell = 8, gap = 4, across = true, labels = false) {
  const level = RANKS.includes(rank) ? RANKS.indexOf(rank) : RANKS.length - 1;
  const parts = [];
  const step = cell + gap;
  RANKS.forEach((name, index) => {
    const px = across ? x + index * step : x;
    const py = across ? y : y + index * step;
    let fill = colors.rule;
    if (index < level) fill = colors.figure;
    else if (index === level) fill = colors.mark;
    parts.push(`<rect x="${fixed(px, 1)}" y="${fixed(py, 1)}" width="${cell}" height="${cell}" fill="${fill}"/>`);
    if (labels) parts.push(label(px + cell / 2, py + cell + 13, name, colors.muted, 10, 0, "middle"));
  });
  return parts.join("\n");
}

function stat(x, y, title, value, colors, numberX) {
  return [
    mark(x, y - 10, colors),
    label(x + 14, y, title, colors.fg, 13, 0.15),
    label(numberX, y, commas(value), colors.figure, 13, 0.1, "end"),
  ].join("\n");
}

function mini(mode, colors, data, border) {
  const [name] = dots("ACTIVITY", 28, 12, colors.fg, 1.15);
  return [
    openSvg(mode, 220, 168, data.login + " activity", 6, 14, border),
    name,
    label(16, 88, data.rank, colors.figure, 32, -1),
    label(16, 108, "Rank", colors.muted, 11, 0.3),
    ladder(16, 122, data.rank, colors, 12, 6),
    stat(16, 156, "Stars", data.stars, colors, 204),
    "</svg>",
  ].join("\n");
}

function share(rank) {
  if (!RANKS.includes(rank)) return 0;
  return (RANKS.length - RANKS.indexOf(rank)) / RANKS.length;
}

function endDot(cx, cy, radius, angle, fill, stroke) {
  const x = cx + radius * Math.cos(angle);
  const y = cy + radius * Math.sin(angle);
  return `<circle cx="${fixed(x, 2)}" cy="${fixed(y, 2)}" r="${stroke + 2}" fill="${fill}"/>`;
}

function dotFill(mode, colors) {
  return mode.endsWith("-r") ? colors.mark : colors.figure;
}

function ring(cx, cy, radius, rank, colors, dot, stroke = 3) {
  const ink = colors.figure;
  const parts = [
    `<circle cx="${fixed(cx, 1)}" cy="${fixed(cy, 1)}" r="${radius}" fill="none" ` +
    `stroke="${colors.rule}" stroke-width="${stroke}"/>`,
  ];
  const portion = share(rank);
  const start = -Math.PI / 2;
  if (portion >= 1) {
    parts.push(
      `<circle cx="${fixed(cx, 1)}" cy="${fixed(cy, 1)}" r="${radius}" fill="none" ` +
      `stroke="${ink}" stroke-width="${stroke}"/>`
    );
    parts.push(endDot(cx, cy, radius, start, dot, stroke));
  } else if (portion > 0) {
    const end = start + 2 * Math.PI * portion;
    const x1 = cx + radius * Math.cos(start);
    const y1 = cy + radius * Math.sin(start);
    const x2 = cx + radius * Math.cos(end);
    const y2 = cy + radius * Math.sin(end);
    const large = portion > 0.5 ? 1 : 0;
    parts.push(
      `<path d="M ${fixed(x1, 2)} ${fixed(y1, 2)} A ${radius} ${radius} 0 ${large} 1 ${fixed(x2, 2)} ${fixed(y2, 2)}" ` +
      `fill="none" stroke="${ink}" stroke-width="${stroke}"/>`
    );
    parts.push(endDot(cx, cy, radius, end, dot, stroke));
  }
  return parts.join("");
}

function compact(mode, colors, data, border) {
  const width = 495;
  const height = 212;
  const [name] = dots("ACTIVITY", 40, 16, colors.fg, 1.8);
  const cy = 118;
  const parts = [
    openSvg(mode, width, height, data.login + " activity", 8, 20, border),
    name,
    ring(86, cy, 36, data.rank, colors, dotFill(mode, colors)),
    label(86, cy + 8, data.rank, colors.figure, 26, -0.8, "middle"),
  ];
  ROWS.forEach(([key, title], index) => {
    parts.push(stat(168, 72 + index * 22, title, data[key], colors, width - 20));
  });
  parts.push("</svg>");
  return parts.join("\n");
}

function regular(mode, colors, data, border) {
  const width = 408;
  const [name] = dots("ACTIVITY", 40, 16, colors.fg, 1.8);
  const cy = 118;
  const parts = [
    openSvg(mode, width, 212, data.login + " activity", 8, 20, border),
    name,
    ring(86, cy, 36, data.rank, colors, dotFill(mode, colors)),
    label(86, cy + 8, data.rank, colors.figure, 26, -0.8, "middle"),
  ];
  const columns = [ROWS.slice(0, 3), ROWS.slice(3)];
  const left = 136;
  const right = width - 20;
  const gap = 10;
  const span = (right - left - gap) / 2;
  const xs = [left, left + span + gap];
  const numbers = [left + span, right];
  const ys = [86, 118, 150];
  columns.forEach((rows, column) => {
    rows.forEach(([key, title], row) => {
      parts.push(stat(xs[column], ys[row], title, data[key], colors, numbers[column]));
    });
  });
  parts.push("</svg>");
  return parts.join("\n");
}

function wide(mode, colors, data, border) {
  const [name] = dots("ACTIVITY", 40, 16, colors.fg, 1.8);
  const parts = [
    openSvg(mode, 896, 220, data.login + " activity", 8, 20, border),
    name,
    label(876, 36, "@" + data.login, colors.muted, 12, 0.2, "end"),
    ring(100, 124, 46, data.rank, colors, dotFill(mode, colors), 4),
    label(100, 132, data.rank, colors.figure, 28, -0.8, "middle"),
  ];
  const columns = [ROWS.slice(0, 3), ROWS.slice(3)];
  const xs = [300, 600];
  const ys = [88, 124, 160];
  columns.forEach((rows, column) => {
    rows.forEach(([key, title], row) => {
      const x = xs[column];
      parts.push(stat(x, ys[row], title, data[key], colors, x + 180));
    });
  });
  parts.push("</svg>");
  return parts.join("\n");
}

module.exports = { render };
