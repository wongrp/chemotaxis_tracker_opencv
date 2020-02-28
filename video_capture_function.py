import cv2
import numpy as np

# capture the video and output the captured object.
def capture_video(input_path):
    # Create a video capture object to read videos
    captured_video = cv2.VideoCapture(input_path)

    # Read first frame
    success, initial_frame = captured_video.read()
    frame_width = initial_frame.shape[1]
    frame_height = initial_frame.shape[0]
    # quit if unable to read the video file
    if not success:
      print('Failed to read video')
      sys.exit(1)
    return captured_video, initial_frame, frame_width, frame_height, success

# takes video, writes frames into a path.
def write_images(input_path, output_path):
    # read video and create list
    captured_video, initial_frame, frame_width, frame_height, success = capture_video(input_path)
    cv2.imwrite(output_path + '_0' + '.png', initial_frame)
    counter = 1
    while success:
        success,image = captured_video.read()
        if type(image) is not None and 0 not in np.shape(image):
            cv2.imwrite(output_path + '_' + str(counter) + '.png', image)
        counter += 1

# takes video, stores frames into list
def store_images(input_path, output_path):
    # read video and create list
    im_list = []
    captured_video, initial_frame, frame_width, frame_height, success = capture_video(input_path)
    im_list.append(initial_frame)
    counter = 1
    while success:
        success,image = captured_video.read()
        if type(image) is not None and 0 not in np.shape(image):
            im_list.append(image)
        counter += 1

    return im_list

def write_video(input_array, output_path):
        frame_width = np.shape(input_array)[2]
        frame_height = np.shape(input_array)[1]
        # define video writer
        video_writer = cv2.VideoWriter(output_path,cv2.VideoWriter_fourcc(*'mp4v'), 15, (frame_width,frame_height), isColor = False) # isColor setting is important
        for frame in input_array:
            video_writer.write(np.uint8(frame))
        # release video writer object
        video_writer.release()


# for taking instantaneous velocity
def split_video_array(input_array):
    # take current frame and the next frame
    # making sure current frame is not the last frame
    split_vid = []
    for index,frame in enumerate(input_array):
        if index == len(input_array)-2:
            break
        frame_next = input_array[index+1]
        mini_vid = [frame, frame_next]
        split_vid.append(mini_vid)

    return split_vid
