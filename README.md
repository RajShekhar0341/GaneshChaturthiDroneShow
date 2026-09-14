# GaneshChaturthiDroneShow
A Python-powered 3D Ganesh Chaturthi drone show featuring an illuminated city, starry skies, animated Ganpati, a girl welcoming him with a diya, colourful lasers, fireworks, and Perfecto Research greetings.
# ✨ Ganpati 3D Drone Show — Perfecto Research

A Python-powered Ganesh Chaturthi drone-light simulation featuring an illuminated city, starry skies, Ganpati Bappa, and a little girl welcoming him with a diya.

The show combines animated drone formations, colourful laser fans, fireworks, and festive greetings from **Perfecto Research**.

## Features

- **3D city:** Residential buildings, warm window lights, dark roads, and rooftop details.
- **Starry night:** A procedurally generated star field.
- **Ganpati formation:** Drone-light artwork featuring a crown, trunk, ornaments, and traditional clothing.
- **Welcome scene:** A girl in a colourful dress holding a diya.
- **Visual effects:** Rotating mandala, glowing particles, laser fans, and fireworks.
- **Camera modes:** Cinematic aerial view, front view, and adjustable orbit view.
- **90-second loop:** A choreographed sequence with smooth formation transitions.
- **Playback controls:** Pause, replay, fullscreen, and camera switching.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Application logic and animation |
| Pygame | Window, drawing, input, and display |
| NumPy | Coordinates, particle calculations, and perspective projection |

## Project Structure

```text
ganpati_sky_show/
├── main.py              # Rendering, camera, animation, and controls
├── formations.py        # Ganpati, girl, lotus, mandala, and text formations
├── city.py              # Procedural city geometry and lighting
├── requirements.txt     # Python dependencies
├── run_windows.bat      # Windows setup and launcher
├── preview.png          # Rendered festival scene
├── city_preview.png     # Rendered aerial city view
└── README.md
```

## Requirements

- Python **3.11 or 3.12** recommended
- Windows, macOS, or Linux with a graphical desktop
- Internet access for the initial dependency installation

After installation, the show runs locally without API keys or online services.

## Installation

Clone your repository or download and extract its ZIP, then open a terminal in the folder containing `main.py`.

### Windows — Quick Start

Double-click `run_windows.bat`.

From PowerShell, use:

```powershell
.\run_windows.bat
```

If the project is inside a nested folder, enter it first:

```powershell
cd .\ganpati_sky_show
.\run_windows.bat
```

### Windows — Manual Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Virtual-environment activation is unnecessary when using these commands.

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Controls

| Key | Action |
|---|---|
| **Space** | Pause or resume |
| **R** | Replay from the beginning |
| **C** | Cycle through camera modes |
| **Arrow keys** | Adjust the orbit camera |
| **= / -** | Zoom in or out in orbit mode |
| **F** | Toggle fullscreen |
| **H** | Show or hide interface labels |
| **Esc** | Exit |

Arrow keys and zoom controls apply to the third camera mode.

## Show Timeline

| Time | Scene |
|---|---|
| 0–18 seconds | Aerial city opening and rising drone helix |
| 18–29 seconds | Girl and diya welcome |
| 29–47 seconds | Ganpati, lotus, and companion formations |
| 47–62 seconds | Perfecto Research and festival greetings |
| 62–83 seconds | Fireworks and finale |
| 83–90 seconds | Fade-out and camera return |

Some animations overlap to create continuous transitions.

## Run Options

The following examples assume your Python environment has the dependencies installed.

### Start Normally

```bash
python main.py
```

### Lower Resolution

```bash
python main.py --quality low
```

### Jump to the Finale

```bash
python main.py --start 79
```

### Save a Screenshot

```bash
python main.py --start 79 --screenshot preview.png
```

Screenshot mode renders one frame and exits. It uses a headless display by default.

### Short Rendering Run

```bash
python main.py --frames 60
```

This exits after 60 rendered frames.

## How It Works

1. **City generation:** `city.py` creates buildings, window faces, roads, and streetlamp positions using a fixed random seed.
2. **Formation design:** `formations.py` defines outlines using curves and ellipses.
3. **Drone placement:** Curves are sampled at approximately equal distances to create individual drone positions.
4. **Animation:** `performance()` moves particles from starting positions into their target formations.
5. **3D projection:** A virtual camera projects world coordinates onto the display.
6. **Rendering:** Pygame draws the geometry, drone lights, text, and visual effects.

## Customization

### Ganpati Artwork

Edit this function in `formations.py`:

```python
def ganesha():
```

### Girl Artwork and Position

Edit:

```python
def girl():
```

Formation coordinates determine placement:

- **X:** Left or right
- **Y:** Up or down
- **Z:** Depth

### Greetings and Appearance Times

Edit the text entries inside `build()` in `formations.py`.

```python
text_points("Perfecto Research", 298, 198, CYAN)
```

The arguments specify the text, vertical position, width, and colour. The final value in each formation entry controls when it begins appearing.

### Drone Density

Adjust the spacing passed to `curve()`:

```python
curve(points, spacing=2.0)
```

- Smaller spacing creates more drone points.
- Larger spacing creates fewer points.

### Lasers, Diya, and Fireworks

Edit `performance()` in `main.py`.

In the right-side laser block, increase the multiplier in `j * 30` to widen the fan. Very wide beams may extend beyond the camera frame.

### City Layout

Edit `build_city()` in `city.py`. Change the random seed to generate another deterministic layout.

## Troubleshooting

### PowerShell Does Not Recognize the Launcher

Use the current-directory prefix:

```powershell
.\run_windows.bat
```

Make sure the terminal is in the folder containing the file.

### Missing Pygame or NumPy

Install dependencies using the same Python interpreter that runs the application:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Animation Runs Slowly

Use low quality and a smaller window:

```powershell
.\.venv\Scripts\python.exe main.py --quality low
```

Performance depends on CPU speed, display resolution, and scene complexity.

### Window Does Not Open in Colab

This project opens a desktop Pygame window. Run it on a local graphical desktop for interactive playback.

## Scope and Limitations

This is a **stylized, software-rendered 3D visualization**. Characters are drone-light outlines, and the city uses procedural low-poly geometry.

It does not provide:

- Photorealistic character rendering
- Real drone control or collision-free flight planning
- Built-in video export or music playback

The renderer uses approximate geometry sorting rather than a full depth buffer. A 60 FPS cap does not guarantee 60 FPS on every device.

## Preview

![Ganesh Chaturthi drone show](preview.png)

![Night-time aerial city view](city_preview.png)

---

Created for **Perfecto Research**.

**Ganpati Bappa Morya! 🙏**
