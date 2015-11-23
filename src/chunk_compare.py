from __future__ import division

import multiprocessing as mp
import numpy
from framediff import frame_rmse
from time_convert import timestamp_to_seconds, seconds_to_timestamp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from math import floor
from PIL import Image
import ctypes

FPS = 30

mutex = mp.Semaphore(1)
ovid_name = ""
cvid_name = ""

def map_func(startpoint):
	startpoint_compare(ovid_name, cvid_name, startpoint)

def comparechunk(orig_vid_name, comp_vid_name, comp_vid_start, comp_vid_end):
	# for frame in comp_vid
	comp_vid = FFMPEG_VideoReader(comp_vid_name)
	orig_vid = FFMPEG_VideoReader(orig_vid_name)
	frameO = orig_vid.get_frame(0)

	comp_start = int(floor(timestamp_to_seconds(comp_vid_start) * comp_vid.fps))
	comp_end = int(floor(timestamp_to_seconds(comp_vid_end) * comp_vid.fps))

	frameC = comp_vid.get_frame(comp_start)
	below_thresh = []
	for i in range(comp_start, comp_end):
		score = frame_rmse(frameO, frameC)
		print "Score for: ", i, " is: ", score
		if frame_rmse(frameO, frameC) < thresh:
			below_thresh.append(i)
		frameC = comp_vid.read_frame()

	pool = mp.Pool(10)
	mutex.acquire()
	ovid_name = orig_vid_name
	cvid_name = comp_vid_name
	ret = pool.map(map_func, below_thresh)
	mutex.release()
	pool.close()
	pool.join()

	print ret

def score_callback(score):
	print "SCORE: ", score

def startpoint_compare(orig_vid_name, comp_vid_name, comp_vid_start):
	comp_vid = FFMPEG_VideoReader(comp_vid_name)
	orig_vid = FFMPEG_VideoReader(orig_vid_name)

	## Hopefully this invariant will be tested sooner
	if comp_vid.fps != orig_vid.fps:
		print "OOPS!"
		exit(1)

	fileinfo = ffmpeg_parse_infos(orig_vid_name)
	length = int(floor(fileinfo['duration'] * fileinfo['video_fps']))

	frameC = comp_vid.get_frame(comp_vid_start * fileinfo['video_fps'])
	comp_vid.read_frame() # Sync up each video. NOTE: temporary solution; there
						  # should be a "seek" method we can use
	frameO = orig_vid.read_frame()
	run_avg = 0
	for i in range(0, length):
		run_avg += frame_rmse(frameC, frameO)
		frameO = orig_vid.read_frame()
		frameC = comp_vid.read_frame()

	return run_avg / length