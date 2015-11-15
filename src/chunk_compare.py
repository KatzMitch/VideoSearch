from __future__ import division

import multiprocessing as mp
import numpy
from framediff import frame_rmse
from time_convert import timestamp_to_seconds
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from math import floor
from PIL import Image
import ctypes

FPS = 30
run_avg = 0.0

def comparechunk(orig_vid_name, comp_vid_name, comp_vid_start, comp_vid_end):
	return
	# for frame in comp_vid
		# get png_rmse(0O, xC)
		# if above threshold
			# call startpoint_compare

def startpoint_compare(orig_vid_name, comp_vid_name, comp_vid_start):
	comp_vid = FFMPEG_VideoReader(comp_vid_name)
	orig_vid = FFMPEG_VideoReader(orig_vid_name)
	comp_vid_start = timestamp_to_seconds(comp_vid_start)

	## Hopefully this invariant will be tested sooner
	if comp_vid.fps != orig_vid.fps:
		print "OOPS!"
		exit(1)

	fileinfo = ffmpeg_parse_infos(orig_vid_name)
	length = int(floor(fileinfo['duration'] * fileinfo['video_fps']))

	frameC = comp_vid.get_frame(comp_vid_start * fileinfo['video_fps'])
	frameO = orig_vid.read_frame()
	for i in range(comp_vid_start, length + comp_vid_start):
		calc_rmse(frameC, frameO)
		frameO = orig_vid.read_frame()
		frameC = comp_vid.read_frame()

	print "SCORE: ", run_avg / length
	return run_avg / length

def calc_rmse(frameC, frameO):
	global run_avg
	score = frame_rmse(frameC, frameO)
	run_avg += score
	print score