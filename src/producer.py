# producer.py
# COMP 50CP: videosearch project
# Modified by Alex King
# Entrypoint function for videosearch program

# To use: run "python producer.py input.mp4 database.mp4"

# This is the producer/interpreter module of our program. It is responsible for
# surveying the input video and database videos, creating jobs with proper 
# length, and telling each consumer to process jobs until all are complete.

import sys
import multiprocessing as mp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from chunk_compare import comparechunk
from pprint import pprint
from random import shuffle
import glob
import os

class Consumer(mp.Process):
    """
    A consumer is a process that takes jobs off of a job queue, completes them,
    and adds its answer to the result queue. In our case, each job is a list of
    arguments to comparechunk.
    """
    def __init__(self, task_queue, result_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                print '%s: Exiting' % proc_name
                # self.task_queue.task_done()
                break
            print '%s taking job: %s' % (proc_name, next_task)
            answer = comparechunk(next_task[0], next_task[1], 
                                  next_task[2], next_task[3],
                                  next_task[4])
            # self.task_queue.task_done()
            self.result_queue.put(answer)
        return

"""
Translate a percentage threshold (passed by client) into a parameter within the
range 10-60
"""
def percent_to_thresh(percent):
    return (percent / 2) + 10

"""
Generates jobs for consumer threads, starts each consumer, waits for all to complete.
"""
def start_search(queryPath, dbPath, threshold):
    queryVid  = FFMPEG_VideoReader(queryPath)
    dbVid     = FFMPEG_VideoReader(dbPath)
    jobQueue      = mp.Queue()
    resultsQueue  = mp.Queue()
    boundaries = []

    # Both videos must have equal frame rates
    if queryVid.fps != dbVid.fps:
        print "FPSs must match!"
        return

    # Make ranges that are twice the length of the input video, overlapping by
    # length of input video,
    # e.g., input = 50, db = 250; boundaries = 0-100, 50-150, 100-200, 150-250
    width = queryVid.nframes
    startFrame = 0

    if width > dbVid.nframes:
        width = dbVid.nframes

    boundaries.append([startFrame, startFrame + width])

    while startFrame < (dbVid.nframes - width):
        startFrame += queryVid.nframes
<<<<<<< HEAD
        endFrame = startFrame + queryVid.nframes
        boundaries.append([startFrame, endFrame])
=======
        boundaries.append([startFrame, startFrame + width])

    # shuffle(boundaries)
    print boundaries
>>>>>>> bf6818917d9cfb93090f6c990b39cebff1780fb2

    num_consumers = 32 # This can be easily modified
    num_jobs      = len(boundaries)

    print "Threshold:", threshold
    print 'Creating %d consumers' % num_consumers
    consumers = [ Consumer(jobQueue, resultsQueue)
                  for i in xrange(num_consumers) ]

    # Prepare the workers to consume jobs
    for worker in consumers:
        worker.start()

    # Now we need to make a job queue. A job must have all of the arguments for 
    # comparechunk.
    for item in boundaries:
        jobQueue.put([queryPath, dbPath, item[0], item[1], threshold])

    # This technique forces each thread to eventually consume a job that tells
    # them to stop, allowing us to join safely afterwards.
    for i in range(num_consumers):
        jobQueue.put(None)
    
    # Print resultsQueue as things come in
    while num_jobs:
        result = resultsQueue.get()
        if len(result) is not 0:
            print 'Found match below specified threshold:',
            pprint(result)
        num_jobs -= 1

    return 0

def server_entry(queryPath, dbPath, threshold):
<<<<<<< HEAD
	if os.path.isdir(dbPath):
		files = glob.glob(dbPath+"*.mp4")
		print files
		pprocesses = []
		for aFile in files:
			print "testing:", queryPath, aFile, threshold
			processes.append(mp.Process(target=start_search,
                                          args=[queryPath, aFile, threshold]))
			#start_search(queryPath, aFile, threshold)
		for process in processes:
			process.start()
		for process in processes:
			process.join()
	else:
		start_search(queryPath, dbPath, threshold)

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
	threshold = percent_to_thresh(int(sys.argv[3]))

	if os.path.isdir(dbPath):
		files = glob.glob(dbPath+"*.mp4")
		print files
		processes = []
		for aFile in files:
			print "testing:", queryPath, aFile, threshold
			processes.append(mp.Process(target=start_search,
                                          args=[queryPath, aFile, threshold]))
		for process in processes:
			process.start()
		for process in processes:
			process.join()
	else:
		start_search(queryPath, dbPath, threshold)
=======
    if os.path.isdir(dbPath):
        files = glob.glob(dbPath+"*.mp4")
        print files
        for aFile in files:
            print "testing:", queryPath, aFile, threshold
            start_search(queryPath, aFile, threshold)
    else:
        start_search(queryPath, dbPath, threshold)

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
    threshold = percent_to_thresh(int(sys.argv[3]))
    # threshold = int(sys.argv[3])

    if os.path.isdir(dbPath):
        files = glob.glob(dbPath+"*.mp4")
        print files
        for aFile in files:
            print "testing:", queryPath, aFile, threshold
            start_search(queryPath, aFile, threshold)
    else:
        start_search(queryPath, dbPath, threshold)
>>>>>>> bf6818917d9cfb93090f6c990b39cebff1780fb2

if __name__ == '__main__':
    main()