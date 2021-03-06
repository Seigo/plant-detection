"""Load (recent image) and Detect commands to load as farmware.

load newest photo in /tmp/images and run calibration
"""

import os
import sys
import glob

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from PlantDetection import PlantDetection

if __name__ == "__main__":
    try:
        RECENT_IMAGE = max(glob.iglob('/tmp/images/*.[Jj][Pp][Gg]'),
                           key=os.path.getctime)
    except ValueError:
        print("No images in /tmp/images")
        sys.exit(0)

    PD = PlantDetection(calibration_img=RECENT_IMAGE, app=True)
    PD.calibrate()
