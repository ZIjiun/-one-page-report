# Self-review before delivery

Run `scripts/review.py` for the automatic part, look at the PNGs, then grade the page.
Report the grade and the open fixes to the user in Chinese.

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
- [ ] No orphan numbers: each says what it means and vs what
- [ ] Next steps say who, what, by when (or say "date not set")

## B. Data credibility

- [ ] Data date shown ("as of …")
- [ ] Units on every number; tricky metrics defined ("Steam only")
- [ ] Every number traces to the user's material or a named source (`review.py` lists each one)
- [ ] Estimates are labelled
- [ ] One name per thing across the page
- [ ] **zh and en versions: identical numbers, dates and names** (`review.py` compares them)

## C. Design

- [ ] Squint test: the most visible thing is the most important thing
- [ ] Zones align to one grid; even gaps
- [ ] ≤ 4 font sizes
- [ ] Readable in black-and-white print, at phone width, and projected
- [ ] Text contrast ≥ 4.5:1 for body text; meaning never by colour alone
- [ ] No text overlaps or overflows (`render.py` warns; also look at the PNG)
- [ ] Icons: one concept = one icon; all with text; none decorative

## D. Before handing over

- [ ] **Stranger test**: a reviewer that did not make the page reads only the PNG and states
      the conclusion and the ask. If it gets them wrong, the page failed.
      - In Claude with sub-agents: start a fresh agent with only the PNG and this prompt:
        "You see a one-page report for the first time. In two sentences: what is the main
        conclusion, and what does it ask the reader to do? Then list anything you could not
        understand."
      - Elsewhere, or when you cannot start a sub-agent: give the user that prompt to paste into
        a new chat with the PNG, and say in the delivery that the stranger test is still open.
- [ ] Version info: date, version, author; confidentiality mark if the material is internal

## "AI feel" self-check (then the user decides)

Flag and fix these:
- Generic phrases with no number: "significantly improved", "robust", "seamless", "leverage",
  「大幅提升」「全面優化」「賦能」「打造」
- Every item in threes with the same rhythm; every card the same length
- Decorative icons or emoji; gradients and glow for no reason
- Titles that are topics, not conclusions
- Perfect symmetry where the content is not symmetric
- Missing the specific: names, dates, units, the one awkward true detail
- A question on every zone tab: keep the question only where the reader would really ask it;
  otherwise the label alone is enough
- Stock phrases in leads such as 「三項都有對策」 / "all covered": say what the fixes are instead
- Table cells that say 「素材未提供」 / "not given": a hole looks unfinished. Ask the user, or drop
  the row or column

## Decision clarity (proposals and asks)

- [ ] The title's cost figure is the **total the reader commits to** (one-off + first-year
      recurring), or the recurring part is said in the same line
- [ ] It is clear **who decides** and **who executes** (two different words: 核准人 / 負責人,
      approver / owner)
- [ ] An estimate states its scope ("pilot tickets only, 46% of volume")

## Design-quality self-check

- One clear focal point per zone
- Generous, even spacing; nothing touching a border
- Numbers set large and quiet; labels small and grey
- Colours limited to the roles in `charts-and-color.md`
- Consistent corner radius, line weight and icon size
