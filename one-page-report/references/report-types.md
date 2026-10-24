# Report types, skeletons and interview questions

Start by asking the user to describe the situation in their own words. Then propose one type
below with a one-line reason. The user can accept it, pick another, mix two, or ask for a new
skeleton. A skeleton is an order of zones; each zone answers one reader question. The types,
questions and picture tables below are starting points, not forms (SKILL.md, "Tools, not
templates").

The skeletons list the zones **after** the background zone. With the background in its own zone,
a skeleton of five becomes six; if it would pass six, merge as `references/layout.md` describes.
Some zones overlap the background and fold into it: a proposal's "Problem", a post-mortem's
"What happened" (its timeline can sit inside the background zone).

## Universal questions (ask only what the material does not answer)

Ask one at a time, most important first:

1. Who reads it? (boss, senior management, client, cross-team, whole company, family)
2. How much background does the reader already have? Suggested answer: "not much: give it its own
   zone". If the reader knows the story, the background shrinks to one line. Then ask the
   background questions below.
3. After reading, what should they do? (approve, choose, support, just know)
4. If they read for ten seconds, what one sentence must they remember?
5. What must not be touched? (confidential numbers, names, wording, brand rules)
6. How will you judge it good? (the user's own words; then add the professional checks)
7. Where will it be shown? (projector, email, phone, print) → affects density and font size
8. Style and languages (handdrawn / business / company template; zh + en by default)

Stop asking when you know what they want, what must not be touched, and how they judge
success. Then restate everything and wait for a yes.

## Background questions (ask until the background zone can be written)

Thin background usually means the interview did not ask enough. Ask these one at a time, each with
a suggested answer drawn from the material, skipping what the material already says. Each answer
fills one row of the background zone (`references/storyline.md`, Step C).

| Row | Ask |
|---|---|
| Situation | Where do things stand now? What is the baseline (numbers, current way of working, current product)? |
| Change | What changed recently? Why does this need settling now? What happens if nothing is done? |
| Decision | What exactly must the reader decide or know, and by when? Is "neither" or "later" an option? |
| Limits | What cannot move (budget, rules, time, space, people)? |
| Who | Who decides, who is affected, who might object, and what does each care about? (always at the company; at home only if others are involved) |
| Ruled out | What was considered and dropped, and why? |

The change and the decision are different questions: the change is what happened, the decision is
what the reader must now answer. If an answer is a guess, label it in the report or leave the row out.

## 1. Results report (project finished) — reader asks "was it worth it?"

Zones: **Results → Issues → What we did → Next → Timeline**

Type questions:
- What did the project set out to fix? What was it like before (baseline numbers)?
- What is different now? Which numbers prove it, and compared with what?
- Which 3 outcomes matter most to this reader?
- What went wrong, and what was done about each problem?
- What happens next, and does anyone need to decide or help?

Writing rule: push every activity up two levels — activity → output → **outcome**.
"Ran 3 trainings" → "120 people trained" → "error rate 8% → 2%". Use the highest level the
evidence supports.

Suggested pictures per zone (`references/diagrams.md`):

| Zone | First choice | Also good |
|---|---|---|
| Results | `bullet` (each KPI vs target and before) | `stattile` with sparkline, `gauge`, `cards` with a chart |
| Issues | `issues` | `heatmap` (where / when it hurts), `variance` (who is short of target) |
| What we did | `chips` / `speclines`, or `waterfall` when actions have measured effects | `photo` with marks for a new screen |
| Next | `flowsteps` with owners and dates | `steps` |
| Timeline | `timeline` | — |

### 1b. Improvement report (a variant of Results) — reader asks "how much better, and why?"

Use when the point is a measured improvement against a baseline (time, cost, quality, errors).

Zones: **Results vs target → What improved → What drove it → What to watch → Next**

| Zone | Picture |
|---|---|
| Results vs target | `bullet` per KPI (actual, target, before); one `stattile` for the headline number |
| What improved | `dumbbell` (each metric before → after), or `slope` when one item rises above the rest |
| What drove it | `waterfall` (baseline → each action's effect → result) — only with measured effects; otherwise a list |
| What to watch | `heatmap` / `variance` / `issues` |
| How work shifted (optional) | `stacked` 100% bars before / during / after |
| Next | `flowsteps` |

Extra questions: the baseline period and its numbers; the target and who set it; whether the
improvement was measured the same way before and after (same definition, same sample); how much of
it each action explains, and whether that split is measured or estimated (label estimates).
Mark lower-is-better metrics (`higher_is_better: false`). Example: `examples/improvement-demo.*.json`.

## 2. Progress report (project running) — reader asks "will it slip? do you need me?"

Zones: **Status → Blockers & risks → Support needed → Timeline → Done so far**

Type questions:
- Overall status per workstream: on track / watch / behind / critical?
- What is late or blocked, why, and what is the plan to recover?
- What do you need from the reader (decision, people, budget, unblock)? By when?
- Which milestones are done, in progress, coming next?
- Any numbers to show progress (percent complete, budget used vs plan)?

Writing rule: status lights always come with an icon and a word, never colour alone.
Lead with what needs the reader, not with what went well. A workstream just under target
(e.g. 94% vs 95%) is `warning`, not `good`; say in the footer that status lights are the
team's judgement. Timelines with past, current and future events: mark past `done`, the one
in progress `doing`, future `plan`.

## 3. Proposal (needs a decision or resources) — reader asks "should I approve?"

Zones: **Problem → Options → Recommendation & benefit → Cost & risk → The ask**

Type questions:
- What problem or opportunity, and what does it cost to do nothing?
- What are the real 2–3 options? (mutually exclusive)
- Which one do you recommend, and which evidence tips it?
- What does it cost (money, people, time) and what could go wrong?
- Exactly what yes/no do you need, from whom, by when?

Writing rule (decision memo): the last zone is one line — a yes/no ask with owner and date.
Never "discuss next steps". In the options zone, show every option on the same criteria and
**mark** the recommended one (column highlight or highlighted bar); keep the **argument** for it
(why it wins) in the recommendation zone, not in the options.

Order of several asks: by deadline, earliest first; if equal, the one that blocks the most.

## 4. Post-mortem (something went wrong) — reader asks "will it happen again?"

Zones: **What happened → Impact → Root cause → Fixes → Prevention**

Type questions:
- Timeline of the incident (start, detected, resolved)?
- Who and what was affected, how much, for how long?
- Root cause (not the symptom)? How do you know?
- What was fixed already, what is still open, owners and dates?
- What changes so it does not happen again?

Writing rule: facts and numbers, no blame. Chronology is fine inside "What happened" only.

## 5. Option comparison — reader asks "which one?"

Zones: **Decision criteria → Options table → Recommendation**

Type questions:
- Which criteria matter, and in what order?
- What are the options and the evidence for each criterion?
- Which one do you recommend, and what would change your mind?

Writing rule: use a table with the same criteria for every option; mark the recommended
column; state the one trade-off that decides it.

Name each option so the reader can tell which thing is meant (a short label in the column
header or card title is usually enough). Why the reader is choosing at all (budget, how it will be
used, limits) is background and goes in the background zone (`references/storyline.md`). How to show the
options depends on what decides the choice: a table for several criteria, `compare` for one
question, a chart for numbers, a drawing for size or layout (`references/diagrams.md`).

## Mixing and new skeletons

- Mixing is fine: e.g. a progress report with one proposal zone at the end ("we need X").
- For a new skeleton, write the 3–6 reader questions in order, then give each a zone.
- Two well-known shapes to borrow from (references, not templates):
  - **A3 report** (Toyota problem solving): the page splits in two. Left: background → current
    condition → goal → root cause. Right: countermeasures → plan → follow-up. Good for improvement
    and problem-solving reports where the background matters.
  - **SCQA / SCPR** (pyramid principle): situation and complication go in the background zone,
    the question is the decision row, the answer or recommendation is the title.
- Keep 4–6 zones, the background zone included. More than 6 means the page is two pages; see
  `references/layout.md` ("When the zones do not fit") for the ways to merge, offered to the user.
