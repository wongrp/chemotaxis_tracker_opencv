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

from plot_velocity import *

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
    output_directory_base, output_picture_extension = os.path.splitext(files[1])

    # parameters
    min_box_weight = np.float(parameters['w'])
    n = np.int(parameters['n'])
    b = np.int(parameters['b'])
    c = np.float(parameters['c'])
    background_relative = np.int(parameters['r'])

    # write images into a folder
    print('converting video to images...')
    im_list = store_images(files[0], output_directory_base)
    # im_list = im_list[:int(len(im_list)/6)]

    # remove background
    # input_folder = os.path.dirname(output_directory_base)
    print('removing background...')
    mask_list = remove_background_a2a(n, b, c, background_relative, im_list)

    # split into frame1-frame2 chunks
    split_list = split_video_array(im_list)
    split_list_binary = split_video_array(mask_list)

    total_boxes = {}
    for interval_index, binary_interval in enumerate(split_list_binary):
        print('interval = ', str(interval_index))
        original_interval = np.copy(split_list[interval_index]) # np.copy solves box overlap problem in videos
        interval = np.copy(binary_interval)

        # run detection on first frame
        print('detecting cells...')
        detected_boxes = detect_frames(min_box_weight, images_array = interval, num_frames = 1)

        # interval video name
        interval_output_directory = output_directory_base + '_interval_' + str(interval_index) + '.mp4'

        # track cells
        tracked_boxes = track_cells(400, detected_boxes, interval, original_interval, output_path = interval_output_directory)

        # write bounding box frame information
        total_boxes['interval ' + str(interval_index)] = tracked_boxes

    print('output bounding box information to: ', output_directory_base)
    # write bounding box frame information to text file
    with open(output_directory_base + 'interval.txt', 'w') as f:
        f.write("%s\n" % total_boxes)

    # write the same bounding box frame information to excel
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    excel_writer = pd.ExcelWriter(output_directory_base + 'interval.xlsx', engine='xlsxwriter')
    for interval in total_boxes:
        startcol = 0
        for frame in total_boxes[interval]:
            dict = total_boxes[interval][frame]
            df = pd.DataFrame(dict).T
            df.to_excel(excel_writer, sheet_name = str(interval), startcol = startcol)
            startcol += 7 # 7 is the number of box attributes.
        startcol = 0
    excel_writer.save()

    # take resulting bounding box frame information and plot velocity field. 
    mid_x, mid_y = get_midpoints(total_boxes)

    for i in range(len(mid_x)):
        fname = output_directory_base + 'vf' + str(i) + '.png'
        X1 = mid_x[i][0]
        X2 = mid_x[i][1]
        Y1 = mid_y[i][0]
        Y2 = mid_y[i][1]
        vplot(fname, X1, Y1, X2, Y2)

if __name__ == "__main__":
    main()
