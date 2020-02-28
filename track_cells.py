from select_tracker import *
from locate_objects import *
import numpy as np
import cv2
import sys, getopt, os
print(cv2.__version__)

# given an array of images, tracks cells.
def track_cells(new_roi_frequency, total_boxes, binary_video, original_video, output_path = None, tracker_type = 'CSRT'):
    if output_path is not None:
        print('outputting to: ', output_path)
    # preprocess
    # binary_video = np.uint8(binary_video)

    # process the total_boxes dictionary into a format for the tracker.
    f0 = total_boxes["frame 0"]
    first_frame_list = []
    for box in f0:
        box = (f0[box]['x'], f0[box]['y'], f0[box]['width'], f0[box]['height'])
        first_frame_list.append(box)


    # draw first frame onto the video array.
    initial_frame = np.uint8(binary_video[0])
    assert(np.sum(initial_frame != 0))
    frame_width = initial_frame.shape[1]
    frame_height = initial_frame.shape[0]


    # for index, new_box in enumerate(first_frame_list):
    #     # access box elements and draw
    #     p1 = (int(new_box[0]), int(new_box[1])) # point 1 of new box
    #     p2 = (int(new_box[0] + new_box[2]), int(new_box[1] + new_box[3])) # point 2 of box
    #

    # initialize multitracker and track the first frame.
    tracker = cv2.MultiTracker_create() # create
    for bounding_box in first_frame_list:
        tracker.add(tracker_selector(tracker_type), initial_frame, bounding_box)

    # update multitracker
    counter = 0
    frame_counter = 0

    for frame in binary_video[1:]:
        # read the frame
        frame_counter += 1
        print('frame = ', frame_counter)

        # update boxes location
        read_success, boxes = tracker.update(np.uint8(frame))

        # update the imported boxes dictionary
        current_frame_boxes = {}
        for index, box in enumerate(boxes):
            box_dict = {"x": box[0], "y": box[1], "width": box[2], "height": box[3], "mid x": box[0]+box[2]/2, "mid y": box[1]+box[3]/2}
            current_frame_boxes["box " + str(index)] = box_dict
        total_boxes["frame " + str(frame_counter)] = current_frame_boxes

        # select new ROI's for new cells.
        counter += 1
        if counter == new_roi_frequency:
            new_boxes, new_colors = annotate_new(frame)
            for bounding_box in new_boxes:
                tracker.add(tracker_selector(tracker_type), frame, bounding_box)
                np.append(boxes, bounding_box)
            for color in new_colors:
                colors.append(color)
            counter = 0

        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
            break


    # draw boxes on gray scale
    if output_path is not None:
        video_writer = cv2.VideoWriter(output_path,cv2.VideoWriter_fourcc(*'mp4v'), 15, (frame_width,frame_height), isColor = True) # isColor setting is important

    for frame_index, frame in enumerate(original_video):
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
            video_writer.write(frame)

    # release video writer object
    if output_path is not None:
        video_writer.release()

    return total_boxes
