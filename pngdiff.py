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

diff_sum = mp.Value('l') # Store total diff in a long integer
sum_lock = threading.Lock()

def _add_to_sum(pixels1, pixels2, w_min, w_max, h_min, h_max):
    """Calculates total pixel difference of an image quadrant"""
    global diff_sum
    local_sum = 0
    for w in range(w_min, w_max):
        for h in range(h_min, h_max):
            # For each pixel in the images, calculate difference between R G B
            # and store sum locally until the end, when it is safely added to 
            # the global sum
            pixeldiff = 0
            for component in range(3):
                pixeldiff += (pixels1[w, h][component] - 
                              pixels2[w, h][component]) ** 2
            local_sum += pixeldiff
    with sum_lock:
        diff_sum.value += local_sum
            
def png_rmse(img1, img2):
    """Returns root-mean-square error between two image files"""
    image1 = Image.open(img1)
    image2 = Image.open(img2)
    width1, height1 = image1.size
    width2, height2 = image2.size
    section_width = width1 / NUM_COLS
    section_height = height1 / NUM_ROWS
    if abs(width2 - width1) > 1 or abs(height2 - height1) > 1:
        # Change the larger image's size. NEAREST is ~40% faster than ANTIALIAS,
        # but it introduces noise
        size = width1, height1
        image2 = image2.resize(size, Image.NEAREST)
        width2, height2 = image2.size

    pixels1 = image1.load()
    pixels2 = image2.load()

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
                                        args = [pixels1, pixels2,
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

def main():
    """Parses command line arguments and passes information to image 
    processing"""
    num_args = len(sys.argv)
    if num_args != 3:
        sys.stderr.write("Usage: python pngdiff.py input1.png input2.png\n")
        sys.exit(1)
    print png_rmse(sys.argv[1], sys.argv[2])

    return 0

if __name__ == '__main__':
    main()