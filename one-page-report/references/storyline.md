# Storyline: from messy material to one sentence

Adapted (rewritten, not copied) from the synthesis, top-down-memo and decision-memo-builder
skills in enterprise-ai-skills by Sruthi Reddy (MIT). See `licenses/`.

The test for the whole page: **can the reader stop after the title and still know what you think
and what you want?** If they must read to the end to find the answer, you wrote a story.

## Step A — Synthesise (when the material is a pile)

Use this when the user gives notes, minutes, survey results, weekly reports or data dumps.

1. **Cluster.** Tag each data point with the theme it belongs to. Let themes come from the data.
2. **Force-rank to 3.** Rank themes by frequency, severity for the decision, and surprise
   (did it contradict what the user expected?). Keep the top 3. Throwing away most of the input
   is the job.
3. **Name each insight as a claim**, not a topic.
   - Topic: "Onboarding feedback". Claim: "Users drop off at step 3 because they must invite
     teammates before they see value."
4. **Stack 2–3 pieces of evidence** under each: exact numbers, named sources, short quotes.
5. **Write the so-what** for each: "Because this is true, the reader should ___."
6. **Anti-summary check.** Would someone who never saw the material know what to do next?
   If they would say "interesting", it is a summary. Rewrite.

## Step B — Pyramid (answer first)

```
            ONE-SENTENCE CONCLUSION   ← becomes the page title
      ┌──────────────┼──────────────┐
   REASON 1       REASON 2       REASON 3     ← become zone leads / card titles
   evidence       evidence       evidence     ← become numbers, charts, rows
```

- The title states the **answer**, not the topic. "Q3 project report" is a topic.
  "System live: handling time halved; phase 2 needs 2 more people" is an answer.
- 2–4 reasons, ideally 3. More than 4 means you have not synthesised yet.
- Reasons are **MECE**: they do not overlap, and together they prove the conclusion.
  If all reasons are true, the conclusion must be true.
- Evidence sits **under its own reason**, not in a separate "data" section.
- The answer comes first; background never comes before it. See Step C.

## Step C — Background: its own zone, explained clearly

Background = why this report exists and what it must settle. Most readers were not in the room, so
by default the background gets **its own zone, the first one after the title**: the reader gets the
answer in the title, then the reason the question came up. The structure follows SCPR (situation,
complication, problem, recommendation; adapted from the scpr-framework skill in
enterprise-ai-skills, MIT): the title is the recommendation, the background zone carries the rest.

Write it as a `speclines` block, one row per item, each with an icon (`references/icons.md`). Use
only the rows the material supports; never fill a row by guessing (core rule 3).

| Row | Says | Example |
|---|---|---|
| Situation (現況) | where things stand now, with the baseline numbers | current car, budget, how often it is used |
| Change (變化) | what changed and why it matters now; the cost of doing nothing | a child is coming; the old car needs more repairs |
| Decision (要決定) | the specific question the reader must answer, and by when | pick one of two cars by the end of next month |
| Limits (限制) | what cannot move: rules, budget, time, space | no home charger; narrow parking |
| Who (誰參與) | who decides, who is affected, who may object (company mode; adapted from stakeholder-map) | the two of you decide; parents ride often |
| Ruled out (排除過) | options already dropped and why | Model Y: same charging problem |

Keep "change" and "decision" apart: the change is what happened, the decision is what the reader
must now answer.

Exceptions, agreed in the interview:

| Reader | Background |
|---|---|
| Does not know the story (default: another team, a client, family, a new manager) | its own zone, first after the title |
| Knows the story (the manager who assigned the work) | one line under the title (spec `"background"`), or fold it into the kicker |

- Background holds premises only: never the conclusion's numbers (each number appears once).
- The background zone counts toward the 4–6 zones. When the page does not fit, see
  `references/layout.md` ("When the zones do not fit").

## Step D — Decision shape (proposals and anything that needs a yes)

- Title names the **decision**, not the topic ("Move to Linear by 5/30").
- Complication carries the number that makes it urgent.
- 2–3 mutually exclusive options, each with its single most important trade-off.
  No recommendation hidden in the options.
- Recommendation: the chosen option and the evidence that tips it.
- Cost in the title = what the reader commits to: one-off **and** recurring (e.g. "60 萬導入＋每年
  180 萬授權"). Never show only the smaller number.
- At the company, name the **approver** (who says yes) and the **owner** (who executes)
  separately. At home, say who decides and by when.
- Top 3 risks, each with a one-line mitigation.
- **The ask: one line, yes/no, owner, date.** Never "let's discuss".

## Present the storyline before any design

Show the user, in Chinese:

```
標題（一句結論）：……
背景（第一格；讀者已知多少：……）：現況……／變化……／要決定……／限制……／誰參與……／排除過……
理由 1：…… 證據：……
理由 2：…… 證據：……
理由 3：…… 證據：……
（提案類）請讀者決定：……（誰、何時）
建議骨架：……（理由一句）
需要你確認的數字或推估：……
```

Wait for a yes. Changing a storyline is cheap; changing a finished page is not.

## Common mistakes

- Burying the lead: "Over six weeks the team explored…". Cut. Lead with the answer.
- Topic-shaped reasons: "Pricing" → "Pricing is 2.4x the standalone value".
- Orphan numbers: every number says what it means and compared with what.
- Hedging: "we may want to consider". Recommend, or do not write it.
- Only good news: a page with no problems is less believable. Show the problem and its fix.
