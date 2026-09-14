# Perfecto Research — Ganesh Chaturthi 3D Sky Festival

A complete Python desktop project: fly over a luminous procedural city, then watch a little girl welcome Ganpati Bappa with a moving aarti plate, drone-light artwork, neon mandala, lasers, fireworks, and festive greetings.

## Windows: easiest start

1. Install 64-bit Python 3.11 or 3.12 from https://www.python.org/downloads/ (enable the Python launcher).
2. Extract this ZIP to a folder.
3. Double-click `run_windows.bat`. The first run installs dependencies and needs internet.

The launcher uses the virtual environment's Python directly, so PowerShell activation is unnecessary.

## Manual setup (Windows terminal, inside the extracted folder)

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

For a slower laptop:

```powershell
.venv\Scripts\python.exe main.py --quality low
```

## macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Run on a desktop with a display. A notebook/Colab output cell cannot show the interactive desktop window directly.

## Controls

| Key | Action |
| --- | --- |
| Space | Pause/resume |
| R | Replay from the aerial opening |
| C | Cycle cinematic / front / orbit cameras |
| Arrow keys | Adjust orbit camera horizontally/vertically (third camera) |
| + / - | Zoom in/out in orbit mode (use the main keyboard equals/minus keys) |
| F | Fullscreen toggle |
| H | Hide/show labels |
| Esc | Exit |

## Show timeline

- 0–18 seconds: aerial city tour and rising light helix.
- 18–29: girl and aarti welcome.
- 29–47: Ganpati and lotus assemble.
- 47–62: Perfecto Research and Ganesh Chaturthi greetings form.
- 62–83: fireworks, lasers, full greeting and Ganpati Bappa Morya.
- 83–90: lights fade and camera returns for the next loop.

## Files

- `main.py`: camera, perspective projection, rendering, glow, animation timeline and controls.
- `formations.py`: editable Ganesha/girl/lotus line artwork and font-to-drone sampling.
- `city.py`: seeded buildings, windows, avenues.
- `requirements.txt`: Python dependencies.
- `run_windows.bat`: setup and launch without shell activation.
- `preview.png`: rendered finale from the actual application.

## Customization

Edit the strings and formation start times in `formations.py:build()` to change branding and greetings. Figure vertices use X/Y coordinates; a third coordinate places them in the 3D scene. Edit the city seed in `city.py` for another skyline. `DURATION` and camera choreography live in `main.py`.

## Rendering and scope

This is a stylized software-rendered 3D visualization with genuine world coordinates, perspective projection, and a moving aerial camera. The characters are luminous line-art drone formations arranged in depth. It is not a photorealistic character animation, real drone controller, collision-free flight planner, or video generator. Lasers and lights are simulated. No music, external assets, API keys or online services are required after installation.

Buildings and window quads use a painter's algorithm, with approximate occlusion rather than a full depth buffer. Performance depends on CPU and resolution; 60 FPS is a frame cap, not a guarantee. Low quality reduces resolution. The more detailed city increases CPU workload. Resizing/fullscreen and keyboard behavior should be checked on your own desktop; automated verification used a headless SDL display.

## Reproduce a still

```bash
python main.py --start 79 --screenshot preview.png
```

The screenshot option uses a headless display by default and exits after saving. `--frames 60` exits after a short rendering run. `--start 55` jumps to a timeline point.

## Technical reference

Pygame official API documentation: https://www.pygame.org/docs/

## Reference-inspired visual update (v2)

Rounded baby-Ganesha silhouette, curled trunk, decorative crown, beaded necklace, orange clothing accents, and a small mouse companion are inspired by the supplied figurine. Evenly spaced spline samples and separated glowing lights follow the drone-photo aesthetic. These are original procedural line-art formations, not a photographic reproduction. Soft radial bloom replaces the coarse glow of v1, and warm avenue lamps enhance the city. No reference image is required at runtime.

Validation: sampled all three camera modes across nine timeline positions with SDL's headless driver, inspected the finale PNG, and checked pause/replay/camera events programmatically.

## Face-to-face welcome update (v3)

The child reference inspired a standing right-facing profile, short curls, bindi, earrings, bangles and a multicoloured patterned dress. Ganpati now has a left-facing head and trunk. Both formations share the same depth plane, with the aarti between them. This is a stylized light-art interpretation rather than an exact portrait. The photograph is not bundled or required at runtime.

## Natural night city (v4)

Replaced cyan roads and transparent window dots with asphalt, warm window quads, irregular block widths, low/mid-rise residences, rooftop structures and streetlamp points. Added 6,500 stars distributed over a hemisphere. Updated both city.py and main.py: copy both when updating an existing project. The city is still a procedural low-poly visualization, not photorealistic footage.
