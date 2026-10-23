# Charts and colour

If the built-in `dataviz` skill exists in the environment, read it and follow it for chart form
and colour; it is the fuller reference. This file is the offline stand-in. The colour check
script `scripts/check_colors.py` was verified to give the same pass/fail as the dataviz
validator on 12 test palettes.

## Pick the form by the relationship

| You want to show | Use | Spec `kind` / block |
|---|---|---|
| One important number | Big number with a comparison | card `big` or `stat` block |
| Change over time | Line | `chart` kind `line` |
| Compare items | Horizontal bar (long labels) or column | `chart` kind `bar` / `column` |
| Parts of a whole | Stacked bar; pie only for ≤ 3 slices | (use a table if unsure) |
| Progress and dates | Milestone timeline | `timeline` block |
| Before / after | Two bars or side-by-side cards | `chart` or `cards` |
| Several options on the same criteria | Table, recommended column marked (argument for it goes in the recommendation zone) | `table` with `header`, `recommend` |
| Status of workstreams | Status lights with icon + word | `status` block |

Sometimes the answer is not a chart. A single bar is a number. A two-slice pie is a number.

## Make the chart say one thing

- **Chart title = the conclusion**, not the metric. "Peak players beat launch and the TV show",
  not "Peak players".
- **One highlight colour; everything else grey.** Mark the highlighted data point with
  `"highlight": true`.
- **Every number has a comparison**: vs target, vs last period, vs the old record.
- Direct labels on the few points that matter; no number on every point.
- No dual y-axis, no 3D, no rainbow. Two measures with different scales → two charts.
- Recessive axes: thin, light grey, no gridlines.
- Estimated values are labelled as estimates in the chart note.

## Colour roles (fixed across every report)

| Role | Meaning | Rule |
|---|---|---|
| Blue (`c-blue`, chart highlight) | The thing to look at, our results | One highlight per chart |
| Grey | Context, comparison | All non-highlighted data |
| Red (`c-red`, critical) | Problems only | Never for "series 2" |
| Green (good text) | Done, up, success | Always with ▲ or ✓ |
| Yellow/amber (warning) | In progress, watch | Always with … or ! and a word |

Status colours never carry meaning alone: always an icon and a word too. About 8% of men have
red-green colour blindness.

## Check before shipping

```bash
python3 scripts/check_colors.py "#2a78d6,#c9c4bb" --surface "#fbf8f1"
```

- `band` / `chroma` FAIL on the grey context colour is expected (grey is meant to be grey).
- `cvd` FAIL: two series look the same to colour-blind readers → change one, or add labels.
- `normal` FAIL: even full-colour readers will confuse them → change one.
- `contrast` WARN: a mark is faint against the page → it must carry a visible label.
- More than 3 categorical series in a chart where any two can sit side by side → cut to 3 and
  fold the rest into "Other", or split into small charts.

## Storytelling with data, in five lines

1. Know the reader and the action you want before choosing anything.
2. Pick the simplest form that shows the relationship.
3. Remove everything that does not help (borders, gridlines, legends you can replace with labels).
4. Use colour and size to point at one thing.
5. Tell it as a story: the title says what happened, the chart proves it, the note says so what.
