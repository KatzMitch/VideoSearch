# COMP 50CP: videosearch project
# Modified by Alex King
# Parallel RMSE difference between two PNGs

# This is a basic and naive image comparison algorithm using the multiprocessing
# library. Multiprocessing allows for a speedup of approximately 75% going from
# one core up to the currently configured 16 cores.

# png_rmse is the only public function of this module; main() is just there as a
# test for now. png_rmse returns the root-mean-square error between two images.
# A value of 0.0 indicates identical images. A maximum value of 255.0 indicates
# completely dissimilar images; for example, a white square and a black square.
# The same image, resized and possibly compressed, should yield a score in the 
# single digits.

from PIL import Image
import sys
import math
import threading
import multiprocessing as mp

# In testing, 16 threads led to the best performance
NUM_ROWS = 4
NUM_COLS = 4

diffSum = mp.Value('l') # Store total diff in a long integer
sumSock = threading.Lock()

def addToSum(pixels1, pixels2, wMin, wMax, hMin, hMax):
    """Calculates total pixel difference of an image quadrant"""
    global diffSum
    localSum = 0
    for w in range(wMin, wMax):
        for h in range(hMin, hMax):
            # For each pixel in the images, calculate difference between R G B
            # and store sum locally until the end, when it is safely added to 
            # the global sum
            pixeldiff = 0
            for component in range(3):
                pixeldiff += (pixels1[w, h][component] - 
                              pixels2[w, h][component]) ** 2
            localSum += pixeldiff
    with sumLock:
        diffSum.value += localSum
            
def png_rmse(img1, img2):
    """Returns root-mean-square error between two image files"""
    image1 = Image.open(img1)
    image2 = Image.open(img2)
    width1, height1 = image1.size
    width2, height2 = image2.size
    sectionWidth = width1 / NUM_COLS
    sectionHeight = height1 / NUM_ROWS
    if abs(width2 - width1) > 1 or abs(height2 - height1) > 1:
        # Change the larger image's size. NEAREST is ~40% faster than ANTIALIAS,
        # but it introduces noise
        size = width1, height1
        image2 = image2.resize(size, Image.NEAREST)
        width2, height2 = image2.size

    pixels1 = image1.load()
    pixels2 = image2.load()

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

            processes.append(mp.Process(target = addTo_Sum, 
                                        args = [pixels1, pixels2,
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

def main():
    """Parses command line arguments and passes information to image 
    processing"""
    numArgs = len(sys.argv)
    if numArgs != 3:
        sys.stderr.write("Usage: python pngdiff.py input1.png input2.png\n")
        sys.exit(1)
    print png_rmse(sys.argv[1], sys.argv[2])

    return 0

if __name__ == '__main__':
    main()