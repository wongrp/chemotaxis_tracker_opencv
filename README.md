# chemotaxis_tracker

# Chemotaxis Tracker
Image processor for chemotaxis videos integrated with detector and tracker.

## Packages
Numpy, matplotlib \
Scipy https://www.scipy.org/install.html \
Opencv (both main and contrib modules)  https://pypi.org/project/opencv-python/ \
Pandas: https://pandas.pydata.org/pandas-docs/stable/install.html \
Pandas to excel writer engine:  https://xlsxwriter.readthedocs.io/getting_started.html \

## Tracking the Entire Video

The following parameters may be used as input:

**Background removal / binarizing parameters** \
n: the size of a the sliding window when background is removed. \
b: the neighborhood size at which local intensity threshold is calculated with binarizing the image. The value has to be odd; it centers around the pixel and takes (b-1)/2 pixels in all four directions. \
c: a constant value subtracted from the threshold value during binarizing. \
r: default is 0, signifying background darker than cells. Input 1 if background is lighter than cells. 

**Detector parameters:** \
w: this is the weight value that is multiplied by the average box area A during first frame detection. Any box under the area w*A is deleted to remove noise. 

**Default values:** \
n: 1 \
b: 1001 \
c: 0 \
r: 0 \
w: 0.3 


**Usage example:**

Input raw video directory: pictures_database/video.avi \
Output tracked video: pictures_database/video_tracked.mp4 \
Cells are brighter than background. \
Want neighborhood size to be 501 instead of default 1001 during local thresholding. \
Default parameters otherwise \

```bash
python scripts/run_whole_video.py -b 501 input_folder/video.avi output_folder/video_tracked.mp4 
```

## Tracking Frame by Frame

Takes position of current and last frame to establish instantaneous velocity fields and export as images. Use the same parameter values as above to adjust image processing. 

**Usage example**
The input directory should be the input video. The output directory should be the output folder.

```bash
python scripts/run_frame_by_frame.py input_folder/video.avi output_folder/
```

## Tuning 

If tracking isn’t going well, you can switch to tuning. This works well if there are a lot of videos of the same type, so that a good binarization setting can be obtained on the first video for easy tracking on the rest of the dataset. Tuning mode takes the raw input video and outputs the binarized video as a .mp4 file. 

Run the background remover on a combination of parameters. Input parameter intervals using the following format: [start, stop, stepsize]. 

**Usage example:**

```bash
python scripts/tune.py -n [0,4,4] -b [301, 402,100] -c [0,5,5] -t True pictures_database/video.avi pictures_database/video.mp4 
```
