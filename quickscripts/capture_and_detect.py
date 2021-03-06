"""Capture and Detect commands to load as farmware.

take a photo and run plant detection
"""
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from PlantDetection import PlantDetection

if __name__ == "__main__":
    PD = PlantDetection(app=True)
    PD.detect_plants()
