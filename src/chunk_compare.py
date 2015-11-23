from __future__ import division

import multiprocessing as mp
import numpy
from framediff import frame_rmse
from time_convert import timestamp_to_seconds, seconds_to_timestamp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from math import floor
from PIL import Image
import ctypes

"""
This function takes the names of the files to compare, and where in the
comparison file to begin checking from. Threshold is a user determined value
that they chose qualitatively, and the GUI turned into a quantitative number
"""
def comparechunk(orig_vid_name, comp_vid_name, comp_vid_start, comp_vid_end, thresh):
	# Create the FFMPEG class variables
	comp_vid = FFMPEG_VideoReader(comp_vid_name)
	orig_vid = FFMPEG_VideoReader(orig_vid_name)

	# Hopefully this invariant will be tested sooner, make sure the two videos
	# have equal FPS
	if comp_vid.fps != orig_vid.fps:
		print "OOPS!"
		exit(1)

	# Calculate the starting and end frame numbers
	comp_start = int(floor(timestamp_to_seconds(comp_vid_start) * comp_vid.fps))
	comp_end = int(floor(timestamp_to_seconds(comp_vid_end) * comp_vid.fps))

	# Skip to the correct frames in the video
	frameO = orig_vid.get_frame(0)
	comp_vid.skip_frames(comp_start)
	frameC = comp_vid.read_frame()

	# Compare the first frame in the query video to every frame in the chunk
	below_thresh = []
	for i in range(comp_start, comp_end):
		score = frame_rmse(frameO, frameC)
		# Save startframes below the threshold
		if frame_rmse(frameO, frameC) < thresh:
			below_thresh.append(i)
		frameC = comp_vid.read_frame()

	# Calculate the scores for the startpoints worth pursuing and store them in
	# a list of lists
	scores = []
	for startpoint in below_thresh:
		score = startpoint_compare(orig_vid_name, comp_vid_name, startpoint)
		if score < thresh:
			scores.append((orig_vid_name, startpoint, score))

	return scores

"""
Startpoint compare take a frame number worth pursuing, and calculates the
average rmse value for the duration of the video starting at that point
"""
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