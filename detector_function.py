import cv2
import numpy as np
import scipy
import scipy.ndimage.measurements as measurements
from skimage.feature import peak_local_max
from skimage.morphology import watershed
import sys
import os
import getopt
import imutils

# takes an image and outputs to a path
def detect(im, min_box_weight):

    w = min_box_weight # abbreviate
    s = [[1,1,1], # structuring element for labeling
         [1,1,1],
         [1,1,1]]
    im = np.uint8(im)
    if len(im) == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # taken from https://www.pyimagesearch.com/2015/11/02/watershed-opencv/
    # compute exact Euclidean distance from every binary
    # pixel to the nearest zero pixel, then find peaks in this
    # distance map
    D = scipy.ndimage.distance_transform_edt(im) # compute euclidean distance map
    localMax = peak_local_max(D, indices=False, min_distance=10,
    	labels=im) # find peaks in the euclidean distance map

    # perform a connected component analysis on the local peaks,
    # using 8-connectivity, then apply the Watershed algorithm
    markers, num_features = measurements.label(im, s) # label image
    markers_m, num_features_m = measurements.label(localMax, s) #
    labels = watershed(-D, markers, mask=im)
    labels_m = watershed(-D, markers_m, mask=im)
    print("[INFO] {} unique segments found".format(num_features))


    # loop over the unique labels
    # labeled, num_features = measurements.label(im, s) # label image
    # print('number of features detected: ', num_features)
    markers = measurements.find_objects(labels) # find labeled objects, output is slice.
    markers_m = measurements.find_objects(labels_m)

    bboxes = []
    bboxes_m = []
    for i in range(len(markers)):
        p1 = markers[i][1].start, markers[i][0].start
        p2 = markers[i][1].stop, markers[i][0].stop
        bboxes.append([p1,p2])

    for i in range(len(markers_m)):
        p1_m = markers_m[i][1].start, markers_m[i][0].start
        p2_m = markers_m[i][1].stop, markers_m[i][0].stop
        bboxes_m.append([p1_m,p2_m])

    # calculate the average area
    areas = []
    for i in range(len(bboxes)):
        p1 = bboxes[i][0]
        p2 = bboxes[i][1]
        area = (p2[0]-p1[0])*(p2[1]-p1[1])
        areas.append(area)
    mean_area  = np.mean(areas)

    # delete small boxes based on avg box size.
    for i in reversed(range(len(bboxes))):
        p1 = bboxes[i][0]
        p2 = bboxes[i][1]
        area = (p2[0]-p1[0])*(p2[1]-p1[1])
        if area < min_box_weight*mean_area:
            del bboxes[i]

    ratiothresh = 1.2 # currently hardcoded parameters
    areathresh = 600
    length_boxes = len(np.copy(bboxes))
    delete_list = []
    # the following algorithm asks the user if the following is one cell or multiple cells.
    for i in range(length_boxes):
        p1x = bboxes[i][0][0]
        p1y = bboxes[i][0][1]
        p2x = bboxes[i][1][0]
        p2y = bboxes[i][1][1]
    # if length is longer than width by a threshold OR
    # if width is longer than length by a threshold
        if (abs((p2y-p1y))/abs((p2x-p1x)) > ratiothresh or abs((p2y-p1y))/abs((p2x-p1x)) < 1/ratiothresh) \
        and abs((p2x - p1x)*(p2y-p1y)) >= areathresh:
            print(abs((p2x - p1x)*(p2y-p1y)))
    # then im.show() the image with a box over it.
            im_copy = 255*np.array(np.copy(im), dtype = np.uint8)
            cv2.rectangle(im_copy, (p1x,p1y), (p2x,p2y), (255,255,255), 2, 1)
            cv2.namedWindow('window',cv2.WINDOW_NORMAL)
            cv2.resizeWindow('window', 600, 600)
            cv2.imshow('window', im_copy)
            # ask user input to see if it's one cell (1) or multiple cells(2)
            print("Is this one cell?")
            print("press 1 for one cell, 2 for multiple cells ")
            k = cv2.waitKey(0)
            if (k == 49):  # 1 is pressed
                cv2.destroyWindow('window')
                continue
            elif (k == 50): # 2 is pressed
            # if it's multiple cells, take all points within that box add it to the list
                delete_list.append(i)
                for p in range(len(bboxes_m)):
                     p1x_m = bboxes_m[p][0][0]
                     p1y_m = bboxes_m[p][0][1]
                     p2x_m = bboxes_m[p][1][0]
                     p2y_m = bboxes_m[p][1][1]
                     print(p1x_m, p1y_m, p2x_m, p2y_m)
                     # ' within the ball park'
                     if p1x_m > p1x-10 and p1y_m > p1y-10 and p2x_m < p2x+10 and p2y_m < p2y+10:
                         bboxes.append(bboxes_m[p])
                cv2.destroyWindow('window')
            elif (k == 113): # q is pressed
                break

    # delete original bouding boxes that were replaced
    for i in range(len(delete_list)):
            del bboxes[np.max(delete_list)]
            delete_list.remove(np.max(delete_list))


        # delete that thing

    print('number of objects detected:' , len(bboxes))
    # cv2.imwrite(output_path, im)


    # export bounding boxes into x y width height form
    boxes_export = {}
    current_frame_boxes = {}
    for index, box in enumerate(bboxes):
        x = box[0][0]
        y = box[0][1]
        width = box[1][0]-box[0][0]
        height = box[1][1] -box[0][1]
        mid_x = (box[0][0]+box[1][0])/2
        mid_y = (box[0][1] + box[1][1])/2
        box_dict = {"x": x, "y": y, "width": width, "height": height, "mid x": mid_x, "mid y": mid_y}
        current_frame_boxes["box " + str(index)] = box_dict

    # write text file containing bounding box information
    # with open(output_picture_directory + '.txt', 'w') as f:
    #     f.write("%s\n" % boxes_export)
    return current_frame_boxes




# takes folder of images OR an array of images, writes bounding box text file + overlaid images.
def detect_frames(min_box_weight, output_directory = None, images_array = None, input_folder = None,  num_frames = None): # folder directory
    # Load images
    if input_folder == True:
        images_array = []
        for filename in os.listdir(input_folder):
            img = cv2.imread(os.path.join(input_folder,filename))
            if img is not None:
                images_array.append(img)
    counter = 0
    boxes_export = {}
    for im in images_array:
        # Detect each frame, index them.
        # output_path = output_directory + '_' + str(counter) + '.png'
        current_frame_boxes  = detect(im, min_box_weight)
        boxes_export["frame " + str(counter)] = current_frame_boxes
        if num_frames is not None:
            if counter == num_frames-1:
                break
        counter += 1

    # # write bounding box frame information
    # with open(output_picture_directory + '.txt', 'w') as f:
    #     f.write("%s\n" % boxes_export)
    return boxes_export
