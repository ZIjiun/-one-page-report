# Changelog

## 1.3.0 — 2026-10-24 (fixes from the v1.2.0 review)

**Numbers you can trust**
- `review.py` checks decimals too (4.3, 2.6 h); only whole numbers below 10 are skipped.
- `review.py --source` reads .xlsx, .pptx and .docx with the standard library, and CSV cell by cell;
  PDFs via `pdftotext` when present.
- New spec field `"derived"`: each worked-out number with its formula and inputs; `review.py`
  recomputes it and checks the inputs are in the sources.
- `waterfall` stops the build when the steps do not reach the end value, and says the gap.
- 100% `stacked` rows that do not add to 100 are no longer rescaled: the gap is drawn as
  "other / unknown" and a note is printed.
- `bullet`: exactly on target counts as met (✓).

**English pages**
- Diagram default labels follow the report language (Before/After, Better/Worse, Our pick …).
- Latin labels measured wider and allowed to overhang, so short labels are no longer clipped.

**Your work**
- Description lists the real triggers: 改善成效, 成效報告, 改善報告, 專案成果, 圖表說明, Excel, screenshots.
- New `references/inputs.md`: Excel/CSV, meeting notes, decks and documents, spoken summaries, screenshots.
- Results skeleton suggests a picture per zone; new Improvement variant (1b) in `report-types.md`.
- Home / company mode (SKILL.md): which sites count, and what to do when a site is blocked.
- Screenshots: `photo` blocks take numbered `marks` (pins and boxes) with a legend.
- Interview questions come with a suggested answer, so "as suggested" is a valid reply.
- Portable instructions trimmed to about 7,600 characters; unverified claude.ai file-limit claim removed.

## 1.2.0 — 2026-10-24

**Report charts for results and improvement**
- 8 new blocks: `stattile` (number + change + sparkline), `bullet` (actual vs target vs before),
  `dumbbell` (before → after per item), `slope` (two points in time), `waterfall` (what drove the
  change), `variance` (gap to target, right = better), `stacked` (part-to-whole, 100% or absolute),
  `heatmap` (two dimensions, one hue, worst cell outlined).
- `higher_is_better: false` for times, costs and error rates: better stays green and to the right.
- New "reports about improvement" guide in `references/diagrams.md`; colour rules for report charts.
- New example: `examples/improvement-demo.*.json` (fictional customer-service pilot).
- Stress-tested: equal values, negatives, huge ranges, long labels, empty rows, dense heatmaps (warns).
- Sources (ideas only): the built-in dataviz skill's form table; the IBCS reporting standard.

## 1.1.0 — 2026-10-24

**Pictures carry the logic**
- New diagram blocks that lay themselves out from their content: `route`, `formula`, `progress`,
  `gauge`, `compare`, `decision`, `transform`, `flowsteps`, plus `photo` and `speclines`.
  Cards accept `diagram` and `photo`; column charts accept an icon per bar and a note line.
- New workflow step: name each zone's shape of information, then pick its diagram
  (`references/diagrams.md`).
- Stress-tested with worst-case text: long labels wrap, then end with "…"; close scale labels
  move to a second row; big numbers keep a halo over lines.

**Light and dark themes**
- Every style (`handdrawn`, `business`, company template) has a `dark` block; choose with
  `--theme light|dark` or `"theme"` in the spec. Dark palettes checked with `check_colors.py`.

**Imagery and the subject's own look**
- `hero` (side / cutout / band, with `src_dark`), `logo` (with `src_dark`), `backdrop`, photo blocks. Local files
  only, embedded; credit in `meta.image_credit` (warned when missing).
- Per-theme image settings: `"dark": {…}` swaps the image (and its mode) in the dark theme, `"dark": null` drops it.
- Images only when the user agrees (asked with the style); an image that does not suit the theme is replaced with one that does, or dropped.
- Rules for matching images to content, placement, finding official images and rights
  (`references/imagery.md`).

**Calmer, more refined page**
- Exactly 4 font sizes (46 / 34 / 18 / 14) across the page and diagrams.
- Tracking and leading by size; cards on soft shadows; problem and step lists as quiet rows.
- Hand-drawn zone frames are clean lines (the wobble filter broke straight lines into steps).
- Footer date never wraps; footer text at 14 px.

**Other**
- 10 Lucide icons added (car, battery-charging, utensils, route, calendar, armchair, speaker,
  fuel, luggage, baby).
- New example: `examples/modely-demo.*.json`. Witcher example uses the new blocks.
