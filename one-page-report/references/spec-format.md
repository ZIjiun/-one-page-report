# Report spec format (JSON)

Write one spec per language. Copy an example from `examples/` and change it.

```json
{
  "lang": "zh-Hant",               // or "en"
  "report_type": "results",        // results | progress | proposal | postmortem | comparison | custom
  "style": "handdrawn",            // default style; --style overrides
  "theme": "light",                // light | dark; --theme overrides
  "doc_title": "file title",
  "meta": {
    "kicker": "small line above the title",
    "as_of": "資料統計至 2026/10 中",
    "version": "v1", "author": "name",
    "confidential": "內部使用",      // optional, shown in red in the footer
    "sources": "sources and estimate notes",
    "image_credit": "圖片：… © …（only when images are used）"
  },
  "title": "one-sentence conclusion\nsecond line",
  "layout": {"columns": "2fr 1fr", "areas": ["a b", "c d", "e e"]},
  "hero": {"src": "img/keyart.jpg", "mode": "side", "dark": {"src": "img/keyart-night.jpg"}},   // optional; "dark": per-theme override or null; see references/imagery.md
  "logo": {"src": "img/logo.png", "src_dark": "img/logo-white.png", "h": 104},
  "backdrop": {"src": "img/bg.jpg", "opacity": 0.3},
  "derived": [{"value": "−60%", "formula": "(2.6-6.5)/6.5*100", "from": ["6.5", "2.6"]}],   // every worked-out number; review.py recomputes it
  "zones": [ { "id": "a", "color": "blue", "icon": "trophy", "label": "成果",
               "question": "這次更新值得嗎？", "lead": "結論：…", "blocks": [ ... ] } ]
}
```

Zone colours: `blue` (main message), `red` (problems), `gray` (details), `green` (next / ask),
`orange` (timeline), `purple`, `teal`.

## Text markup (any text field)

`**bold**`, `==good (green)==`, `!!bad (red)!!`, `^^marker highlight^^`, `++up arrow green++`,
`{{icon:name}}`, `\n` for a line break. No HTML.

## Blocks

| type | fields (**bold** = required) |
|---|---|
| `cards` | **`items`**: `[{icon, tag, title, big, big_note, chart, diagram, photo, sub, foot}]`, optional `cols`. `diagram` = any diagram block; `photo` = `{src, position, caption}` (fills the card bottom) |
| diagrams | `route`, `formula`, `progress`, `gauge`, `compare`, `decision`, `transform`, `flowsteps`, `photo`, `speclines` — fields in `references/diagrams.md` |
| `chart` | **`kind`** bar/column/line (column: `icon` per bar, `top_note`), **`data`**: `[{label, value, display, highlight}]`, `title`, `note`, `caption`; line: `reference {value,label}`, `y_min`, `y_max` |
| `issues` | **`items`**: `[{problem, icon, detail, fix}]` (`fix` optional but strongly recommended), `title` |
| `chips` | **`rows`**: `[{label, icon, items: ["*key item", "item"]}]`, `title`, `note` |
| `table` | key/value: **`rows`**: `[{key, value, icon}]`; grid: **`header`**, **`rows`**: `[[...]]`, `recommend`: column index; cells may start with `ok`, `no`, `warn` |
| `steps` | **`items`**: `[{title, sub, owner, due}]` — `owner` and `due` show as a small tag; use them for every action |
| `note` | **`text`**, `icon` |
| `timeline` | **`events`**: `[{date, label, sub, icon, status, highlight}]`; `status`: `done` (✓ solid line), `doing` (… amber), `plan` (○ dashed). The line is solid up to the last `done` event |
| `status` | **`items`**: `[{state, name, note}]`; `state`: `good` 正常 / On track, `warning` 注意 / Watch, `serious` 落後 / Behind, `critical` 嚴重 / Critical. Override the words with `labels: {"good": "已達標"}` |
| `stat` | **`value`**, **`label`**, `unit`, `compare` — one standalone number |
| `text` | **`md`**: lines; `- ` starts a bullet |
| `columns` | **`children`**: `[[blocks], [blocks]]`, `cols` "1fr 1fr" |

**`cards` or `stat`?** Use `cards` for 2–4 parallel claims, each with its evidence (the usual
case). Use `stat` for one headline number on its own, e.g. in a narrow side zone.

**Lead length.** A zone `lead` is one line; past about 22 Chinese characters or 60 English
characters it is cut with "…". Keep it short; put detail in the zone.

## Translating numbers and units (zh → en)

- 萬 → K or M: 12.1 萬 = 121K; 830 萬 = 8.3M; 1,200 萬 = 12M. 億 → 100M units (3.5 億 = 350M).
- Money: keep the currency the material uses. If it does not say, write the number without a
  symbol in both versions and state the currency once in the footer (e.g. "Amounts in NT$").
- Dates: keep `10/27`-style dates identical in both versions so review.py can compare them.
- Months as words ("Early Oct", 10 月初) are fine; review.py ignores them.
- review.py converts 萬/億/K/M/B before comparing, so 830 萬 and 8.3M match.

A chart inside a card: put the chart object in the card's `chart` field.
