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
- Background goes last, or nowhere. The reader rarely needs it.

## Step C — Decision shape (proposals and anything that needs a yes)

- Title names the **decision**, not the topic ("Move to Linear by 5/30").
- Complication carries the number that makes it urgent.
- 2–3 mutually exclusive options, each with its single most important trade-off.
  No recommendation hidden in the options.
- Recommendation: the chosen option and the evidence that tips it.
- Cost in the title = what the reader commits to: one-off **and** recurring (e.g. "60 萬導入＋每年
  180 萬授權"). Never show only the smaller number.
- Name the **approver** (who says yes) and the **owner** (who executes) separately.
- Top 3 risks, each with a one-line mitigation.
- **The ask: one line, yes/no, owner, date.** Never "let's discuss".

## Present the storyline before any design

Show the user, in Chinese:

```
標題（一句結論）：……
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
