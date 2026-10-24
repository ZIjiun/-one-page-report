# Credits and third-party licences

one-page-report is released under the MIT licence (see `LICENSE` in the repository root).
It bundles or adapts the following.

| Item | Where | Licence | How it is used |
|---|---|---|---|
| enterprise-ai-skills by Sruthi Reddy (github.com/sruthir28/enterprise-ai-skills, commit ae8fe60) | `references/storyline.md`, `references/report-types.md`, `references/review-checklist.md`, `scripts/build_pptx.py` | MIT (`enterprise-ai-skills-MIT.txt`) | Methods from synthesis, top-down-memo, decision-memo-builder, mckinsey-critic, mckinsey-charts, scpr-framework (background rows) and stakeholder-map (who decides, who is affected) rewritten in our own words; no files copied |
| Lucide icons (lucide.dev) | `assets/icons.json` (173 icons; 10 added in v1.1.0 from lucide-static 0.460.0) | ISC (`Lucide-ISC.txt`) | SVG markup copied unchanged into one JSON file |
| LXGW WenKai TC (霞鶩文楷 TC) by LXGW | `assets/fonts/lxgw-wenkai-tc-*.json` | SIL OFL 1.1 (`LXGW-WenKai-TC-OFL.txt`) | Web font pieces and CSS copied unchanged (base64) into one JSON file per weight; reports embed only the glyphs used |
| Inter by Rasmus Andersson | `assets/fonts/inter.json` | SIL OFL 1.1 (`Inter-OFL.txt`) | Latin web font files |
| Patrick Hand by Patrick Wagesreiter | `assets/fonts/patrick-hand.json` | SIL OFL 1.1 (`Patrick-Hand-OFL.txt`) | Latin web font file |

## Watching the adapted sources

`upstream-sources.json` records the repository, paths and reviewed commit of enterprise-ai-skills and
storytelling-with-data (sammcj/agentic-coding, `Skills/storytelling-with-data`), and a content hash of
the built-in `dataviz` skill files that `scripts/check_colors.py` was checked against.

## Ideas and sources cited (no code or text copied)

- Colour checks in `scripts/check_colors.py` are written from public sources: OKLab (Björn Ottosson,
  2020), colour-vision-deficiency simulation (Machado, Oliveira & Fernandes, 2009), WCAG 2.x contrast.
  Thresholds follow common data-visualisation practice. Results were compared with the built-in
  `dataviz` skill's validator on 12 palettes and matched on every check.
- Storytelling with Data (Cole Nussbaumer Knaflic): the five-line summary in
  `references/charts-and-color.md` paraphrases widely known principles.
- Icon guidance cites Nielsen Norman Group, "Icon Usability" (2014) and Borkin, Bylinskii et al.,
  "Beyond Memorability" (IEEE InfoVis 2015).
- Pyramid Principle (Barbara Minto): the general method, described in our own words; SCQA as a reference skeleton.
- A3 problem-solving report (Toyota): the left/right layout, described in our own words as a reference skeleton in `references/report-types.md`.
- Heading, frame, arrow and aside options in `references/design-options.md` follow common editorial and infographic practice; no code or artwork was copied.

The Witcher 3 example uses public news reporting (sources listed in the example) for
demonstration only; it is not an official CD PROJEKT RED report. The progress and proposal
examples use fictional data.

## Added in v1.1.0 (ideas only, no code or text copied)

- Diagram categories checked against AntV Infographic (antvis/Infographic, MIT) and the
  answer-me-with-html skill's component table.
- Type details (tracking and leading by size), soft shadows instead of hard borders, no stacked
  translucent layers, worst-case text testing and side-by-side options: ideas from
  emilkowalski/skills (MIT), written in our own words.
- Example images are not bundled. The examples run without images; image fields are documented
  in references/imagery.md and must point to files the user supplies.

## Added in v1.2.0 (ideas only)

- Report-chart forms follow the built-in dataviz skill's form table; actual / target / previous
  notation, variance bars and bridges follow the IBCS reporting standard. Described in our own
  words; no code or text copied. The improvement example uses fictional data.
