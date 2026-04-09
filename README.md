# Simple Object Tracker

This is my simple project using Python and OpenCV.
It opens the camera and tracks one object.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you use macOS, allow camera access first.

## Run

```bash
python3 main.py
```

## How it works

The program opens the camera and shows a preview.
When the picture looks okay, press `s`.
Then draw a box around the object.
After that, the tracker follows the object.
It works better if the box is close to the object and not too big.

## Implementation Details

The code opens the webcam first.
Then it shows a live preview.
When the user presses `s`, the program takes that frame.
After that, the user draws a box around the object.
The tracker then follows the object in each new frame.
The program also makes the image a little brighter because the camera was dark.

## Controls

- Press `s` to start
- Draw a box with the mouse
- Press `ENTER` or `SPACE`
- Press `q` to quit

## Demo

For the demo video:

1. Run the code
2. Press `s`
3. Select an object
4. Move the object
5. Show the green box following it
