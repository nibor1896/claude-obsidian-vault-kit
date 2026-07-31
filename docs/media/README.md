# Media

Social and repository artwork, all of it rendered from the landing page's own scene rather than
drawn separately — same colours, same typeface, same fibre tracts and knots as
[`docs/index.html`](../index.html). The one exception is the product shot at the bottom of the
table; it is a photograph of a real vault, not a rendering.

| File | Pixels | Where |
|---|---|---|
| `neural_hero-animated-960x480.gif` | 960 × 480 | the README header |
| `neural_github-social-1280x640.png` | 1280 × 640 | GitHub social preview (Settings → General → Social preview) |
| `neural_x-banner-1500x500.png` | 1500 × 500 | X header |
| `neural_kofi-banner-1920x500.png` | 1920 × 500 | Ko-fi header |
| `neural_status-instagram-1080x1920.png` | 1080 × 1920 | Instagram story |
| `neural_status-whatsapp-1080x1920.png` | 1080 × 1920 | WhatsApp status |
| `vault-in-obsidian.png` | 2400 × 1490 | the README, above the licence — what a finished vault looks like |

The two status images carry the product name and nothing else. The banners add the tagline, and the
X one the repository URL.

## The product shot is a real vault, and the numbers on it are countable

`vault-in-obsidian.png` is a screenshot of the author's own vault — seven projects, opened in
Obsidian with the generated root index on the left and the graph view on the right. The frame around
it — window chrome, drop shadow, and a background washed in the same `#D97757` and `#7C3AED` as
everything else here — was composited with Pillow so it sits beside the rendered artwork without
looking borrowed from somewhere else.

**`404 indexed notes` is the sum of the lines visible in the shot** — 121 + 180 + 27 + 33 + 7 + 24 +
12 — so anyone can check it against the image itself. Two other counts were available and are not
used: 492 is every `.md` file including the 37 generated indexes and 7 templates, and 448 is every
note whether indexed or not. `823/823 links resolve` is the output of `check_links` on the same
vault, the same day.

**There is no script for this in `tools/`, on purpose.** It was composited once, by hand, and a
one-off does not earn a permanent home next to the shipped tools — `build_kit.py` would have to carry
it as an exception in `REPO_ONLY` for a file nobody runs twice. Replacing the shot means taking a new
screenshot and compositing it again; the recipe is this paragraph, and the values above are the ones
to re-measure.

The vault on it is the author's, with real project names. That is deliberate — an empty demo vault
proves nothing about what the kit produces after months of use — but it is also the only file here
that carries anything personal.

## The logos are the vendors' own paths

Nothing here is traced or redrawn. Both marks are the Simple Icons paths inlined into the scene —
Claude in `#D97757`, Obsidian in `#7C3AED`, each the vendor's own outline.

## How the animated header loops

A screen recording would drift and show a seam. Instead the page was rendered as 300 deterministic
frames driven by a single `renderFrame(t)` with `t` running 0 to 1, and every animated term is
periodic in `t`, so the last frame meets the first. The dots are the part that needs care: on the
live page each pulse hops to a *random* neighbour forever, which never returns to where it started.
Here each one instead walks a **closed circuit** — a few random hops, then the shortest way home —
exactly once per loop. Circuit lengths of 8 to 20 edges over the 15 second loop reproduce the live
page's own speed. The tracts themselves do not move at all; only the dots do.

Assembled with ffmpeg at 20 fps, 256 colours, Floyd-Steinberg dithering.

## Rebuilding

The generators are scratch tooling and deliberately live outside this repository: a parameterised
copy of the landing page plus a headless browser driving `renderFrame`. Nothing in `tools/` builds
these, and no check reads this folder — see
[how-it-works.md](../how-it-works.md#what-is-not-covered-by-a-check).

**Not measured:** how any of these survive Instagram's or WhatsApp's own recompression, and whether
Ko-fi still wants 1920 × 500 — that size was taken as given, not read off Ko-fi's current spec.
