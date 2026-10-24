# Layout

## The page

- 16:9, 1920×1080 CSS px, exported at 2x (3840×2160). One page; no scrolling.
- Top: a short kicker line (report type | project | owner), then the **title = one-sentence
  conclusion** (one or two lines). Mark the key phrase: `^^marker^^`, good news `==green==`,
  the problem or ask `!!red!!`.
- Under the title, the **background** when the reader needs it (`references/storyline.md`): one
  line to two sentences at body size (spec `"background"`). It is not a zone.
- Body: 4–6 zones on a grid. Footer: sources, estimates note, data date; at the company also
  version, author and confidentiality mark (SKILL.md, "Where you work").

## Zones = the reader's questions

Each zone has a coloured tab with an icon or a number (core rule 2: the user picks) and a short
label, and at the right a **lead line
with the zone's conclusion**. Add the reader's question ("Results — was it worth it?") only
where it helps; a question on every tab reads like a template.
Reading only the tabs and leads should tell the whole story (horizontal logic).

## Position follows the reader's questions

The reader goes top-left first, then right, then down. Put the zones in the order the reader asks
their questions. The grid below is **one arrangement, for a results report**; other reports ask in
another order:

- Comparison: the options on the same criteria (largest) → the recommendation and the one
  trade-off that decides it.
- Proposal: problem → options → recommendation and cost → the ask (last, often full width).
- Post-mortem: what happened (time order) → impact → root cause → fixes and prevention.

Results report example:

```
┌───────────────────────┬────────────┐
│ main message (largest)│ problems / │   top: results
│                       │ risks      │
├───────────────────────┼────────────┤
│ how / details         │ next / ask │   bottom: process and action
├───────────────────────┴────────────┤
│ timeline (full width)              │
└────────────────────────────────────┘
 left 2/3: what we did well   right 1/3: what to watch and what to do
```

Spec: `"layout": {"columns": "2fr 1fr", "areas": ["outcome problems", "method next", "timeline timeline"]}`.
Other grids are fine (e.g. 3 columns for a comparison). If no arrangement here fits, plan one in
the interview and include it in the requirement summary.

## Weight follows importance

- The most important zone gets the most area, the biggest numbers and the strongest colour.
- Detail zones use small text and grey tones.
- Exactly 4 font sizes on the page: **46** big numbers, **34** page title, **18** headings and key
  values, **14** everything else (body, notes, labels, footer). Emphasis inside a size comes from
  weight and colour. Diagrams follow the same scale.
- Type details: large text tracked tight (-0.02em), small labels slightly open; headings line
  height ~1.2, body ~1.5.
- Cards float on a soft shadow instead of a hard outline; lists of problems and steps are quiet
  rows with thin dividers, not a box per item. Fewer frames, more space.
- Squint test: the thing that stands out must be the thing that matters.

## Title position

Centred by default. With a header image on the right (`hero`), the title moves left and leaves the
right side to the image; with a logo, the title starts after it. Neither may overlap the title.

## Each number appears once, next to what it proves

Do not repeat a figure in a KPI row, a card, a chart and the timeline. Put it where it is the
evidence for a claim. The title may restate the one headline figure.

## Evidence sits right under its claim

Card order: claim (title) → number or chart → comparison → "because we did …" at the bottom.
The reader never has to match a number to a claim across the page.

## Density

- `render.py` zoom 0.95–1.10 is ideal. Below 0.8: too dense, cut. Rows stretch to fill the page,
  so a short page does not leave a blank strip; if `render.py` says the content is thin, the
  zones were stretched: add evidence or use fewer zones.
- A zone spanning two rows next to a short zone gets tall. Fill it with evidence (a chart, a
  table) or rearrange the grid so zones of similar length share a row.
- Prefer white space over squeezing. One page holds about 250–450 Chinese characters of body
  text, or 180–320 English words.

## Bilingual sets

Design for the **English length** (about 1.5–2x the Chinese width). Build Chinese first, then
translate inside the same spec structure. Same zones, same order, same numbers.
