# COMP 50CP: videosearch project
# Modified by Alex King
# Example of MoviePy API for using ffmpeg to access frames of videos

from __future__ import division

import subprocess as sp
import numpy
from PIL import Image

from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader

FRAMES_PER_SECOND = 30 # This could be defined globally, or something else

# Initialize an instance of this class with the video you want to access
video = FFMPEG_VideoReader('chrg.mp4')

for x in range(15):

    # The read_frame() method returns a plain 2D RGB array of the next frame
    image1 = video.read_frame()

    # This example wants to show every 10th frame, so here we read one frame
    # and skip the next nine
    video.skip_frames(9)

    # For debugging, and to make sure we're extracting what we think we're 
    # extracting, we can easily save the plain 2D RGB array to a file
    newimage = Image.new('RGB', (len(image1[0]), len(image1)))  # type, size
    newimage.putdata([tuple(p) for row in image1 for p in row])
    newimage.save(str(x) + "test.png")  # takes type from filename extension

for y in range(5):

    # The get_frame(time) method is likely going to be key for us. It expects
    # seconds and returns the frame at that point in time. Dividing seconds by
    # video frames per second, being sure to use non-integer division, this
    # gives the identical 0th-4th frames from the video as I got when running
    # ffmpeg normally on the command line.

    img = video.get_frame(y / FRAMES_PER_SECOND)
    newimage = Image.new('RGB', (len(img[0]), len(img)))
    newimage.putdata([tuple(p) for row in img for p in row])
    newimage.save(str(y) + "timetest.png")