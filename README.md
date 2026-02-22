# BeatSpace Multitouch Bridge

Standalone OSC bridge for BeatSpace (Sonic Charge Microtonic).  
Receives OSC multitouch messages and writes them to a JSON file that the BeatSpace Microtonic script reads in real time.

# Demo

- Video: https://www.youtube.com/watch?v=om4IqrFOAt4
- Controller example: MobMuPlat (https://mobmuplat.com)

# Features

- Runs standalone via Python
- Low latency (optimized file writing for real-time performance)
- Configurable (GUI: Port, Multiplier, File Path)

# OSC Protocol

The server listens for OSC messages with address `/myMultiTouch`.  
It expects the string identifier `touchesByTime` followed by a sequence of `index x y` triplets.

Format:
```text
/myMultiTouch touchesByTime [index] [x] [y] [index] [x] [y] ...
```

Example:
```text
/myMultiTouch touchesByTime 1 0.046 0.810 2 0.439 0.440
```

Parameters:
- index: integer (1–8) representing the touch point / channel
- x, y: float values in range 0.0–1.0

# Installation

# Prerequisites

- Python 3
- python-osc

Install dependency:
```bash
pip3 install python-osc
```

# Install BeatSpace script files

Move `BeatSpace_main.js` `latentPoints.json` `server.py`  into the Microtonic scripts folder:
```text
/Library/Application Support/Sonic Charge/Microtonic Scripts/BeatSpace.mtscript
```

Notes:
- Overwrite existing files if prompted (recommended: backup the existing folder first)

# Permissions (macOS)

The server must be able to write `latentPoints.json` inside the BeatSpace script directory:
```bash
sudo chmod -R 777 "/Library/Application Support/Sonic Charge/Microtonic Scripts/BeatSpace.mtscript"
```

# Usage

# Start the OSC server

```bash
cd "/Library/Application Support/Sonic Charge/Microtonic Scripts/BeatSpace.mtscript"
python3 server.py
```

# Configure

- A GUI window opens
- Set OSC Port (default: 9000)
- Select the multiplier (in my case is 999. because MobMuPlat sends value 0-1 and BeatSpace needs 0-1000)
- Click Start Server

# Run Microtonic

- Open Microtonic
- Load the BeatSpace script
- Send OSC messages from your controller (e.g., MobMuPlat)

# Configure MobMuPlat

- Connect your phone/tablet to your computer via USB
- Transfer the files `Main.mmt` `Main.pd` `sfondo2.png` into the MobMuPlat folder on your device
- Unplug the device and connect to the same network (check MobMuPlat network configuration)
- Load the patch on MobMuPlat
- Enjoy Multitouch Microtonic

# Credits

BeatSpace is a script for Sonic Charge Microtonic.
