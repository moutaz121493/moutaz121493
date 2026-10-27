# Profile image generators

Every image in the profile README is generated here. Python 3.11+, standard library plus `fonttools` + `brotli`
(font subsetting). Everything is deterministic: a rebuild without changes produces byte-identical files.

```bash
pip install -r scripts/requirements.txt
make assets                 # hero, CAN FD decoder, isometric cards, thesis trace, quiet sections
make homelab activity       # the two data-driven cards (need data/live.json / a GitHub token)
python scripts/preview.py   # GitHub-like preview: README.md -> .preview/*.png (dark + light, 1012 px + 375 px)
```

| Script | Output | Notes |
|---|---|---|
| `hero3d.py` | `hero-*.svg` | Real 3D: a 4-layer network spun around its layer axis, perspective-projected into 72 SMIL keyframes (36 s per turn); a CAN FD frame travels the twisted pair every 6 s and triggers pulses. |
| `canfd.py` | `canfd-*.svg` | A real CAN FD base frame: dynamic stuffing, Gray-coded stuff count + parity, fixed stuff bits, CRC-17, bit-rate switch at the BRS / CRC-delimiter sample points. Layout documented at the top of the file. |
| `iso.py` | `now3d-*.svg`, `card3d-*.svg` | Raised tiles with extrusion + shadow and a small isometric illustration each. |
| `trace.py` | `trace-*.svg` | Typing terminal, content from `data/trace.json` (edit that file, not the script). |
| `homelab.py` | `homelab-*.svg` | From `data/live.json`, which the Raspberry Pi publishes hourly to the branch `live` (aggregate numbers only). Older than 3 h → "last seen X h ago". |
| `activity.py` | `activity-*.svg` | Public GitHub API only: commits (30 d, bots excluded), recently pushed repos, language mix. |
| `sections.py` | dividers, toolbox, journey, footer | The quiet parts. |
| (workflow) | `skyline-*.svg` | `yoshi389111/github-profile-3d-contrib`, colours in `data/skyline-*.json`. |

## Rules these images follow (GitHub's sanitizer)

- Loaded as `<img>`: no scripts, links, hover or external resources inside an SVG. SMIL and CSS animations work.
- Fonts (Chakra Petch, IBM Plex Sans, JetBrains Mono, all OFL, see `fonts/`) are subset per file and embedded.
- Every animated SVG has a static layer: `prefers-reduced-motion: reduce` hides `.m` and shows `.s`.
- Dark and light variants are switched by `<picture><source media="(prefers-color-scheme: …)">` in the README.
- Colours live in `assets/theme.json`; the `*Text` variants keep small text at WCAG AA (≥ 4.5:1) in both themes.

## Workflows

`assets` (on push to these sources) · `activity` (daily) · `contrib` (daily) · `homelab` (every 2 h).
All pinned to commit SHAs, minimal `contents: write`, commits by `github-actions[bot]` with `[skip ci]`.
