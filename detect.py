# Detects cells in the specified frames.
# Standard imports
import cv2
import numpy as np
import scipy
import scipy.ndimage.measurements as measurements
import sys
import os
import getopt
from video_capture_function import *
from detector_function import *
from background_remover_function import *
from track_cells import *
import pandas as pd

def usage():
    script = os.path.basename(__file__)
    print("\n\nUsage:  " + script + " [options] <input picture> <output picture>")
    print('''
                    Options:
                    -h --help (help)
                    -w --minboxweight (bounding boxes below minboxweight * (averagebox size) area deleted)

                    -n --windowsize (resolution of background removal in terms of pixel size)
                    -b --blocksize (region at which local threshold is calculated)
                    -c --subtractedconstant (constant value subtracted from threshold value in gaussian adaptive threshold)
                    -r --backgroundrelative (default 0, signifying a dark background. If background is lighter than cells, input 1)

                    -t --tuningmode (if tuning background remover, input 'True')

                    <input video> (e.g. ~/input.avi)
                    <output video> (e.g. ~/output.mp4)
                    ''')
    sys.exit()

def main():

    opts, files = getopt.getopt(sys.argv[1:], "h:w:n:b:c:r:t:", [ "help", "minboxweight","windowsize", "blocksize", "subtractedconstant", "backgroundrelative", "tuningmode"])

    if len(files) != 2:
        usage()

    # defaults:
    parameters = {}
    parameters['w'] = 0.3
    parameters['n'] = 1
    parameters['b'] = 1001
    parameters['c'] = 0
    parameters['r'] = 0
    parameters['t'] = False

    # loop over options:
    for option, argument in opts:
        if option in ("-h", "--help"):
            usage()
        elif option in ("-w", "--minboxweight"):
            parameters['w'] = argument
            if np.float(parameters['w']) <= 0:
                usage()
        elif option in ("-n", "--windowsize"):
            parameters['n'] = argument
        elif option in ("-b", "--blocksize"):
            parameters['b'] = argument
        elif option in ("-c", "--subtractedconstant"):
            parameters['c'] = argument
        elif option in ("-r", "--backgroundrelative"):
            parameters['r'] = argument
        elif option in ("-t", "--tuningmode"):
            parameters['t'] = argument

    # split path
    base = os.path.basename(files[0])
    input_picture_name, input_picture_extension = os.path.splitext(base)
    output_path = files[1]
    output_picture_directory, output_picture_extension = os.path.splitext(files[1])

    # parameters
    min_box_weight = np.float(parameters['w'])
    n = np.int(parameters['n'])
    b = np.int(parameters['b'])
    c = np.float(parameters['c'])
    background_relative = np.int(parameters['r'])
    tuning_mode = False
    if parameters['t'] in ['True', 'true']:
        tuning_mode = True

    # write images into a folder
    print('converting video to images...')
    im_list = store_images(files[0], output_picture_directory)
    im_list = im_list[:int(len(im_list)/45)]

    # remove background
    # input_folder = os.path.dirname(output_picture_directory)
    print('removing background...')
    mask_list = remove_background_a2a(n, b, c, background_relative, im_list)
    if tuning_mode:
        write_video(mask_list, files[1])
        sys.exit()
        return

    # run detection on first frame
    print('detecting cells...')
    total_boxes = detect_frames(min_box_weight, output_picture_directory, images_array = mask_list, num_frames = len(im_list))
    # draw boxes on gray scale
    for frame_index, frame in enumerate(im_list):
        f = total_boxes['frame ' + str(frame_index)]
        boxes = []
        for box in f:
            box = (f[box]['x'], f[box]['y'], f[box]['width'], f[box]['height'])
            boxes.append(box)

        # draw
        for index, new_box in enumerate(boxes):
            # access box elements and draw
            p1 = (int(new_box[0]), int(new_box[1])) # point 1 of new box
            p2 = (int(new_box[0] + new_box[2]), int(new_box[1] + new_box[3])) # point 2 of box
            cv2.rectangle(frame, p1, p2, (255,255,255), 2, 1)
            cv2.putText(frame, str(index), (p1[0],p1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)

        # write the current frame of the video
        if output_path is not None:
            cv2.imwrite(output_picture_directory + 'frame_' + str(frame_index) + '.png', frame)

        # write bounding box frame information
        with open(output_picture_directory + '_fframe.txt', 'w') as f:
            f.write("%s\n" % bboxes)

if __name__ == "__main__":
    main()
