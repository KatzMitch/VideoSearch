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
jobQueue = Queue.Queue()

class Job:
  def __init__(self, video, start, finish, chunksProcessed):
  	self.video = video
  	self.start = start
  	self.finish = finish
  	self.video.pos = start
  	self.pos = self.video.pos
  	self.chunksProcessedSwitch = chunksProcessedSwitch

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


def chunkVideo(queryVideo, dbVideo):
	global jobQueue
	chunkThreads = []

	finalChunkSize = queryVideo.nframes
	numChunks = math.ceil(dbVideo.nframes / queryVideo.nframes)
    chunksProcessed = LightSwitch(numChunks)
	startingChunkSize = dbVideo.frames / numChunks

	for chunk in range(numChunks):
		startPoint = chunk * startingChunkSize
		endPoint = (chunk + 1) * startingChunkSize
		if chunk != 0:
			startPoint -= (finalChunkSize - startingChunkSize) / 2
		if chunk != (numChunks - 1):
			endPoint += (finalChunkSize - startingChunkSize) / 2
	    
	    jobQueue.put(Job(dbVideo, startPoint, endPoint, chunksProcessed)))

    chunksProcessed.wait()
    # (weighted?) average of scores


def prepareToCompare(queryVideoPath, testFilesPath):
	threads = []

	videoLibrary = os.listdir(testFilesPath)
	queryVideo = FFMPEG_VideoReader(queryVideoPath)
	for video in videoLibrary:
	    dbVideo = FFMPEG_VideoReader(video)
	    threads.append(threading.Thread(target=chunkVideo,
	    							    args=[queryVideo, dbVideo]))

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()


