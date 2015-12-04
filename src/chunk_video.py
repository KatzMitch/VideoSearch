from __future__ import division

import multiprocessing as mp
import numpy
import threading
import os
import math
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from chunk_compare import comparechunk

FPS = 30

scores = {}


# A job gives a FFMPEG object
class Job:
  def __init__(self, queryVideo, dbVideo, start, finish, chunksProcessed):
  	self.queryVideo = queryVideo
  	self.dbVideo = dbVideo
  	self.start = start
  	self.finish = finish
  	self.chunksProcessedSwitch = chunksProcessed

# Lightswitch: initialized given a number (the number of chunks for a given 
# video) and holds a semaphore until all of the chunks have been processed,
# and when that occurs a thread waiting on the semaphore can proceed to reap
# the scores of the video's chunks
class LightSwitch:
	def __init__(self, targetNum):
		self.target = targetNum
		self.finished = 0
		self.countLock = mp.Manager().Lock()
		self.finishedLock = mp.Manager().Semaphore(0)

	def wait():
		self.finishedLock.acquire()

	def finish():
		self.countLock.acquire()
		self.finished += 1
		self.countLock.release()
		if self.finished == self.target:
			self.finishedLock.release()



# spawns a chunkVideo process for each video in the database. passes
# a path to the query video and database video to the chunkVideo function
def search(queryVideoPath, testFilesPath):
	processes = []
	jobQueue = mp.Manager().Queue()
	videoLibrary = os.listdir(testFilesPath)
	#queryVideo = FFMPEG_VideoReader(queryVideoPath)
	for video in videoLibrary:
		processes.append(mp.Process(target=chunkVideo,
	    						    args=[queryVideoPath,
	    						          testFilesPath + '/' + video,
	    						          jobQueue]))
		#chunkVideo(queryVideoPath, testFilesPath + "/" + video, jobQueue)
	for process in processes:
		process.start()
    
	for process in processes:
		process.join()

def printJobs(queryVideo, dbVideo, start, finish):
	print "queryVideo is" + queryVideo
	print "dbVideo is" + dbVideo
	print "startpoint is" + str(start)
	print "endpoint is" + str(finish)

def processJobs(jobQueue, processLock):
	processLock.acquire()
	consumers = []
	while not jobQueue.empty():
		try:
			job = jobQueue.get(False)
			consumer = mp.Process(target=comparechunk,
							      args=[job.queryVideo,
							      		job.dbVideo,
							      		job.start,
							      		job.finish])
			consumer.start()
			consumers.append(consumer)
		except:
			break

	processLock.release()
	for consumer in consumers:
		consumer.join()


def chunkVideo(queryVideoPath, dbVideoPath, jobQueue):
	queryVideo = FFMPEG_VideoReader(queryVideoPath)
	dbVideo = FFMPEG_VideoReader(dbVideoPath)

	finalChunkSize = queryVideo.nframes
	numChunks = int(math.ceil(dbVideo.nframes / float(queryVideo.nframes)))
	chunksProcessed = LightSwitch(numChunks)
	startingChunkSize = dbVideo.nframes / numChunks

	processLock = mp.Lock()
	processLock.acquire()
	processJob = mp.Process(target=processJobs, args=[jobQueue,
													  processLock])
	processJob.start()

	for chunk in range(numChunks):
		qV = queryVideoPath
		dV = dbVideoPath
		startPoint = chunk * startingChunkSize
		endPoint = (chunk + 1) * startingChunkSize
		if chunk != 0:
			startPoint -= (finalChunkSize - startingChunkSize) / 2
		else:
			endPoint += (finalChunkSize - startingChunkSize) / 2

		if chunk != (numChunks - 1):
			endPoint += (finalChunkSize - startingChunkSize) / 2
		else:
			startPoint -= (finalChunkSize - startingChunkSize) / 2

		if numChunks == 1:
			startPoint = 0
			endPoint = dbVideo.nframes - 1

		job = Job(qV, dV, int(startPoint), int(endPoint), chunksProcessed)
		jobQueue.put(job)

		if chunk == 0:
			processLock.release()

	processJob.join()


