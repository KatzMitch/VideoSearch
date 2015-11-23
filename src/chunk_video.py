from __future__ import division

import multiprocessing as mp
import numpy
from framediff import frame_rmse
from time_convert import timestamp_to_seconds
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from math import floor
from PIL import Image
import Queue
import ctypes
import os

FPS = 30

scores = {}
jobQueue = mp.Queue()


# A job gives a FFMPEG object
class Job:
  def __init__(self, queryVideo, dbVideo, start, finish, chunksProcessed):
  	self.queryVideo = queryVideo
  	self.dbVideo = dbVideo
  	self.start = start
  	self.finish = finish
  	self.dbVideo.pos = start
  	self.pos = self.dbVideo.pos
  	self.chunksProcessedSwitch = chunksProcessedSwitch

# Lightswitch: initialized given a number (the number of chunks for a given 
# video) and holds a semaphore until all of the chunks have been processed,
# and when that occurs a thread waiting on the semaphore can proceed to reap
# the scores of the video's chunks
class LightSwitch:
	def __init__(self, targetNum):
		self.target = targetNum
		self.finished = 0
		self.countLock = threading.Lock()
		self.finishedLock = threading.Semaphore(0)

	def wait():
		self.finishedLock.acquire()

	def finish():
		self.countLock.acquire()
		self.finished += 1
		self.countLock.release()
		if self.finished == self.target:
			self.finishedLock.release()


# chunk db video according to our specifications. for each chunk,
# spawn off a job that contains two unique open FFMPEG_VideoReaders
# to a query and database video, with the database video starting
# at the start of the chunk.
def chunkVideo(queryVideoPath, dbVideoPath):
	global jobQueue
	
	queryVideo = FFMPEG_VideoReader(queryVideoPath)
	dbVideo = FFMPEG_VideoReader(dbVideoPath)

	finalChunkSize = queryVideo.nframes
	numChunks = math.ceil(dbVideo.nframes / queryVideo.nframes)
    chunksProcessed = LightSwitch(numChunks)
	startingChunkSize = dbVideo.frames / numChunks

	for chunk in range(numChunks):
		qV = FFMPEG_VideoReader(queryVideoPath)
		dV = FFMPEG_VideoReader(dbVideoPath)
		startPoint = chunk * startingChunkSize
		endPoint = (chunk + 1) * startingChunkSize
		if chunk != 0:
			startPoint -= (finalChunkSize - startingChunkSize) / 2
		if chunk != (numChunks - 1):
			endPoint += (finalChunkSize - startingChunkSize) / 2
	    
	    jobQueue.put(Job(qV, dV, startPoint, endPoint, chunksProcessed)))

    chunksProcessed.wait()
    #  code to reap score




# spawns a chunkVideo process for each video in the database. passes
# a path to the query video and database video to the chunkVideo function
def prepareToCompare(queryVideoPath, testFilesPath):
	processes = []

	videoLibrary = os.listdir(testFilesPath)
	#queryVideo = FFMPEG_VideoReader(queryVideoPath)
	for video in videoLibrary:
	   #dbVideo = FFMPEG_VideoReader(video)
	    processes.append(mp.Process(target=chunkVideo,
	    						    args=[queryVideoPath,
	    						          testFilesPath + '/' + video])

	for process in processes:
		processes.start()

	for process in process:
		processes.join()

