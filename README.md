# motionDetector

# Introduction

This is a small python script designed to detect and highlight any motion in a live video feed from a specified image source. It can be used to monitor a specific area for activity or to trigger an alert when movement is detected. The app displays a live feed with any detected motion highlighted by a green rectangle, and also saves a video of the detected motion to the local directory.

With the motion detector app, you can easily set up a simple surveillance system or use it for any other purpose where motion detection is needed. Simply run the app and specify the image source, and it will start detecting and highlighting any motion in the live feed.

# Prerequisites

Before you can install and run the motion detector app, you need to have the following dependencies installed on your system:

    Python 3
    OpenCV
    Numpy

To install these dependencies, you can use a package manager such as pip. For example, to install OpenCV and Numpy, you can use the following commands:

pip install opencv-python
pip install numpy

# Usage

To run the app, open a terminal and navigate to the directory where the app is located. Then, enter the following command:

python3 motionDetector.py

To specify a different image source, use the -s flag followed by the source. For example:

python3 motionDetector.py -s 0

This will use the default camera (usually the built-in webcam on a laptop).
# Output

The app will display a live feed from the specified image source, with any detected motion highlighted by a green rectangle. The app will also save a video of the detected motion to the local directory.
