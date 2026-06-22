"""UI layer. This package is the ONLY place that imports the GUI toolkit (Kivy).

Keeping the toolkit quarantined here means swapping it (or the compositing strategy
in video_layer.py) doesn't ripple into the camera layer or the app wiring.
"""
