import numpy as np
import cv2
from video_capture_function import *
from random import randint
import json

def annotate_new(frame):
    new_colors = []
    new_boxes = []
    # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
    # So we will call this function in a loop till we are done selecting all objects
    # draw bounding boxes over objects
    # selectROI's default behaviour is to draw box starting from the center
    # when fromCenter is set to false, you can draw box starting from top left corner
    while True:
        box = cv2.selectROI('MultiTracker', frame)
        new_boxes.append(box)
        new_colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
        print("Press q to quit selecting boxes and start tracking")
        print("Press any other key to select next object")
        k = cv2.waitKey(0) & 0xFF
        if (k == 113):  # q is pressed
            break

    print('Selected bounding boxes {}'.format(new_boxes))
    return new_boxes, new_colors
