import numpy as np
import sys
import os
import getopt
from run import *

def usage():
    script = os.path.basename(__file__)
    print("\n\nUsage:  " + script + " [options] <input picture> <output picture>")
    print('''
                    Options:
                    -h --help (help)

                    -n --windowsize (resolution of background removal in terms of pixel size)
                    -b --blocksize (region at which local threshold is calculated)
                    -c --subtractedconstant (constant value subtracted from threshold value in gaussian adaptive threshold)
                    -r --backgroundrelative (default 0, signifying a dark background. If background is lighter than cells, input 1)


                    <input video> (e.g. ~/input.avi)
                    <output video> (e.g. ~/output.mp4)

                    NOTE: when entering parameter format [start, stop, step], do not have space inside the list.
                    ''')
    sys.exit()

def main():

    opts, files = getopt.getopt(sys.argv[1:], "h:n:b:c:r:", [ "help" ,"windowsize", "blocksize", "subtractedconstant", "backgroundrelative"])

    if len(files) != 2:
        usage()

    # defaults:
    parameters = {}
    parameters['n'] = '[1,2,1]'
    parameters['b'] = '[1001,1002,1]'
    parameters['c'] = '[0,1,1]'
    parameters['r'] = 0

    # loop over options:
    for option, argument in opts:
        if option in ("-h", "--help"):
            usage()
        elif option in ("-n", "--windowsize"):
            parameters['n'] = argument
        elif option in ("-b", "--blocksize"):
            parameters['b'] = argument
        elif option in ("-c", "--subtractedconstant"):
            parameters['c'] = argument
        elif option in ("-r", "--backgroundrelative"):
            parameters['r'] = argument


    # split path
    base = os.path.basename(files[0])
    input_name, input_extension = os.path.splitext(base)
    output_directory_base, output_directory_extension = os.path.splitext(files[1])

    # parameters
    n = parameters['n']
    b = parameters['b']
    c = parameters['c']
    r = parameters['r']

    n = eval(n)
    b = eval(b)
    c = eval(c)

    # window size array
    n_vals = np.arange(n[0],n[1],n[2])

    # block size array
    b_vals = np.arange(b[0],b[1],b[2])

    # constant array
    c_vals = np.arange(c[0],c[1],c[2])

    print(c_vals, b_vals, n_vals
    )

    for n in n_vals:
        for b in b_vals:
            for c in c_vals:
                text = ('python scripts/run.py -t True ' + ' -n ' + str(n) + ' -b ' + str(b) + ' -c ' + str(c) + ' -r ' + str(r) + ' ' + files[0] + ' ' + \
                output_directory_base + '_n'+ str(n) + '_b'+ str(b) + '_c' + str(c) + output_directory_extension)
                os.system(text)

    print('done')


if __name__ == "__main__":
    main()
