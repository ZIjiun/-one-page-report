# Changelog

## 1.3.2 — 2026-10-25 (background first, design options you choose)

**Background**
- The background gets its own zone by default, first after the title, written as rows with icons:
  situation, change, decision, limits, who, ruled out (SCPR; who-decides from stakeholder-map, both
  adapted from enterprise-ai-skills, MIT). It shrinks to one line only when the reader knows the story.
- The interview asks the background questions one at a time until each row can be written; a row is
  never filled by guessing.
- A3 and SCQA are listed as reference skeletons.

**Design options** (`references/design-options.md`; every one optional, recommended with a reason,
tried on the page first, and chosen by the user; quality first)
- Zone headings: `tab` (default), `number`, `bar`, `label`, `ribbon`; one per page.
- Zone frames: `solid` (evidence), `dashed` (the one zone to act on), `open` (short text that is not
  evidence), with a three-question test for when a zone goes without a frame.
- A zone shorter than its row: `fit` `stretch` (default), `center`, `content`, plus the layout
  fixes to try first (shorten the tall neighbour, move a related picture in, change widths).
- Too many zones: merge, two pictures in one zone, move detail out, or another skeleton.
- Layout style: even grid or bento (sizes by importance, edges on the grid). Staggered zones are
  not offered.
- `links` (arrows between zones, drawn in the gap; the gap widens), `summary` (a strip above the
  footer), `aside` (one speech bubble beside the title).
- `speclines` rows take an `icon`; the label column is aligned.
- The editable PPT keeps dashed frames, underlined headings, arrows and their labels.

Nothing changes for an existing spec: all five examples render as before.

## 1.3.1 — 2026-10-24 (works for any subject: tools, not templates)

**Rules that hold for any subject**
- SKILL.md opens with a principle: report types, skeletons, diagrams, charts and layouts are tools,
  not templates. Exceptions are planned in the interview and confirmed before building; the core
  rules and page rules always hold. Examples show one way, not a form to copy.
- Background: the interview asks how much the reader already knows. The background (why the report
  exists) goes under the title, sized to that reader: one line, two sentences, or its own zone when
  it is the point. New spec field `"background"`; it shows in the editable PPT too.
  `references/storyline.md` (Step C) replaces "background goes last, or nowhere".
- Images are placed by their job: evidence (inside the zone), identification (small, next to the
  name), mood (header or faint background), or a real thing a drawing cannot show. The job and place
  of each image are proposed in the interview; the user decides. `references/imagery.md`.
- Layout: zones follow the order of the reader's questions; the results grid is one example, with
  the usual order for comparison, proposal and post-mortem. Zone tabs take an icon or a number.
- Home or company decides the footer and the decision words: home = sources and data date, "who
  decides, by when"; company = also version, author, confidentiality, approver and owner. New
  `meta.mode`; `review.py` checks only the fields that mode needs.

**Blocks and scripts**
- New `seatmap` block: a top view of a vehicle drawn to scale, with seats per row, folded rows and
  where the luggage goes. It is one way to draw size and layout, not a rule for comparisons; it draws
  vehicles only (other objects: a bar chart of the real dimensions, or a user-provided plan).
- Neutral Chinese defaults: 之前 / 之後 (was 改善前 / 改善後) and ★ 建議 (was ★ 最推), matching the English.
  Existing examples set their own labels and are unchanged.
- `flowsteps` widens (up to 560 px) before wrapping titles, so English pages no longer turn into
  tall, thin step lists that shrink the whole page.
- `waterfall` widens with the number of bars so labels do not run together.
- Card `photo.caption` takes the same list form as the `photo` block.
- `review.py` ignores layout and drawing settings (image size and opacity, drawing scale, seat
  counts) when tracing numbers, and no longer reads "長 4.72" as a version number.

**Docs**
- `report_type` lists `improvement`; it is a label only.
- The portable instructions carry all of the above, now about 7,600 characters (was 7,983, too close
  to the 8,000 limit), and include the interview questions for improvement and comparison reports.

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
