# Company style from a .pptx

When the user uploads a company PowerPoint (ideally a blank template or one with confidential
content removed):

```bash
python3 scripts/extract_brand.py company.pptx --out my-company.json [--logo-out my-company-logo.png]
```

It reads the theme colours, the theme fonts (Latin and East Asian), the slide background, and
the largest picture on the master or first layout as a candidate logo. It writes a style file
based on `assets/styles/brand-template.json`:

- Theme `accent1` → main colour (blue role), `accent2`… mapped to the other zone colours by hue
  (red-ish → problems, green-ish → next). Roles with no matching hue keep the defaults.
- Chart highlight → the main colour **only if it passes** `check_colors.py` against the grey
  context colour; otherwise the default blue stays and the script says why.
- Fonts → the theme fonts by name. Paid fonts are **not** copied; the user's PC provides them.
- Logo → saved next to the style file; path stored in `logo`.

Then:

1. Show the user the extracted colours and fonts and ask if they look right (core rule 2).
2. Render with `--style my-company.json`.
3. **Give the user the style file (and logo) to keep.** Skills cannot save files between
   conversations; next time the user uploads the style file instead of the .pptx.

Rules: do not upload the company file anywhere else; do not keep its content; use it only for
colours, fonts and logo.
