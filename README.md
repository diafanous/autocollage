# collage

Drop in images or PDFs, cut them into sections, scatter and layer the sections into a new picture, export at print resolution.

```
uv run server.py        # opens http://127.0.0.1:8765  (uv run server.py 9000 for another port)
uv run test_collage.py
```

Needs [uv](https://docs.astral.sh/uv/); the first run installs Pillow, PyMuPDF, the HEIC codec and the MP4 encoder listed in `pyproject.toml`. Python 3.10+. Everything runs locally; the server only listens on 127.0.0.1.

## Desktop apps

Release downloads include `Collage.exe` for Windows and separate `Collage-macOS-AppleSilicon.zip` and `Collage-macOS-Intel.zip` archives for macOS 15 or later. On a Mac, unzip the matching archive and move `Collage.app` into Applications. Mac builds use ad-hoc signing and are not Apple-notarized; macOS may require approval in System Settings > Privacy & Security on first launch.

Run `uv run --extra desktop desktop.py` to open Collage in its own resizable window. This keeps the existing HTML interface and Python image engine, but does not open an external browser. Windows needs the Microsoft Edge WebView2 Runtime.

GitHub Actions builds and tests the executable before publishing it to [Releases](https://github.com/diafanous/collage/releases). To build locally, run `uv sync --extra desktop --group build`, then `uv run --extra desktop --group build pyinstaller --clean --noconfirm --onefile --windowed --name Collage --add-data "index.html;." --collect-all imageio_ffmpeg --collect-all pillow_heif --exclude-module PIL._imagingft desktop.py` on Windows.

Version 0.1.3 adds up to 16 layers, Ctrl+Z/Ctrl+Y edit history, a fixed sidebar header, export settings under the gear button, HEIC imports, and folder selection. Exports save to Downloads by default; choose another folder in settings to remember it. Existing exports receive numbered filenames rather than being overwritten.

Version 0.1.4 adds native Mac builds and a lightweight TXT export of slider values, tone curves, drawing guide points, source metadata, and map settings. The TXT file contains readable UTF-8 JSON and does not embed source images.

GIF and MP4 exports show the collage progression at a 720-pixel long edge. Smoothness controls frame count and pace controls duration; both have an animation preview. Triptych exports a PNG with the original, collage, and styled migration map in three equal panels. Map start/end markers are selectable; end markers can be scaled, and migration lines meet their edges. Use "save map settings as default" to remember map styling for future launches.

## How it works

1. **Source.** Add any number of images or PDFs (drag onto the window too). The physical size is read from the PDF page or the image's dpi tag. If an image has no dpi tag the size is assumed at 300 dpi and flagged; type the real width and the height follows. **Random from folder:** paste a folder path, say how many, press *pick*: that many random images/PDFs from the folder (not its sub-folders) replace the previous random pick; files you added yourself stay.
2. **Cut.** Width/height sliders (or typed physical sizes) set the section size as a share of the source, which sets the grid (25% = 4 columns). *Portion of each file* below 100% cuts only random square portions of each file (*portions per file* of them), each cut into the same grid; sections stay in the part of the canvas their portion came from.
3. **Collage.** Each section goes back where it was cut, then moves. Every slider value can be typed.

   | slider | does |
   |---|---|
   | scale | section size on the canvas, relative to its real physical size |
   | size variance | random spread around that scale |
   | rotation | max random tilt, degrees |
   | scatter | 0 = home position, 100% = anywhere on the canvas |
   | density | share of sections used per layer |
   | layers | how many times the sections are laid down, each on top of the last |
   | opacity | per-section transparency |
   | edge blur | feathers each section's edge into the paper |
   | grid pull / size / irregularity | the **▦ grid** button on the preview shows a guide grid (moving any of these sliders turns it on). Each section settles in its own cell, a dot marks the landing spot; irregularity makes columns and rows uneven |
   | drawing pull | press **✎ draw** on the preview and sketch: sections drift toward your lines (clear erases them) |
   | seed / paper | reroll the randomness / canvas colour |

   Double-click a slider to reset it. With scatter, variance and rotation at 0 and one layer, the output is the source, rebuilt exactly.
4. **Tone.** Contrast, black/white point and gamma, then a tone curve (click the curve to add a point, drag to move it, double-click to remove). Applied to the sources, so preview and export match.
5. **Output.** Size (in / cm / mm), dpi, and `png` (lossless), `tif` (lossless, Deflate) or `pdf` (page of the exact physical size holding the full-resolution image, lossless). Output is capped at 400 MP.

   - **`map`** exports the *migration map* as a zip of vector PDFs, each the size of the canvas: `collage-1-initial.pdf` (every section's outline where it was cut), `collage-2-migration.pdf` (lines joining each section's old corners to its new ones, so move, turn and scale read at once, plus an arrow along each centre's path; the guide grid and your drawing appear faintly when they steered), `collage-3-final.pdf` (where each section landed), and `collage-map-layers.pdf` with the three as PDF layers. Print or plot the three separate files and stack them. Each layer has its own tone, line opacity, paper colour and paper opacity (0 = no paper, so layers can overlay). Choosing `map` shows the stack on the stage while you adjust. Not every PDF viewer lets you toggle layers (browsers don't); the separate files always work.
   - **also save portion linework** (when *portion of each file* is below 100%) adds a vector PDF, one page per source at its physical size, outlining the selected portions with their numbers and the cut grid inside. With it ticked the download is a zip of the main output and `collage-portions.pdf`.

The preview is rendered by the same engine as the export, at screen size. Sliders drag at half resolution and sharpen on release. Layout is in inches, so the export matches the preview at any dpi.

## Layout

| file | |
|---|---|
| `collage.py` | engine: load, cut, layout, render, export |
| `server.py` | local HTTP server, serves the UI and the font |
| `desktop.py` | starts the local server in a standalone pywebview window |
| `index.html` | the UI (no build step, no framework) |
| `test_collage.py` | self-checks |
| `fonts/` | linked folder holding `paper-mono-v1.0.zip`; the server reads the font straight from the zip. Not tracked by git. |

## Limits

- 8-bit RGB only, no colour management: 16-bit inputs are scaled to 8-bit, CMYK is converted naively (ignoring ICC profiles), and exports carry no colour profile.
- The migration map and portion linework are vector, but the collage itself is raster, and PDF sources are rasterised, not kept as vectors. They are rendered at the resolution the sections will actually have (72-600 dpi).
- Tone is one curve applied to all channels together (no separate R/G/B curves). The drawing pull and grid use at most 400 sampled points / 48 grid rows.
- A 24 x 36 in, 300 dpi export (78 MP) with ~200 rotated sections takes about 10-15 s and ~1.3 GB of RAM; rotation dominates.
