---
name: one-page-report
description: "Turn project or business material (notes, Excel/CSV data, existing decks or documents, screenshots, or a spoken summary) into a one-page visual report (16:9, PNG/PDF/HTML/editable PPT, Chinese and English, light or dark) that a busy reader gets in ten seconds. Interviews first, one question at a time; builds a pyramid storyline; picks a skeleton (results, improvement, progress, proposal, post-mortem, comparison); lets diagrams and report charts carry the logic (KPI vs target, before/after, waterfall, heatmap, steps, decisions); checks every number against the material. Use whenever the user wants a one-pager, project summary, results or improvement report, status update, proposal, 一頁式報告, 專案成果, 改善成效, 成效報告, 改善報告, 進度報告, 提案, 簡報一頁, 圖表說明, or says 'make this into one page', even if they only paste notes, data or screenshots."
---

# One-page report

Version 1.4.0 · source: https://github.com/ZIjiun/-one-page-report · see `CHANGELOG.md` in the repo

Make one 16:9 page that a busy reader understands in ten seconds, from the user's own material.
The page is the last step. Most of the value is in the thinking before it: who reads it, what
they must decide, and the one sentence they should remember.

**Tools, not templates.** The report types, skeletons, diagrams, charts and layouts in this skill
are tools to pick from, not forms to fill in. The same rules must work for any subject: a project,
a purchase, a plan, an incident. When the material needs something they do not cover (a mixed
skeleton, a zone order of its own, a picture no block draws), plan the exception during the
interview, write it into the requirement summary, and start only after the user says yes. The core
rules below and the page rules (4–6 zones, 4 font sizes, colour roles, one offline file, Chinese
and English) are not tools: they always hold.

**Language rule.** Talk with the user in **Traditional Chinese** (interview, storyline check,
requirement summary, design questions). The final report ships as **two sets with the same
layout: Chinese and English**, unless the user asks for one language.

## Core rules (do not skip)

1. **Interview before building.** After each user answer, do not start yet. Check what is still
   missing that would change the result, and ask **one question at a time, the most important one
   first**. Keep going until you know three things: **what the user wants, what must not be
   touched, and how the user will judge a good result**. Then restate the full requirements and
   wait for confirmation. Only then start. (Information already in the material is not asked again.)
2. **Design choices with no right answer go to the user.** Examples: numbered tabs or icon tabs,
   whether an icon that needs a moment of thought stays, which point gets the single highlight,
   light or dark, which official image. When the choice is visual, show 2–3 versions side by side.
   List them with a recommendation when you show the first draft, and let the user decide.
3. **Facts only from allowed sources.** Allowed: what the user provides, the company intranet, and
   external sites the company allows. Mark every external fact with its source. Never send the
   user's company material to any other service. **Never invent or "fill in" a number.** If a
   number is missing, ask. Estimates are allowed only when the user agrees, and are labelled.

## Where you work: home or company (ask once)

Core rule 3 decides what counts as an allowed source; where the user works decides what that means.
Ask once at the start, unless the user already said: "Is this for home use or for the company?"

| | Home | Company |
|---|---|---|
| Facts and images | the user's material, plus any public website (mark the source) | the user's material, the company intranet, and only external sites the company allows |
| Finding images | official sites, press kits, store pages | only company-allowed sites or the intranet; otherwise ask the user for the files |
| If a site cannot be reached | try another public official source | do not route around it: ask the user to attach the file or point to an intranet copy; if neither, go on without it and say what is missing |
| Company material | stays in this conversation | stays in this conversation; never sent to another service |
| Footer and decision words | sources and data date; the ask names who decides and when | sources, data date, version, author, confidentiality mark; approver and owner named separately |

Record the answer as `"mode": "home"` or `"company"` in the spec's `meta`; `review.py` checks the
footer fields that mode needs.

The page itself always opens offline (fonts, icons and images are embedded), in both modes.

## Reading the material

`references/inputs.md` says how to handle each kind: Excel/CSV data (compute in code, record every
worked-out number under `"derived"`), meeting notes, existing decks or documents, a spoken summary,
and screenshots (evidence photos, numbered marks). Read it before the storyline step.

## Workflow

| Step | Do | Read |
|---|---|---|
| 1 Situation | Ask the user to describe the situation in their own words (reader, occasion, what happened) | — |
| 2 Report type | Propose a type and skeleton with one line of reasoning; the user may accept, switch, mix, or ask for a new one | `references/report-types.md` |
| 3 Purpose | Interview per core rule 1, with the type's own questions. Always ask **how much background the reader already has**, then the background questions (situation, change, decision, limits, who, ruled out) until the background zone can be written; thin background means the interview did not ask enough. Give each question a recommended answer (from the material or the usual case), so the user can reply "as suggested" | `references/report-types.md` |
| 4 Storyline | Read the material (`references/inputs.md`). Distil: messy input → 3 insights → one-sentence conclusion + 2–4 reasons. Proposal types use the decision-memo shape. Write the background zone (its own zone by default; one line only when the reader knows the story). **Show the storyline (in Chinese) and get a yes before any visual work** | `references/storyline.md` |
| 5 Diagrams & charts | For each zone name the **shape of its information** (route, calculation, choice, yes/no, before→after, steps, numbers, dates, appearance, layout & size) and draw it: the picture carries the logic, text supports. Each image gets a job (evidence, identification, mood, or a real thing a drawing cannot show) that decides where it goes. One highlight, rest grey; check colours. Show the zone → diagram plan with the storyline if it changes much | `references/diagrams.md`, `references/charts-and-color.md` |
| 6 Layout | Zones = the reader's questions; position follows the order of those questions; background zone first; weight follows importance; each number appears once; exactly 4 font sizes | `references/layout.md` |
| 7 Icons & imagery | Icons: sort categories fast or act as nodes in a diagram; 5-second rule; one concept = one icon; always with text. Then check coverage: every place the reader sorts categories (zone tabs, the first column of a table, steps, timeline events, issues, card tags) has an icon, or the block says `"icons": false` and you tell the user why. Imagery and theme colours only when they match the content and keep the squint test; place each image by its job | `references/icons.md`, `references/imagery.md` |
| 8 Draft & choices | Build the Chinese version first, show it, list open design choices (core rule 2): heading style, frames, layout style, arrows, summary strip, aside, and what to do with empty space or too many zones. Try each on the page before recommending it; quality first. Do not skip this round and hand over a finished page instead | `references/design-options.md` |
| 9 Output | Translate to English with the same spec structure; render both sets | below |
| 10 Self-review | Run `review.py`, then go through every checklist item it cannot measure; fix; report the result with the step log (Delivery) | `references/review-checklist.md` |

### Style, theme and imagery

Ask once per report (unless the user already said), as one question with a recommendation:
- **Style**
  - `handdrawn`: warm paper, hand-written fonts, hand-drawn diagram lines (internal, casual)
  - `business`: clean, sans-serif, straight lines (managers, clients, formal)
  - **Company template** (below) or **the subject's own look** (a product, game or brand: colours
    from its key art, its official imagery) — `references/imagery.md`
- **Theme**: `light` or `dark` (`--theme`, or `"theme"` in the spec). Every style has both.
  Recommend light for print and PDF, dark for screens and dark key art.
- **Imagery — the user decides, always ask first.** Ask whether to use images at all (header
  image, logo, background, photos in zones), and if yes whether the user has official images or
  wants you to find them on official sources. Before offering to find them, try one download from
  an official source: if this environment cannot fetch images, say so in the same question and
  offer only "you attach them" or "no images". Never add images the user did not agree to.
  For each image, propose its job and placement in the interview (evidence → inside its zone;
  identification → small, next to the name; mood → header or faint background), and let the
  user decide (`references/imagery.md`).
  Show candidates side by side and let the user choose. If a chosen image does not suit the
  chosen theme (e.g. a white studio shot for a dark page), look for a different image that fits
  the theme, or drop it; do not force it — and tell the user which you did.
- **Company template**: if the user uploads a company .pptx, run
  `python3 scripts/extract_brand.py company.pptx --out my-company.json` and use that style.
  Give the user the resulting style file to keep and re-upload next time (skills cannot save files
  between conversations). Paid fonts are never bundled: the style names them, and the user's PC
  supplies them. See `references/brand-style.md`.

### Build commands

The report is written as a JSON spec (`references/spec-format.md`). Examples to copy from:
`examples/witcher3-results.*.json` (results, with gauge / column icons / before→after),
`examples/modely-demo.*.json` (product explainer: route, formula, progress, compare, decision, steps),
`examples/improvement-demo.*.json` (improvement report: bullet, dumbbell, slope, waterfall, variance, stacked, heatmap, KPI tile),
`examples/progress-demo.*.json` (progress), `examples/proposal-demo.*.json` (proposal). The demo materials they were made from are next to
them (`*.material.md`, fictional data). Each example shows one way to do it; copy the parts that
fit the user's material, not the whole page.

```bash
S=<this skill's folder>
python3 $S/scripts/build_report.py report.zh.json --style handdrawn --theme light --out out/report.zh.html
python3 $S/scripts/render.py out/report.zh.html            # → .png (3840x2160) + .pdf
python3 $S/scripts/build_pptx.py report.zh.json --png out/report.zh.png --out out/report.zh.pptx
python3 $S/scripts/review.py report.zh.json report.en.json --html out/report.zh.html out/report.en.html \
        --source notes.txt data.csv deck.pptx --out out/review.json   # .xlsx .pptx .docx read directly; export .pdf to text
```

- **No installs.** Everything uses the Python standard library plus what is already present.
  `render.py` uses Playwright or any Chrome/Edge on the machine. If neither exists, deliver the
  HTML and tell the user to open it and use Print → Save as PDF.
- `build_pptx.py` makes a **picture** PPT by default: the PNG on one 16:9 slide. It always
  looks right. When the user wants to edit in PowerPoint, add `--html out/report.zh.html
  --editable`: text boxes and NATIVE charts (right-click → Edit Data), placed where the
  browser put them. Fonts missing on the viewer's PC can make text run long in that version;
  say so, and keep the PNG as the version to present.
- `render.py` fits the page by zooming 0.75–1.15 and stretching rows to fill it. A `warning`
  means too dense (cut) or too thin. **Thin = cards stretched with empty middles: add evidence
  (a chart, a comparison, a table) or use fewer zones.** Never ship an overflow. Aim for zoom 0.9 or
  more; under that, offer the ways to merge or move content (`references/design-options.md`).
- Bundled fonts (LXGW WenKai TC, Patrick Hand, Inter) are embedded into the HTML automatically,
  trimmed to the characters used.
- Images in the spec (`hero`, `logo`, `backdrop`, `photo`) are local files, embedded into the
  HTML; remote URLs are refused so the page opens offline. Put the credit in `meta.image_credit`.
- Diagrams (`scripts/diagrams.py`) lay themselves out from their content. In the editable PPT
  they become pictures, like the timeline; charts stay native.

### Colour check

If the built-in **`dataviz`** skill is available, use it for chart colour decisions and its
validator. Otherwise run the offline stand-in, which gives the same pass/fail results:
`python3 scripts/check_colors.py "#2a78d6,#c9c4bb" --surface "#fbf8f1"`.

## Delivery

1. Send the PNGs first (Chinese, then English), then PDF, HTML and PPTX.
2. In Chinese, say in a few lines: the one-sentence conclusion, the self-review grade and the
   top fixes still open, anything estimated or unverified, the PPT mode used, and the open
   design choices (style, theme, heading style, frames, highlight, images, and any arrows, summary
   strip or aside). If official images were used,
   say once that the page is for internal use unless the user holds the rights.
3. A **step log**: one short line per workflow step 1–10: done, skipped (and why), or not
   verified. A step that was not run is never reported as done. `review.py` passing is not the
   self-review: it measures only part of the checklist, so say which remaining items you checked
   by eye and which you could not check.
4. Do not recap the steps.

## Files

- `references/` the method (read the row for each step above)
- `scripts/` build, render, PPT, colour check, review, brand extraction
- `assets/styles/` style files, each with a light and a `dark` block; `assets/icons.json` 173 Lucide icons (ISC); `assets/fonts/*.json` bundled fonts (OFL), packed into a few JSON files to keep the file count small
- `examples/` complete specs for five report types, both languages
- `references/inputs.md` how to read each kind of material, including screenshots
- `references/design-options.md` the optional design tools (headings, frames, layout style, arrows, summary strip, aside, empty space, too many zones), when each fits, and the self-check
- `scripts/diagrams.py` the diagram blocks (standard library only)
- `portable/` the same method as one instruction file for other AI tools
- `licenses/` third-party licences and credits
- `upstream-sources.json` the skills this one adapted and the versions last reviewed; read only by skill-update-check, never by this skill
