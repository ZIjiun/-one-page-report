# Design options: what to offer, when, and how to check it

The page rules never change: the title is the conclusion, 4–6 zones, exactly 4 font sizes, the
colour roles, one highlight, no decoration, one offline file, Chinese and English. Everything in
this file is a **tool on top of those rules**. None is required; each has a job.

## How to offer them (core rule 2)

1. Look at the material and the reader, and pick the option that fits. Say it in one line with the
   reason ("numbered headings: the page has a reading order").
2. **Try it before recommending it.** Build the page and look at the PNG. An option that cuts text
   the reader needs (a label ending in "…"), pushes the zoom under 0.9, or breaks the reading order
   is not offered for this page, however well it worked elsewhere.
3. When two or three options are all good and the choice is a matter of taste, show them side by
   side and let the user pick. Otherwise recommend one and move on: quality first, then speed.
4. Put the choices into the requirement summary, or list them as open design choices with the first
   draft.

## Zone headings (`"zone_heading"`, one style for the whole page)

| Value | Looks like | Suits |
|---|---|---|
| `tab` (default) | coloured label on the frame line | most work reports; clear categories |
| `number` | `01` `02` … in reading order, no icon | a page read in order: proposals, A3, steps, comparisons with a decision |
| `bar` | a coloured bar on the left of a plain heading | formal, data-heavy reports; the quietest |
| `label` | heading above the frame, underlined | casual pages, hand-drawn style, family readers |
| `ribbon` | outlined banner with faint ends | events, marketing, pages meant to feel lively |

Never mix styles on one page. The heading stays at size 18 in the zone's colour.

## Zone frames (`"frame"` on a zone)

The frame says what role the content plays.

| Value | Use for | Limit |
|---|---|---|
| `solid` (default) | evidence and analysis: numbers, charts, comparisons, and the background zone | none |
| `dashed` | the one zone where the reader must act or decide (a decision, the ask, how to choose) | at most one per page |
| `open` | lead-in or side text that is not evidence | text only, no charts or numbers that prove a claim |

Test for `open`: (1) remove it and the conclusion still stands; (2) it talks to the reader (a
reminder, an opinion, a lead-in); (3) it is one or two sentences. All three yes → no frame. The
background zone is evidence of why the report exists, so it keeps a solid frame unless the reader
already knows the story and it is only a short reminder.

## When a zone is shorter than its row (`"fit"` on a zone)

A row is as tall as its tallest zone, so a short zone beside a tall one shows empty space.
`review.py --html` flags any zone whose content fills less than 70% of it. Do not fill it with
invented content (core rule 3). Options, in order of preference:

| Option | How | Watch for |
|---|---|---|
| Shorten the tall neighbour | smaller drawing (`seatmap` `scale`), fewer rows, move detail to the footer | text cut by an ellipsis, a drawing too small to read |
| Move a related picture in | put a diagram that belongs to this zone's story inside it (one zone, two pictures) | the zone growing past its row |
| Change the column widths | narrower short zone, wider tall zone (`layout.columns`) | other zones getting cramped |
| Center the content | `"fit": "center"`: the space splits above and below and reads as white space | the space is still there |
| End the frame at the content | `"fit": "content"`: the frame stops where the content does | a gap in the grid; best with open frames or a bento layout |

## When the zones do not fit (more than 6, or the zoom drops under 0.9)

Offer only the ways that apply to this material:

- **Merge zones that answer one chain of questions**: problem + fix (`issues` has both), next steps
  + timeline (`flowsteps` takes owners and dates), options + recommendation (`compare` marks the
  pick), cost + risk (a chart beside a list).
- **Two pictures in one zone**, when they have different shapes (a decision and a list of issues).
- **Move secondary content out**: detail to the footer, the headline number into the title, a
  one-line remark into the zone's lead or an aside.
- **Another skeleton**: A3 or SCQA (`references/report-types.md`).

## Layout style

| Style | How | Suits |
|---|---|---|
| Even grid | rows and columns of similar size | formal, data-heavy pages |
| Bento | a finer grid (e.g. 6 columns) where zones take different sizes by importance; every edge still on the grid | pages that should feel designed without losing the reading order |

Staggered zones (off the grid) are not offered: they break the alignment check and the reading order.

## Extra elements (only when the content has a job for them)

| Element | Spec | Job | Limits |
|---|---|---|---|
| Arrow between zones | `"links": [{"from", "to", "label"}]` | A leads to B (background → the options; the decision → its costs) | only for a real cause or sequence; 1–3 per page; label a few words. The gaps widen to fit the arrows, so zones get narrower: check that leads and chart labels still fit, in English too |
| Summary strip | `"summary": {"icon", "color", "lead", "items", "result"}` | a closing action list or a condition = result line, above the footer | never repeats the title; it does not count as a zone but takes space |
| Aside | `"aside": {"icon", "text"}` | one remark to the reader beside the title: a reminder or an opinion | at most one; no numbers or evidence; never over data or the title; with a header image on the right (`hero` side or cutout) leave it out or put the remark in a zone |
| Row icons | `speclines` rows take `icon` | lets the reader scan the rows (background, specs) | one concept = one icon (`references/icons.md`) |

Pure decoration (stars, hearts, sparkles) is never added, whatever the style.

## Self-check after applying any option

- [ ] Title still the conclusion; reading order still follows the reader's questions
- [ ] Still 4–6 zones and 4 font sizes; zoom 0.9 or more
- [ ] No text cut by "…" that the reader needs; no overlap (`review.py --html`)
- [ ] One heading style; at most one dashed zone and one aside; open zones hold no evidence
- [ ] Arrows point at real relations; the summary does not repeat the title
- [ ] Both languages built and checked; the editable PPT still opens (dashed frames, underlines,
      arrows and labels carry over)
