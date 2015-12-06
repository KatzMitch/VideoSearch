"""
producer.py
COMP 50CP: videosearch project
Modified by Alex King and Mitchell Katz
Entrypoint function for videosearch program

To use: run "python producer.py input.mp4 /path/to/database/ threshold"

This is the producer/interpreter module of our program. It is responsible for
surveying the input video and database videos, creating jobs with proper 
length, and telling each consumer to process jobs until all are complete.
"""

import sys
import multiprocessing as mp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from chunkCompare import comparechunk
from pprint import pprint
import glob
import os

globalJobs = mp.Value("l", 0)
jobLock = mp.Lock()

class Consumer(mp.Process):
	"""
	A consumer is a process that takes jobs off of a job queue, completes them,
	and adds its answer to the result queue. In our case, each job is a list of
	arguments to comparechunk.
	"""
	def __init__(self, taskQueue, resultQueue):
		mp.Process.__init__(self)
		self.taskQueue = taskQueue
		self.resultQueue = resultQueue

	def run(self):
		procName = self.name
		while True:
			nextTask = self.taskQueue.get()
			if nextTask is None:
				print '%s: Exiting' % procName
				break
			print '%s: %s' % (procName, nextTask)
			answer = comparechunk(nextTask[0], nextTask[1], 
								  nextTask[2], nextTask[3],
								  nextTask[4])
			self.resultQueue.put(answer)
		return


def percentToThresh(percent):
	"""
	Translate a percentage threshold (passed by client) into a parameter within the
	range 10-60
	"""
	return (percent/3) + 10


def startSearch(queryPath, dbPath, threshold, jobQueue, resultsQueue):
	"""
	Generates jobs for consumer threads, starts each consumer, waits for all to
	complete.
	"""
	global globalJobs
	queryVid  = FFMPEG_VideoReader(queryPath)
	dbVid     = FFMPEG_VideoReader(dbPath)
	boundaries = []

	# Both videos must have equal frame rates
	if queryVid.fps != dbVid.fps:
		print "FPSs must match!"
		return

	# Make ranges that are the length of the input video
	width = queryVid.nframes
	startFrame = 0

	if width > dbVid.nframes:
		width = dbVid.nframes

	boundaries.append([startFrame, startFrame + width])

	while startFrame < (dbVid.nframes - width):
		startFrame += queryVid.nframes
		boundaries.append([startFrame, startFrame + width])

	numConsumers = 16 # This can be easily modified
	numJobs      = len(boundaries)

	print "Threshold:", threshold
	print 'Creating %d consumers' % numConsumers
	consumers = [ Consumer(jobQueue, resultsQueue)
				  for i in xrange(numConsumers) ]

	# Prepare the workers to consume jobs
	for worker in consumers:
		worker.start()

	# Now we need to make a job queue. A job must have all of the arguments for 
	# comparechunk.
	for item in boundaries:
		jobQueue.put([queryPath, dbPath, item[0], item[1], threshold])

	# This technique forces each thread to eventually consume a job that tells
	# them to stop, allowing us to join safely afterwards.
	for i in range(numConsumers):
		jobQueue.put(None)

	print "Nones have been put on the queue for video", dbPath
	
	jobLock.acquire()
	globalJobs.value += numJobs
	jobLock.release()

	print "Jobs have been incremeneted for video", dbPath
	print "Returning should happen right now"

	return True

def serverEntry(queryPath, dbPath, threshold, resultsQueue):
	"""
	This is the 'main' function for the sever, parses the input and calls a new
	process running startSearch on each file in the database
	"""
	jobQueue = mp.Queue()
	if os.path.isdir(dbPath):
		files = glob.glob(dbPath+"*.mp4")
		print files
		processes = []
		for aFile in files:
			print "testing:", queryPath, aFile, threshold
			processes.append(mp.Process(target=startSearch,
										  args=[queryPath, aFile,
												threshold, jobQueue,
												resultsQueue]))
		for process in processes:
			process.start()
		for process in processes:
			process.join(1)
	else:
		startSearch(queryPath, dbPath, threshold, jobQueue, resultsQueue)

	jobLock.acquire()
	returnVal = globalJobs.value
	jobLock.release()
	return returnVal

def main():
	"""
	Parses command line arguments for a query video and database video.
	threshold is a number from 0-100 which we translate into a threshold value
	"""
	if len(sys.argv) != 4:
		print "Usage: python producer.py input.mp4 source.mp4 threshold"
		exit(1)

	queryPath = sys.argv[1]
	dbPath    = sys.argv[2]
	threshold = percentToThresh(int(sys.argv[3]))
	jobQueue = mp.Queue()
	resultsQueue = mp.Queue()

	if os.path.isdir(dbPath):
		files = glob.glob(dbPath+"*.mp4")
		print files
		processes = []
		for aFile in files:
			print "testing:", queryPath, aFile, threshold
			processes.append(mp.Process(target=startSearch,
										  args=[queryPath, aFile, threshold,
												jobQueue, resultsQueue]))
		for process in processes:
			process.start()
		for process in processes:
			process.join(1)
	else:
		startSearch(queryPath, dbPath, threshold, jobQueue, resultsQueue)

	print "Total number of jobs is", globalJobs.value
	print
	print
	print
	print "*** FINAL RESULT ***"

	print "Okay, now the total number of jobs is", globalJobs.value
	jobLock.acquire()
	while globalJobs.value:
		result = resultsQueue.get()
		if len(result) is not 0:
			pprint(result)
		globalJobs.value -= 1
	jobLock.release()

if __name__ == '__main__':
	main()