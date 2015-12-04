# COMP50CP Final Project- Video Search
# chunk_compare.py
# File written by Mitchell Katz

from __future__ import division

from framediff import frame_rmse
from time_convert import seconds_to_timestamp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from multiprocessing import Semaphore
from pprint import pprint

# This function takes the names of the files to compare, and where in the
# comparison file to begin checking from. Threshold is a user determined value
# that they chose qualitatively, and the GUI turned into a quantitative number
# Args: path to query video, path to comparison video, start frame number, 
# endframe number, callback to process results, RMSE threshold (a number from 
# 0-255, realistically should be between 10-50)
def comparechunk(orig_vid_name, comp_vid_name, 
				 comp_start, comp_end, thresh = 30.0):
    # Create the FFMPEG class variables
    comp_vid = FFMPEG_VideoReader(comp_vid_name)
    orig_vid = FFMPEG_VideoReader(orig_vid_name)

    # Skip to the correct frames in the video
    frameO = orig_vid.get_frame(0)
    comp_vid.skip_frames(comp_start)
    frameC = comp_vid.read_frame()

    scores = []

    # Compare the first frame in the query video to every frame in the chunk
    below_thresh = []
    for i in range(comp_start, comp_end):
        score = frame_rmse(frameO, frameC)
        # Immediately look at startframes below the threshold
        if frame_rmse(frameO, frameC) < thresh:
            print "Found a frame below the threshold. Scanning sequence..."
            score = startpoint_compare(orig_vid_name, comp_vid_name, i)
            if score < thresh and score is not None:
                scores.append(({"Video Name":orig_vid_name},
                               {"Timestamp":seconds_to_timestamp(i / orig_vid.fps)},
                               {"Frame Number": i},
                               {"Score":score}))
                return scores
            else:
                print "A sequence had a poor score of", score, ". Moving on..."
        frameC = comp_vid.read_frame()

    return scores

# Startpoint compare take a frame number worth pursuing, and calculates the
# average rmse value for the duration of the video starting at that point
def startpoint_compare(orig_vid_name, comp_vid_name, comp_vid_start):
	#Create the FFMPEG class variables
	comp_vid = FFMPEG_VideoReader(comp_vid_name)
	orig_vid = FFMPEG_VideoReader(orig_vid_name)
	length = orig_vid.nframes

	# Skip to the startpoint frame
	comp_vid.skip_frames(comp_vid_start)
	frameC = comp_vid.read_frame()
	frameO = orig_vid.read_frame()

	run_avg = 0

	# Calculate the RMSE for each frame
	for i in range(0, length):
		run_avg += frame_rmse(frameC, frameO)
		frameO = orig_vid.read_frame()
		frameC = comp_vid.read_frame()

	# Return the average RMSE score
	return run_avg / length