# Diagrams: let the picture carry the logic

A zone is understood fastest when its main element is a picture of the relationship, with text
as support. Before filling a zone, name the **shape of its information**, then pick the block.
If the text in a zone describes a flow, a choice, a route, a calculation or a before/after,
draw it instead of writing it.

## Shape of the information → block

| The zone says… | Shape | Block | Not this |
|---|---|---|---|
| "from A to B and back, X km, battery left" | route / distance | `route` | a big number with a sentence |
| "75.5 kWh × 7 = ≈530" | calculation | `formula` | a sentence with the arithmetic |
| "115 of 125 stations; 5 min → 120 km" | progress to a target | `progress` | a big number alone |
| "score 94 / 100, ranked first" | one score + a badge | `gauge` | a big number alone |
| "which of the 3 to pick" | options from one question | `compare` | a spec table (keep a table only for 4+ criteria) |
| "can you charge at home? yes → … no → …" | yes/no decision | `decision` | a bullet list of conditions |
| "65M owners keep their mods → 450+ mods ready" | before → after | `transform` | two big numbers side by side |
| "do these four things" | ordered steps | `flowsteps` (or `steps`) | a paragraph |
| numbers across items / time / parts | comparison | `chart` (bar / column / line) | a table of numbers |
| dates and milestones | sequence in time | `timeline` | a list of dates |
| what a real thing looks like (product, screen, place) | appearance | `photo` (user-provided) | a hand-drawn imitation |
| "2.6 h, ▼ from 6.5, falling for 8 weeks" | one headline number + trend | `stattile` | a number with no comparison |
| "2.6 h against a 3 h target (was 6.5)" | actual vs target per KPI | `bullet` | a gauge per KPI, a sentence |
| "4 metrics, each before → after" | before → after per item | `dumbbell` | two tables, two bars per item |
| "satisfaction 3.6 → 4.3; Email rose most" | two points in time, 1–6 items | `slope` | a grouped column chart |
| "6.5 h → 2.6 h: AI −2.4, routing −1.0, volume +0.3" | contributions to a change | `waterfall` | a list of reasons with numbers |
| "+14 / +10 / −8 pt against target" | gap to target / plan / last year | `variance` | a table with ± numbers |
| "46% AI-drafted, 54% manual" | parts of a whole | `stacked` (100% or absolute) | a pie with many slices |
| "Monday morning is the peak" | two dimensions crossed | `heatmap` | a long table of numbers |
| 2–4 parallel claims, each with evidence | parallel points | `cards` with `chart` / `diagram` / `photo` inside | identical text cards |

## Reports about improvement (the common case)

"What did we do, what did we get, how much better?" — a zone set that works:

| Reader's question | Block |
|---|---|
| Did we hit the targets? | `bullet` (one row per KPI: actual, target, before) |
| How much better is each metric? | `dumbbell`, or `slope` when the point is one item rising above the others |
| What caused the change? | `waterfall` (start → each action's contribution → end) |
| Where are we still short? | `variance` against target; `heatmap` for where/when the problem sits |
| How did the work shift? | `stacked` 100% bars before / during / after |
| The one number to remember | `stattile` with its trend |

Comparison notation follows the IBCS reporting standard in spirit: actual = solid highlight,
target = a thick line, before / previous = a hollow mark; better = green and to the right,
worse = red and to the left, regardless of whether "better" means higher or lower
(`higher_is_better: false` for times, costs, error rates).

One zone, one main picture. A second element is fine when it is a different shape
(e.g. a `decision` followed by `issues`).

## Rules

- **Pictures carry the logic; text supports.** Each diagram answers the zone's lead. Labels sit
  on the diagram, next to what they explain.
- **Every icon still has a word** (a picture of a house means nothing until it says "home charging").
- **No decoration.** No mascots, stars, hearts, glow or 3D for effect. Theme imagery is the only
  exception and has its own rules (`references/imagery.md`).
- **The 4-size scale holds inside diagrams.** 46 for the one big number, 18 for headings and key
  values, 14 for everything else. Emphasis comes from weight and colour.
- **Colour roles hold inside diagrams.** Highlight blue = the thing to look at; grey = context;
  red = problem only; green = done / yes; amber = in progress / watch. The `decision` block uses
  green for yes and orange for the path that needs care.
- **Short values.** A formula tile fits about 6 characters at 18 px; a route value about 8 at 46 px.
  Longer values shrink to the next size, then get an ellipsis. Write `≈530`, not `大約 530 元左右`.
- **Draw from real numbers only.** No invented data to make a diagram look full.

## Block reference (fields in **bold** are required)

| type | fields |
|---|---|
| `route` | **`from`**, **`to`**, **`value`**, `unit`, `round_trip` (default true), `icon` (default car), `start` `{pct, label}`, `end` `{pct, label}`, `bars` `[{label, value, display, highlight}]` |
| `formula` | **`terms`** `[{icon, value, label}]`, `ops` `["×", "÷"…]`, **`result`** `{icon, value, label}`, `aside` `{icon, text}`, `scale` `{title, min, max, points:[{value, label, kind: good / hi / bad}]}` |
| `progress` | **`current`**, `target`, `current_label`, `current_display`, `unit`, `target_label`, `sub`, `then` `{from_icon, from_label, to_icon, prefix, value, unit, sub}` |
| `gauge` | **`value`**, `max` (100), `display`, `label`, `badge` `{icon, title, sub}` |
| `compare` | **`options`** `[{name, price, why, specs:[{icon, text}], recommended}]`, `question`, `badge` ("★ 最推") — 2 or 3 options |
| `decision` | **`question`** (string, or two lines as a list), **`yes`** `{label, text}`, **`no`** `{label, text}`, `icon` |
| `transform` | **`from`** `{icon, value, label, sub}`, **`to`** `{…}`, `arrow`, `note` |
| `flowsteps` | **`items`** `[{icon, title, sub, owner}]` |
| `photo` | **`src`** (local file), `title`, `alt`, `position` (CSS, e.g. "40% 45%"), `height`, `caption` `["text" or {value, unit, label}]`, `marks` `[{x, y, w, h, label}]` (screenshots: numbered pins / boxes, x y w h in % of the image, whole image shown) |
| `speclines` | **`rows`** `[{label, text}]` — a quiet replacement for long chip rows |
| `stattile` | **`value`**, `label`, `delta`, `vs`, `good` (true), `arrow`, `spark` `[numbers]`, `spark_label` `[first, last]` |
| `bullet` | **`rows`** `[{label, actual, target, compare, max, ranges:[poor, ok, good], display, note}]`, `higher_is_better`, `legend` `[actual, target, compare]` |
| `dumbbell` | **`rows`** `[{label, before, after, before_display, after_display}]`, `higher_is_better`, `legend` `[before, after]`, `zero` (true) |
| `slope` | **`items`** `[{label, before, after, highlight, unit}]` (1–6), `left`, `right`, `higher_is_better` |
| `waterfall` | **`start`** `{label, value}`, **`steps`** `[{label, value}]`, `end` `{label, value}`, `unit`, `higher_is_better` |
| `variance` | **`rows`** `[{label, delta, display}]`, `higher_is_better`, `worse`, `better`, `baseline` |
| `stacked` | **`rows`** `[{label, values:[…]}]`, **`series`**, `highlight` (index, default 0), `percent` (true) |
| `heatmap` | **`cols`**, **`rows`** `[{label, values:[…]}]`, `unit`, `higher_is_worse` (true), `mark` (max / min / none), `mark_label`, `legend`, `show_values` (true) — keep to ≤ 6 rows × 9 columns |

Inside `cards` items: `diagram` (any block above), `chart`, `photo` `{src, position, caption}`.
Column charts take an `icon` per bar and a `top_note` line above the bars.

All diagram blocks accept `title` (a small heading above the picture).

## Layout behaviour

Diagrams size themselves from their content: widths follow text length, long text wraps to two
lines and then ends with "…", scale labels move to a second row when points are close. They scale
down with the zone but never above their natural size (so text stays at the page scale). If a
diagram looks cramped, the zone is too small: give it more area or move detail to the footer.

## Ideas and sources

The report-chart forms (stat tile with sparkline, heatmap, dumbbell, emphasis instead of many
colours, diverging bars, stacked part-to-whole) follow the form table of the built-in `dataviz`
skill; actual / target / previous notation, variance bars and bridges follow the IBCS reporting
standard (ibcs.com). Both are described here in our own words. The shape-first approach follows common infographic practice; the category list was checked
against the template families of AntV Infographic (`antvis/Infographic`, MIT: sequence, list,
compare, hierarchy, relation, chart) and the shape → component table of the answer-me-with-html
skill. No code or text was copied; see `upstream-sources.json`.
