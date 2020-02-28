# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 11:04:24 2019

@author: wongryan and esfahanp

remove_background() is the base function that takes one image and, depending on conditional parameters, writes the image to a directory.
The three following functions can be chosen depending on the desired format.
"""
import sys
import os
import getopt
import cv2
import numpy as np

# takes one image array and removes background
def remove_background(n, b, c, background_relative, im, output_path = None, write = True):

    # set paths
    if write == True:
        output_picture_directory, output_picture_extension = os.path.splitext(output_path)

    # read image and convert to 8 bit
    original_picture = np.uint8(im)
    original_picture = cv2.cvtColor(original_picture, cv2.COLOR_BGR2GRAY)

	# preprocess pixel values into binary
    final_picture = cv2.medianBlur(original_picture,3)
    binary_picture = cv2.adaptiveThreshold(final_picture,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                                           cv2.THRESH_BINARY,b,c)
    # initialize binary mask
    binary_shape = binary_picture.shape
    mask = np.ones(binary_shape)*255


    # loop: apply nxn window to each passed pixel
    # note: if statements take care of corner and edge cases.
    for i in range(binary_shape[0]):
        for j in range(binary_shape[1]):
            if binary_picture[i, j] == 0:
                if i < n:
                    for counter_i in range(0,i+n):
                        if j < n: # corner case
                            for counter_j in range(0,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j >= n and j <= binary_shape[1] - n: # edge case
                            for counter_j in range(j-n,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j > binary_shape[1] - n: # corner case
                            for counter_j in range(j-n,binary_shape[1]):
                                mask[int(counter_i),int(counter_j)] = 0

                elif i >=n and i <= binary_shape[0] - n:
                    for counter_i in range(i-n,i+n):
                        if j < n:
                            for counter_j in range(0,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j >= n and j <= binary_shape[1] - n:
                            for counter_j in range(j-n,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j > binary_shape[1] - n:
                            for counter_j in range(j-n,binary_shape[1]):
                                mask[int(counter_i),int(counter_j)] = 0

                elif i > binary_shape[0] - n:
                    for counter_i in range(i-n,binary_shape[0]):
                        if j < n:
                            for counter_j in range(0,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j >= n and j <= binary_shape[1] - n:
                            for counter_j in range(j-n,j+n):
                                mask[int(counter_i),int(counter_j)] = 0
                        elif j > binary_shape[1] - n:
                            for counter_j in range(j-n,binary_shape[1]):
                                mask[int(counter_i),int(counter_j)] = 0


    # initialize final picture array
    shape = im.shape
    final_picture = np.zeros(shape)

    # clean image (remove noise)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2,2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


    # write both mask and picture on which it is applied.
    # cv2.imwrite(output_path, final_picture)
    if write == True:
        cv2.imwrite(output_picture_directory + '.png', mask)
    return mask


# # Takes a folder of images and outputs removed backgrond
def remove_background_f2f(n, b, c, background_relative, input_folder, output_directory):
    # Load images
    images = []
    for filename in os.listdir(input_folder):
        im = cv2.imread(os.path.join(input_folder,filename))
        if im is not None:
            images.append(im)
    counter = 0
    for im in images:
        # Detect each frame, index them.
        output_path = output_directory + '_'  + str(counter) + '.png'
        remove_background(n, b, c, background_relative, im, output_path)
        counter += 1

# Takes an array of images and outputs removed background as a picture
def remove_background_a2f(n, b, c, background_relative, im_list, output_directory):
    counter = 0
    for im in im_list:
        # Detect each frame, index them.
        output_path = output_directory + '_'  + str(counter) + '.png'
        if im is not None:
            remove_background(n, b, c, background_relative, im, output_path)
        counter += 1


# Takes an array of images and outputs removed background
def remove_background_a2a(n, b, c, background_relative, input_list):
    counter = 0
    mask_list = []
    for im in input_list:
        print('produced mask ' + str(counter))
        # Detect each frame.
        if im is not None:
            mask = remove_background(n, b, c, background_relative, im, write = False)
        counter += 1
        mask_list.append(mask)

    return mask_list
