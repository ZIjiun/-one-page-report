# Reading the material

Most reports start from a mix: some numbers, some notes, an old deck, a screenshot or two, and
what the user says. Whatever the mix, two rules hold:

1. **Every number on the page traces back** to a file the user gave, or to a calculation recorded
   under `"derived"`. Run `scripts/review.py --source <the files>` before delivery.
2. **Ask instead of guessing.** A missing baseline, a unit you cannot tell, two files that disagree:
   ask the user (core rule 1), with your best guess as the suggested answer.

## Excel / CSV data

- Read it with code (Python `csv`, or `openpyxl` / pandas when present), not by eye. Check the sheet
  name, header row, units and date range, and say them back to the user in one line.
- Compute every derived figure in code: changes (6.5 → 2.6 = −60%), averages, totals, shares.
  Record each one in the spec:

  ```json
  "derived": [
    {"value": "−60%", "formula": "(2.6-6.5)/6.5*100", "from": ["6.5", "2.6"]},
    {"value": "210", "formula": "1180-970", "from": ["1180", "970"]}
  ]
  ```

  `review.py` recomputes each formula (numbers and + − × ÷ only) and checks the inputs are in the
  source files. Round only for display; keep the precision the reader needs (one decimal for hours,
  whole points for scores out of 100).
- Pick the comparison the reader cares about: before vs after, actual vs target, this period vs last.
  If the data has no baseline or target, ask for it; do not invent one.
- Charts take the real values. Totals must add up: a `waterfall` whose steps do not reach its end
  value, or 100% stacked rows that do not add to 100, are flagged when the page is built.
- Pass the data files themselves to `review.py --source` (.csv, .tsv, .xlsx are read directly).

## Meeting notes and loose notes

- Pull out claims, numbers, decisions, owners and dates; ignore chatter.
- Notes often hold rounded or remembered numbers ("about 20% less overtime"). If a data file has the
  exact figure, use it and say so; if not, label it as approximate or ask.
- Cluster into themes (`references/storyline.md`), then turn activities into outcomes:
  "held 3 trainings" → "45 people trained" → "first reply 6.5 → 2.6 h".

## Existing decks and documents (.pptx, .docx, .pdf)

- Extract the text with the matching skill (pptx, docx, pdf-reading) or with code; read the speaker
  notes and tables too, not just slide titles.
- A deck usually has more than one page can hold. Keep only what answers the reader's questions;
  move detail to the footer or leave it out, and tell the user what was left out.
- A company template deck is a style source, not content: use `scripts/extract_brand.py` for its
  colours and fonts (`references/brand-style.md`).
- `review.py --source` reads .pptx and .docx text directly. For a PDF, export its text to .txt first
  (`pdftotext` is used automatically when it exists).

## A spoken summary

- It is allowed material (the user provides it), but numbers given in conversation need a source
  for the footer: write "per <user / team>, <date>" in `meta.sources`.
- Repeat back the numbers you heard in the requirement summary, so the user confirms them.
- Save the user's words to a short notes file and pass it to `review.py --source`, so the check
  still works.

## Screenshots

- A screenshot is evidence of what changed (a new screen, an error, a dashboard). Use it in a
  `photo` block; never redraw it by hand.
- To point at parts of it, add numbered marks (x / y in % of the image; w / h for a box):

  ```json
  {"type": "photo", "src": "img/new-ticket-screen.png", "alt": "new ticket screen",
   "marks": [{"x": 4, "y": 25, "w": 55, "h": 30, "label": "**AI draft** written when the ticket opens"},
             {"x": 3.5, "y": 64, "label": "One click to **use the draft**"}]}
  ```

  The whole image is shown (not cropped) so the marks land exactly. Keep to 1–5 marks.
- Before / after: two `photo` blocks side by side in `columns`, the same crop and size.
- Numbers read off a screenshot (a dashboard figure) still need tracing: type them into a notes
  file with the screenshot name and pass that file to `review.py --source`.
- Check screenshots for personal or confidential data (names, emails, IDs) and ask before using them.
