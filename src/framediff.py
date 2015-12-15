"""
COMP 50CP: videosearch project
Modified by Alex King
Parallel RMSE difference between two RGB image buffers

To use: import frame_rmse from this module. Call it with two NumPy arrays 
returned from MoviePy.

This is a basic and naive image comparison algorithm using the multiprocessing
library. Multiprocessing allows for a speedup of approximately 75% going from
one core up to the currently configured 16 cores.

frame_rmse is the only public function of the module.
frame_rmse returns the root-mean-square error between two images.
A value of 0.0 indicates identical images. A maximum value of 255.0 indicates
completely dissimilar images; for example, a white square and a black square.
The same image, resized and possibly compressed, should yield a score in the 
single digits.
"""

import sys
import math
import numpy
import scipy.misc
from PIL import Image
import multiprocessing as mp

NUM_ROWS = 1
NUM_COLS = 1

DENOM    = 32

diffSum = mp.Value('l', 0) # Store total diff in a long integer

# Python's documentation states that Values default to having Locks inside them,
# but research online indicates they do not work as one would expect. We have 
# to make sure to use the multiprocessing lock and not the threading lock, too.
sumLock = mp.Lock() 

def addToSum(pixels1, pixels2, wMin, wMax, hMin, hMax):
    """Calculates total pixel difference of an image quadrant"""
    localSum = 0
    for w in range(wMin, wMax):
        for h in range(hMin, hMax):
            # For each pixel in the images, calculate difference between R G B
            # and store sum locally until the end, when it is safely added to 
            # the global sum. Note: integer casting is key, because NumPY RGB
            # arrays are converted to unsigned 8-bit integers, and the diff math
            # can underflow otherwise
            pixeldiff = 0
            for component in range(3):
                pixeldiff += (int(pixels1[h][w][component]) - 
                              int(pixels2[h][w][component])) ** 2
            localSum += pixeldiff
    with sumLock:
        diffSum.value += localSum


def frame_rmse(img1, img2):
    """Returns root-mean-square error between two NumPy image buffers"""
    global diffSum
    diffSum = mp.Value('l', 0) # Reset value on each call, else it persists
    width1, height1 = len(img1[0]), len(img1)
    width2, height2 = len(img2[0]), len(img2)
    sectionWidth = width1 / NUM_COLS
    sectionHeight = height1 / NUM_ROWS

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
    if sectionWidth == 0:
        sectionWidth = 1
    if sectionHeight == 0:
        sectionHeight = 1

    processes = []

    heightMin = widthMin = 0
    while heightMin < height1:
        while widthMin < width1:
            
            heightMax = heightMin + sectionHeight
            widthMax  = widthMin  + sectionWidth
            
            # If the next iteration will spill over the end of the image,
            # include that region in this section
            if heightMax + sectionHeight > height1:
                heightMax = height1
            if widthMax + sectionWidth > width1:
                widthMax = width1

            processes.append(mp.Process(target = addToSum, 
                                        args = [img1, img2,
                                                widthMin,
                                                widthMax,
                                                heightMin, 
                                                heightMax]))

            widthMin = widthMax
        heightMin = heightMax
        widthMin = 0

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    divided = diffSum.value / (3 * width1 * height1)
    E = math.sqrt(divided)
    return E
