# Plant Detection
Detects and marks green plants in a (not green) soil area image using Python OpenCV.

The goal is to mark unwanted volunteer plants for removal.

For an overview of the image processing performed, see [the wiki](../../wiki/Plant-Detection-Image-Processing-Steps).

## Contents
 * [Installation](#installation)
 * [Basic Usage](#basic-usage)
   * [Option 1: Run script](#run-the-script)
   * [Option 2: Python console](#alternatively-process-images-using-a-python-command-line)
   * [Option 3: GUI](#or-run-the-gui-and-move-the-sliders)
 * [Suggested Workflow](#image-file-processing-suggested-workflow)
 * [Tips](#tips)
 * [Project Directory](#project-directory)

---

## Installation

`pip install -r requirements.txt`

## Basic Usage

#### Run the script:

Using the sample soil image, `soil_image.jpg`.

Run the script: `python PlantDetection.py`

View `soil_image_marked.jpg`

#### Alternatively, process images using a python command line:
```python
from PlantDetection import PlantDetection
help(PlantDetection)
PD = PlantDetection(image='soil_image.jpg')
PD.calibrate()
PD.detect_plants()
PD = PlantDetection(image='soil_image.jpg', morph=15, iterations=2, debug=True)
PD.detect_plants()
```

#### Or, run the GUI and move the sliders:
`python PlantDetection.py --GUI`

Default image to process is `soil_image.jpg`. To process other images, use:

`python PlantDetection.py --GUI other_image_name.png`

<img src="https://cloud.githubusercontent.com/assets/12681652/15620382/b7f31dd6-240e-11e6-853f-356d1a90376e.png" width="350">

## Image file processing suggested workflow

#### 1. Save image to be processed
For example: `test_image.jpg`

#### 2. Run the GUI and move the sliders:
`python PlantDetection.py --GUI test_image.jpg`

This will create a plant detection parameters input file from the slider values.

#### 3. Run detection:
`python PlantDetection.py test_image.jpg`

>Or, for more options, enter a python command line: `python`
```python
from PlantDetection import PlantDetection
PD = PlantDetection(image='test_image.jpg', from_file=True)
PD.detect_plants()
```
>(_For examples of output for graphic-related keyword arguments, see [the wiki](../../wiki/IO#graphics))_

#### 4. View output
Annotated image: `test_image_marked.png`

## Tips

#### View help
`python -c 'from PlantDetection import PlantDetection; help(PlantDetection)'`

#### Hue range aid
`python PlantDetection.py --GUI PD/p2c_test_color.jpg`

## Project Directory

```
plant-detection
├── PD  - Plant Detection Package
│   ├── __init__.py
│   ├── Capture.py  - take photos with a camera
│   ├── Parameters.py  - handle input parameters
│   ├── Image.py  - image processing
│   ├── DB.py  - handle plant data
│   ├── P2C.py  - pixel to coordinate conversion
│   ├── CeleryPy.py  - convert plant data to CeleryScript
│   ├── ENV.py  - environment variable save and load operations
│   ├── GUI.py  - interactively change input parameters
│   ├── p2c_test_calibration.jpg  - coordinate conversion calibration test image
│   ├── p2c_test_objects.jpg  - coordinate conversion detection test image
│   └── p2c_test_color.jpg  - color range test image
├── tests  - project test suite
├── quickscripts  - scripts to run specific tasks
├── soil_image.jpg  - plant detection test image
├── PlantDetection.py  - calibrate and detect plants
└── README.md
```
