# Imagery, themes and light / dark

Images and theme colours make a page feel like its subject (the product, the game, the brand).
They are there to **strengthen** the page, never to compete with it. Order of priority:

0. **The user decides whether to use images at all.** Ask before adding any (header, logo,
   background, photos). "No images" is a fine answer; the page must work without them.
1. Easy to read, the conclusion stands out (squint test).
2. Images and colours match the content.
3. Immersion.

If 3 hurts 1, remove the image.

## Light or dark (ask once, with the style)

Every style has a light and a dark version (`--theme light|dark`, or `"theme"` in the spec).
Colour roles stay the same; only lightness changes. Recommend:

| Situation | Theme |
|---|---|
| Printed, attached as PDF, read on paper | light |
| Projected, shown on screen, product imagery is dark (games, cars at night, cinema) | dark |
| Not sure | light (it prints) |

Dark-theme notes: bright photos are dimmed automatically; a logo made for light pages looks too
dark, so ask for the brand's dark-background logo (`logo.src_dark`). Do not invert a logo.
**Do not force an image into a theme it does not suit.** A white studio shot on a dark page, a
pale misty key art behind a dark page, a black logo on dark: find a different official image that
fits the theme (a night or dusk shot, a dark key art, the brand's white logo) and pass it as
`src_dark` — or leave that image out. Show the replacement candidates to the user.

Per-theme settings: any image field can carry a `dark` object that replaces its fields in the dark
theme, or `"dark": null` to drop it there:

```json
"hero": {"src": "img/studio-white.jpg", "mode": "cutout", "w": 372, "h": 142,
         "dark": {"src": "img/dusk-drive.jpg", "mode": "side", "w": 900, "h": 240, "position": "center 72%"}},
"logo": {"src": "img/logo-black.png", "dark": null},
"backdrop": {"src": "img/mist.jpg", "opacity": 0.35, "dark": null}
```

Images chosen for the dark theme are not dimmed. As a last
resort the build fades a light cut-out's edges and warns; treat that warning as "find another image".

## Theme colours from the subject

When the report is about one product or brand, the page can take its colours from the key art.
Keep the colour roles: take the **highlight** from a colour in the key art that suits "look here"
(often a blue or the brand colour), keep red for problems, green for done, amber for in progress.
A striking key-art colour that clashes with a role (e.g. ember orange vs amber "in progress") stays
in the picture, not in the data. Check every new colour with `scripts/check_colors.py` on the page
colour of the chosen theme (`--surface`, `--mode dark` for dark).

Match the era: a report about a remaster uses the remaster's key art and colours, not the original's.

## An image's job decides where it goes

Before placing any image, say in one line what it does on this page. The job decides the place.
In the interview, propose the job and place of each image with a recommendation; the user decides
(core rule 2). "No image" is always a fine answer.

| Job | Ask | Typical content | Where it goes |
|---|---|---|---|
| **Evidence** | Does the picture itself prove this zone's claim? | a screen, damage, before / after, the real object | inside that zone, edge to edge (`photo`, card `photo`); numbered marks to point at parts |
| **Identification** | Does the reader need to know *which* thing we mean? | a product, an option, a person, a place | small, next to its name: a card `photo` strip on that option's card, or one shared header band labelled left / right; never larger than the data |
| **Mood** | Does it only set the scene, with no information? | key art, a landscape, a brand look (games, brands, travel) | header (`hero`) or a faint `backdrop`; never behind numbers |
| **A real thing a drawing cannot show** | Is a photo faster to read than any diagram? | a site, a design detail, a colour or material | treat it as evidence or identification, depending on the zone's claim |

A lifestyle shot (a family walking, a car on a coast road) is mood, not evidence: in a zone about
seats or boot size it shows none of the claim and reads as decoration (圖文不符). Move it to the
header, or leave it out.

### When to draw instead

Drawn means a diagram built from real numbers and dimensions, never an imitation of a product's design.

| Situation | Do |
|---|---|
| The point is structure, size, quantity, a flow or a relationship that a photo cannot show | draw it (`references/diagrams.md`; size and layout of a vehicle: `seatmap`) |
| No image shows what the zone says | draw it, or use no image |
| The image does not suit the topic or the theme (a white studio shot on a dark page) | find another official image; if there is none, draw it or leave it out |

## Where images go

| Place | Use for | Spec |
|---|---|---|
| Header, right side, fading in | key art with a character or product | `"hero": {"src", "mode": "side", "w", "h", "position"}` |
| Header, cut-out on the page colour | studio shot on white (or on black for dark) — no edges | `"hero": {"src", "src_dark", "mode": "cutout", "w", "h"}` |
| Header, full width behind the title | a calm landscape; the title gets a soft shade | `"hero": {"src", "mode": "band", "h", "opacity"}` |
| Top-left logo | product or brand logo (user-provided) | `"logo": {"src", "src_dark", "h"}` |
| Page background, faint | the key art's own background (mist, texture) | `"backdrop": {"src", "opacity"}` |
| Inside a zone, edge to edge | evidence (the open trunk, the new screen) | `photo` block / card `photo` |
| Card strip, under one option's name | identification (which product or option this card is about) | card `photo` |

Rules:

- **Never behind numbers, charts or body text.** Header and gaps only; zones stay opaque.
- **A character must be recognisable or not used.** A face placed faintly behind a zone reads as
  noise. Put it in empty header space, clear and uncropped at the face.
- **No sticker look.** No visible image edges on the page (use `cutout` only when the photo
  background matches the page; otherwise `side` or `band`, which fade out). No framed thumbnails,
  no coloured label boxes or dots over photos. Photos go edge to edge; captions sit on the dark
  gradient at the bottom (`caption`).
- **Check every downloaded image** for stray lines, UI text, watermarks, dimension marks; crop them out.
- Low-resolution images (under ~1200 px wide) only work as blurred backgrounds.

## Where images come from

Home or company (SKILL.md, "Where you work") decides which sites count. At the company, only
company-allowed sites and the intranet; when a site is blocked, do not try another route to it —
ask the user to attach the image or point to an intranet copy, or go on without the image.


- Only from the user, or from **official sources the user agrees to**: the brand's own site,
  its press / media kit, the game's store page (Steam), the company's newsroom. Not wallpaper
  sites, not search-result thumbnails.
- **Never generate, draw or imitate** a logo, character or key art.
- When the user asks you to find images: list the official source, show the candidates side by
  side (a contact sheet), recommend 2–3 with one line each on why they fit the content, and let
  the user choose (core rule 2). Download only the chosen ones; tell the user where they were saved.
- Put the source and rights holder in `meta.image_credit` (the build warns if it is empty), e.g.
  `圖片：Steam 商店頁 © CD PROJEKT RED，內部示範`.
- A page with a brand's official logo or key art is for **internal use** unless the user has the
  rights; a page marked "not official" should not carry the official logo when shared publicly.
  Mention this once at delivery.

## Self-check

- [ ] Squint test passes with the images on: title first, then the zone conclusions
- [ ] Every image has a job (evidence, identification, mood) and sits where that job puts it
- [ ] Every image matches the content (right product, right version, right era)
- [ ] No image behind data; no visible image edges; no framed thumbnails
- [ ] Characters and products recognisable where they appear
- [ ] Title contrast still ≥ 4.5:1 over the image (the shade / text shadow does its job)
- [ ] `image_credit` filled; internal-use note given if needed
