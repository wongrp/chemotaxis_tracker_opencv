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
    total_boxes = detect_frames(min_box_weight, output_picture_directory, images_array = mask_list, num_frames = 1)

    # track cells
    new_roi_frequency = 400
    total_boxes = track_cells(new_roi_frequency, total_boxes, mask_list, im_list, files[1])

    # write bounding box frame information
    with open(output_picture_directory + '.txt', 'w') as f:
        f.write("%s\n" % total_boxes)

    print(total_boxes)
    # # write the same bounding box frame information to excel
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    excel_writer = pd.ExcelWriter(output_picture_directory + '.xlsx', engine='xlsxwriter')
    for interval in total_boxes:
        startcol = 0
        for frame in total_boxes:
            dict = total_boxes[frame]
            df = pd.DataFrame(dict).T
            df.to_excel(excel_writer, startcol = startcol)
            startcol += 7 # 7 is the number of box attributes.
        startcol = 0
    excel_writer.save()

if __name__ == "__main__":
    main()
