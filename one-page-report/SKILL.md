---
name: one-page-report
description: "Turn project or business material into a one-page visual report (16:9, PNG/PDF/HTML/editable PPT, Chinese and English versions) that a busy reader understands in ten seconds. Interviews the user first, one question at a time, to pin down reader, purpose and limits, then distils a pyramid storyline, picks the skeleton (results, progress, proposal, post-mortem, comparison), charts, icons and layout, and self-reviews before delivery. Use whenever the user wants a one-pager, project report, status update, project summary, business explainer, 一頁式報告, 專案說明, 進度報告, 成果報告, 提案, 簡報一頁, or says 'make this into one page', even if they only paste notes or data."
---

# One-page report

Version 1.0.3 · source: https://github.com/ZIjiun/-one-page-report · see `CHANGELOG.md` in the repo

Make one 16:9 page that a busy reader understands in ten seconds, from the user's own material.
The page is the last step. Most of the value is in the thinking before it: who reads it, what
they must decide, and the one sentence they should remember.

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
   whether an icon that needs a moment of thought stays, which point gets the single highlight.
   List them with a recommendation when you show the first draft, and let the user decide.
3. **Facts only from allowed sources.** Allowed: what the user provides, the company intranet, and
   external sites the company allows. Mark every external fact with its source. Never send the
   user's company material to any other service. **Never invent or "fill in" a number.** If a
   number is missing, ask. Estimates are allowed only when the user agrees, and are labelled.

## Workflow

| Step | Do | Read |
|---|---|---|
| 1 Situation | Ask the user to describe the situation in their own words (reader, occasion, what happened) | — |
| 2 Report type | Propose a type and skeleton with one line of reasoning; the user may accept, switch, mix, or ask for a new one | `references/report-types.md` |
| 3 Purpose | Interview per core rule 1, with the type's own questions | `references/report-types.md` |
| 4 Storyline | Distil: messy input → 3 insights → one-sentence conclusion + 2–4 reasons. Proposal types use the decision-memo shape. **Show the storyline (in Chinese) and get a yes before any visual work** | `references/storyline.md` |
| 5 Charts & colour | Pick each chart by the relationship it shows; one highlight, rest grey; check colours | `references/charts-and-color.md` |
| 6 Layout | Zones = the reader's questions; position carries meaning; weight follows importance; each number appears once | `references/layout.md` |
| 7 Icons | Only where the reader sorts categories fast; 5-second rule; one concept = one icon; always with text | `references/icons.md` |
| 8 Draft & choices | Build the Chinese version first, show it, list open design choices (core rule 2) | — |
| 9 Output | Translate to English with the same spec structure; render both sets | below |
| 10 Self-review | Run the full checklist; fix; report the result | `references/review-checklist.md` |

### Style

Ask once per report which style to use (unless the user already said):
- `handdrawn`: warm paper, hand-written fonts, slightly wobbly lines (internal, casual)
- `business`: clean white, sans-serif, straight lines (managers, clients, formal)
- **Company template**: if the user uploads a company .pptx, run
  `python3 scripts/extract_brand.py company.pptx --out my-company.json` and use that style.
  Give the user the resulting style file to keep and re-upload next time (skills cannot save files
  between conversations). Paid fonts are never bundled: the style names them, and the user's PC
  supplies them. See `references/brand-style.md`.

### Build commands

The report is written as a JSON spec (`references/spec-format.md`). Examples to copy from:
`examples/witcher3-results.*.json` (results), `examples/progress-demo.*.json` (progress),
`examples/proposal-demo.*.json` (proposal). The demo materials they were made from are next to
them (`*.material.md`, fictional data).

```bash
S=<this skill's folder>
python3 $S/scripts/build_report.py report.zh.json --style handdrawn --out out/report.zh.html
python3 $S/scripts/render.py out/report.zh.html            # → .png (3840x2160) + .pdf
python3 $S/scripts/build_pptx.py report.zh.json --png out/report.zh.png --out out/report.zh.pptx
python3 $S/scripts/review.py report.zh.json report.en.json --html out/report.zh.html out/report.en.html \
        --source material.txt --out out/review.json
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
  (a chart, a comparison, a table) or use fewer zones.** Never ship an overflow.
- Bundled fonts (LXGW WenKai TC, Patrick Hand, Inter) are embedded into the HTML automatically,
  trimmed to the characters used.

### Colour check

If the built-in **`dataviz`** skill is available, use it for chart colour decisions and its
validator. Otherwise run the offline stand-in, which gives the same pass/fail results:
`python3 scripts/check_colors.py "#2a78d6,#c9c4bb" --surface "#fbf8f1"`.

## Delivery

1. Send the PNGs first (Chinese, then English), then PDF, HTML and PPTX.
2. In Chinese, say in a few lines: the one-sentence conclusion, the self-review grade and the
   top fixes still open, anything estimated or unverified, the PPT mode used, and the open
   design choices.
3. Do not recap the steps.

## Files

- `references/` the method (read the row for each step above)
- `scripts/` build, render, PPT, colour check, review, brand extraction
- `assets/styles/` style files; `assets/icons.json` 163 Lucide icons (ISC); `assets/fonts/*.zip` bundled fonts (OFL), archived so the skill stays under the 200-file upload limit
- `examples/` complete specs for three report types, both languages
- `portable/` the same method as one instruction file for other AI tools
- `licenses/` third-party licences and credits
- `upstream-sources.json` the skills this one adapted and the versions last reviewed; read only by skill-update-check, never by this skill
