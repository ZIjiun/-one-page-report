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

## An image must show what its zone says

Before placing a photo, say in one line what the zone claims, then ask: does this picture show
that? A lifestyle shot (a family walking, a car on a coast road) in a zone about seats and boot
size shows none of it, and reads as decoration (圖文不符). Then, in order:

1. Find an official image that shows the claim (the open boot, the third row, the charging port).
2. If there is none, **draw it** with a diagram (`seatmap`, `route`, `transform`…) — drawn from
   real dimensions and numbers, never an imitation of the product's design.
3. Keep the mood pictures for the header (`hero` band) or the background, where they set the scene
   and do not pretend to be evidence. Two options can share one band: place the two official
   photos side by side with a soft blend, and label "left / right" in the kicker.

## Where images go

| Place | Use for | Spec |
|---|---|---|
| Header, right side, fading in | key art with a character or product | `"hero": {"src", "mode": "side", "w", "h", "position"}` |
| Header, cut-out on the page colour | studio shot on white (or on black for dark) — no edges | `"hero": {"src", "src_dark", "mode": "cutout", "w", "h"}` |
| Header, full width behind the title | a calm landscape; the title gets a soft shade | `"hero": {"src", "mode": "band", "h", "opacity"}` |
| Top-left logo | product or brand logo (user-provided) | `"logo": {"src", "src_dark", "h"}` |
| Page background, faint | the key art's own background (mist, texture) | `"backdrop": {"src", "opacity"}` |
| Inside a zone, edge to edge | a photo that is evidence (the open trunk, the new screen) | `photo` block / card `photo` |

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
- [ ] Every image matches the content (right product, right version, right era)
- [ ] No image behind data; no visible image edges; no framed thumbnails
- [ ] Characters and products recognisable where they appear
- [ ] Title contrast still ≥ 4.5:1 over the image (the shade / text shadow does its job)
- [ ] `image_credit` filled; internal-use note given if needed
