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
def comparechunk(queryVid_name, dbVid_name, 
				 db_start, db_end, thresh = 30.0):
    # Create the FFMPEG class variables
    dbVid = FFMPEG_VideoReader(dbVid_name)
    queryVid = FFMPEG_VideoReader(queryVid_name)

    # Skip to the correct frames in the video
    frameQ = queryVid.get_frame(0)
    dbVid.skip_frames(db_start)
    frameD = dbVid.read_frame()

    scores = []

    # Compare the first frame in the query video to every frame in the chunk
    below_thresh = []
    for i in range(db_start, db_end):
        score = frame_rmse(frameQ, frameD)
        # Immediately look at startframes below the threshold
        if frame_rmse(frameQ, frameD) < thresh:
            print "Found a frame below the threshold. Scanning sequence..."
            score = startpoint_compare(queryVid_name, dbVid_name, i)
            if score < thresh and score is not None:
                scores.append(({"Video Name":dbVid_name},
                               {"Timestamp":seconds_to_timestamp(i / dbVid.fps)},
                               {"Frame Number": i},
                               {"Score":score}))
                return scores
            else:
                print "A sequence had a poor score of", score, ". Moving on..."
        frameD = dbVid.read_frame()

    return scores

# Startpoint compare take a frame number worth pursuing, and calculates the
# average rmse value for the duration of the video starting at that point
def startpoint_compare(queryVid_name, dbVid_name, db_start):
	#Create the FFMPEG class variables
	dbVid = FFMPEG_VideoReader(dbVid_name)
	queryVid = FFMPEG_VideoReader(queryVid_name)
	length = queryVid.nframes

	# Skip to the startpoint frame
	dbVid.skip_frames(db_start)
	frameD = dbVid.read_frame()
	frameQ = queryVid.read_frame()

	run_avg = 0

	# Calculate the RMSE for each frame
	for i in range(0, length):
		run_avg += frame_rmse(frameD, frameQ)
		frameQ = queryVid.read_frame()
		frameD = dbVid.read_frame()

	# Return the average RMSE score
	return run_avg / length