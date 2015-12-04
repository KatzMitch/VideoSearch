# COMP 50CP: videosearch project
# Modified by Alex King
# Parallel RMSE difference between two RGB image buffers

# To use: import frame_rmse from this module. Call it with two NumPy arrays 
# returned from MoviePy.

# This is a basic and naive image comparison algorithm using the multiprocessing
# library. Multiprocessing allows for a speedup of approximately 75% going from
# one core up to the currently configured 16 cores.

# frame_rmse is the only public function of the module.
# frame_rmse returns the root-mean-square error between two images.
# A value of 0.0 indicates identical images. A maximum value of 255.0 indicates
# completely dissimilar images; for example, a white square and a black square.
# The same image, resized and possibly compressed, should yield a score in the 
# single digits.

import sys
import math
import numpy
import scipy.misc
from PIL import Image
import multiprocessing as mp

NUM_ROWS = 1
NUM_COLS = 1

DENOM    = 32

diff_sum = mp.Value('l', 0) # Store total diff in a long integer

# Python's documentation states that Values default to having Locks inside them,
# but research online indicates they do not work as one would expect. We have 
# to make sure to use the multiprocessing lock and not the threading lock, too.
sum_lock = mp.Lock() 

def _add_to_sum(pixels1, pixels2, w_min, w_max, h_min, h_max):
    """Calculates total pixel difference of an image quadrant"""
    local_sum = 0
    for w in range(w_min, w_max):
        for h in range(h_min, h_max):
            # For each pixel in the images, calculate difference between R G B
            # and store sum locally until the end, when it is safely added to 
            # the global sum. Note: integer casting is key, because NumPY RGB
            # arrays are converted to unsigned 8-bit integers, and the diff math
            # can underflow otherwise
            pixeldiff = 0
            for component in range(3):
                pixeldiff += (int(pixels1[h][w][component]) - 
                              int(pixels2[h][w][component])) ** 2
            local_sum += pixeldiff
    with sum_lock:
        diff_sum.value += local_sum


def frame_rmse(img1, img2):
    """Returns root-mean-square error between two NumPy image buffers"""
    global diff_sum
    diff_sum = mp.Value('l', 0) # Reset value on each call, else it persists
    width1, height1 = len(img1[0]), len(img1)
    width2, height2 = len(img2[0]), len(img2)
    section_width = width1 / NUM_COLS
    section_height = height1 / NUM_ROWS

    # Resize larger image if necessary using the fast nearest-neighbor algorithm
    if abs(width2 - width1) > 1 or abs(height2 - height1) > 1:

        # img1 is larger
        if width1 > width2:
            img1 = scipy.misc.imresize(img1, (width2, height2), 'nearest', None)
            width1, height1 = width2, height2
            
        # img2 is larger
        else:
            img2 = scipy.misc.imresize(img2, (width1, height1), 'nearest', None)
            width2, height2 = width1, height1

    # Downsize each image for faster processing
    img1 = scipy.misc.imresize(img1, (height1 / DENOM, width1 / DENOM), 
                               'nearest', None)
    width1, height1 = width1 / DENOM, height1 / DENOM

    img2 = scipy.misc.imresize(img2, (height2 / DENOM, width2 / DENOM), 
                               'nearest', None)
    width2, height2 = width2 / DENOM, height2 / DENOM

    # if more sections are requested than pixels
    if section_width == 0:
        section_width = 1
    if section_height == 0:
        section_height = 1

    processes = []

    height_min = width_min = 0
    while height_min < height1:
        while width_min < width1:
            
            height_max = height_min + section_height
            width_max  = width_min  + section_width
            
            # If the next iteration will spill over the end of the image,
            # include that region in this section
            if height_max + section_height > height1:
                height_max = height1
            if width_max + section_width > width1:
                width_max = width1

            processes.append(mp.Process(target = _add_to_sum, 
                                        args = [img1, img2,
                                                width_min,
                                                width_max,
                                                height_min, 
                                                height_max]))

            width_min = width_max
        height_min = height_max
        width_min = 0

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    divided = diff_sum.value / (3 * width1 * height1)
    E = math.sqrt(divided)
    return E
