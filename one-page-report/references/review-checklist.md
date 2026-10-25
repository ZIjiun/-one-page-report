# Self-review before delivery

Run `scripts/review.py` for the automatic part, look at the PNGs, then grade the page.
Report the grade and the open fixes to the user in Chinese.

**Passing `review.py` is not the review.** It measures only part of this list (marked
"review.py" below). Go through every other item yourself, and in the delivery say which items you
could not check (the step log, `SKILL.md` → Delivery).

## Grade (adapted from mckinsey-critic in enterprise-ai-skills, MIT)

| Grade | Meaning |
|---|---|
| Green | Ready. Minor polish only. |
| Yellow | Fixable now, do not send as-is. |
| Red | Storyline or structure is broken. Go back to the storyline step. |

Output in the reply: grade + one line; **top 3 fixes** ranked by impact (fix them, then say
which remain); **one thing that works** (protect it).

## The user's criteria (ask how they judge; these are the defaults)

- Reader gets it at a glance and does not ask "so what?"
- Numbers and facts are right (every figure traceable to the material)
- Fast to make, few rounds of changes
- Same quality every time
- Complete content
- Logical layout
- **No "AI feel"** — the user judges; the skill self-assesses first (see below)
- **Design-quality feel** — the user judges; the skill self-assesses first

## A. Logic (automatic where possible)

- [ ] Horizontal reading: tabs + leads + title alone tell the story
- [ ] Vertical reading: every zone's content proves its lead; nothing off-topic
- [ ] 30-second test: you can say the whole page in 30 seconds
- [ ] Background fits the reader: a reader who does not know the story learns from the background
      zone why the report exists, what changed and what must be decided; no conclusion numbers in it;
      no row filled by guessing
- [ ] No orphan numbers: each says what it means and vs what
- [ ] Next steps say who, what, by when (or say "date not set")

## B. Data credibility

- [ ] Data date shown ("as of …")
- [ ] Units on every number; tricky metrics defined ("Steam only")
- [ ] Every number traces to the user's material or a named source (`review.py --source <files>`;
      .xlsx .pptx .docx are read directly, export PDFs to text)
- [ ] Every worked-out number is under `"derived"` with its formula and inputs, and recomputes
- [ ] Totals add up (waterfall steps reach the end value; 100% rows add to 100)
- [ ] Home or company mode respected: no blocked site worked around; missing items named
- [ ] Estimates are labelled
- [ ] One name per thing across the page
- [ ] Each number appears once, next to what it proves; the title may restate the headline figure
      (review.py flags a number shown in more than one zone)
- [ ] **zh and en versions: identical numbers, dates and names** (`review.py` compares them)

## C. Design

- [ ] Squint test: the most visible thing is the most important thing
- [ ] Zones align to one grid; even gaps
- [ ] Exactly 4 font sizes (46 / 34 / 18 / 14), diagrams included (review.py `--html` measures the
      rendered sizes: a chart scaled up, or squeezed under 12 px)
- [ ] Every zone: is its main element a picture of the relationship (diagram, chart, photo) where the
      content has a shape? Text describing a flow, choice, route or calculation → draw it
- [ ] Light / dark: built in the theme the user chose; dark-theme logo and photos checked
- [ ] Imagery (if any): matches the content, never behind data, no sticker edges, credit in footer
      (`references/imagery.md` self-check)
- [ ] Readable in black-and-white print, at phone width, and projected
- [ ] Text contrast ≥ 4.5:1 for body text; meaning never by colour alone
- [ ] No text overlaps or overflows (`render.py` warns; also look at the PNG)
- [ ] Icons: one concept = one icon; all with text; none decorative
- [ ] Icons are **where they should be**: zone tabs, the first column of a table, steps, timeline
      events, issues and card tags each have one, or the block says `"icons": false` and the user
      was told why (review.py lists the gaps)
- [ ] One highlight per chart (review.py flags charts with more)
- [ ] Design options (if used): one heading style; at most one dashed zone and one aside; open
      zones hold no evidence; arrows show real relations; the summary strip does not repeat the
      title (`references/design-options.md`, self-check)
- [ ] No large empty space in a zone (`review.py --html` flags under 70% filled), and nothing
      invented to fill one

## D. Before handing over

- [ ] **Stranger test**: a reviewer that did not make the page reads only the PNG and states
      the conclusion and the ask. If it gets them wrong, the page failed.
      - In Claude with sub-agents: start a fresh agent with only the PNG and this prompt:
        "You see a one-page report for the first time. In two sentences: what is the main
        conclusion, and what does it ask the reader to do? Then list anything you could not
        understand."
      - Elsewhere, or when you cannot start a sub-agent: give the user that prompt to paste into
        a new chat with the PNG, and say in the delivery that the stranger test is still open.
- [ ] Footer for the mode (`meta.mode`): home = sources and data date; company = also version,
      author and a confidentiality mark if the material is internal
- [ ] Step log ready: each workflow step 1–10 done, skipped (why) or not verified

## "AI feel" self-check (then the user decides)

Flag and fix these:
- Generic phrases with no number: "significantly improved", "robust", "seamless", "leverage",
  「大幅提升」「全面優化」「賦能」「打造」
- Every item in threes with the same rhythm; every card the same length
- Decorative icons or emoji; gradients and glow for no reason (theme imagery is allowed only under
  `references/imagery.md`: it matches the content and stays out of the data)
- Every zone the same shape (title + big number + small text) when the content has different shapes
- A box around every item; many zone colours where three roles would do
- Titles that are topics, not conclusions
- Perfect symmetry where the content is not symmetric
- Missing the specific: names, dates, units, the one awkward true detail
- A question on every zone tab: keep the question only where the reader would really ask it;
  otherwise the label alone is enough
- Stock phrases in leads such as 「三項都有對策」 / "all covered": say what the fixes are instead
- Table cells that say 「素材未提供」「未公開」「待補」 / "not given": a hole looks unfinished. Ask the
  user, or drop the row or column (review.py flags these)

## Decision clarity (proposals and asks)

- [ ] The title's cost figure is the **total the reader commits to** (one-off + first-year
      recurring), or the recurring part is said in the same line
- [ ] It is clear **who decides** (and by when). At the company, also **who executes**: two
      different words, 核准人 / 負責人, approver / owner
- [ ] An estimate states its scope ("pilot tickets only, 46% of volume")

## Design-quality self-check

- One clear focal point per zone
- Generous, even spacing; nothing touching a border
- Numbers set large and quiet; labels small and grey
- Colours limited to the roles in `charts-and-color.md`
- Consistent corner radius, line weight and icon size
- Pictures carry the logic; text explains them; a photo is either edge to edge or not there
