# Media

Social and repository artwork. Five designs, each rendered at every size that is actually used.

| Prefix | Design |
|---|---|
| `e-blueprint` | **the one to use.** Night ground, a single luminous hue, the file as a light source whose beams fan into the five stations, hairline orbit rings for the guards |
| `a-document` | typographic: it looks like the file it is — flush-left, a coral rule, the steps as a ledger |
| `b-split` | two surfaces, one per product, with a seam between them |
| `c-ledger` | the five steps as measured bars, coral to violet |
| `d-neon` | the ring chain: five glowing rings connected by curved ribbons |

| Suffix | Pixels | Where |
|---|---|---|
| `portrait-1080x1350` | 1080 × 1350 | Instagram feed, WhatsApp |
| `square-1080` | 1080 × 1080 | Instagram, WhatsApp |
| `github-1280x640` | 1280 × 640 | GitHub social preview (Settings → Social preview) |
| `wide-1600x900` | 1600 × 900 | README header, slides |

Both `.svg` and `.png` are here. The SVG is the source — edit that, then re-render.

## The logos are the vendors' own files

Nothing here is a traced or redrawn mark.

- **Obsidian**: `obsidian-logo-gradient.svg` from obsidian.md, 512 × 512, inlined with its own radial
  gradients intact.
- **Claude**: `claude_app_icon.png` from claude.ai, 338 × 338. No SVG of the mark is published, and
  the PNG ships as coral on cream with rounded corners because it is an app icon. Rather than trace
  it, the cream is keyed to transparent with `feColorMatrix`: alpha is driven by luminance and RGB is
  pinned to `#D97757`, so the pixels stay the vendor's and the edge cannot go grey.

## Rebuilding

The generators live outside this repo (they are scratch tooling, not part of the kit). Each poster is
a single Python file that writes SVG; the PNGs come from headless Edge at the exact target size:

```
msedge --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
       --window-size=1080,1350 --screenshot=out.png file:///…/e-blueprint_portrait-1080x1350.svg
```

**Not measured:** how any of these render on Instagram's own compression, and whether the hairlines
survive it. Text is set in Inter with a Segoe UI fallback — a machine with neither will shift metrics.
