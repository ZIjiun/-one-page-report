# Changelog

## 1.0.1 — 2026-10-23

- claude.ai allows at most 200 files per skill; 1.0.0 had 399. Icons are now one file
  (`assets/icons.json`) and fonts are zip archives (`assets/fonts/*.zip`): 41 files in total.
  Output is pixel-identical to 1.0.0 (checked on all six examples).

## 1.0.0 — 2026-10-23

First release.

- Interview-first workflow: one question at a time, confirm full requirements before building
- Five report types with skeletons and interview questions: results, progress, proposal, post-mortem, comparison
- Storyline method (synthesis → pyramid → decision shape), adapted from enterprise-ai-skills (MIT)
- Chart, colour and icon rules; offline colour checker matching the dataviz validator on 12 palettes
- Hand-drawn and business styles; company style extracted from a .pptx
- Output: Chinese and English sets as PNG (3840×2160), PDF, self-contained HTML, PPTX (picture by default, editable with --editable)
- Automatic review: zh/en fact match, numbers traced to source, overlaps and overflow, vague words, icon consistency
- Portable one-file instructions for ChatGPT, Copilot, Gemini and other AI tools
- Tested on 3 scenarios (results, progress, proposal) in both languages, plus an independent stranger test
