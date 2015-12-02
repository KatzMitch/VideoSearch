# producer.py
# COMP 50CP: videosearch project
# Modified by Alex King
# Entrypoint function for videosearch program

# To use: run "python entrypoint.py input.mp4 database.mp4"

# This is the producer/interpreter module of our program. It is responsible for
# surveying the input video and database videos, creating jobs with proper 
# length, and telling each consumer to process jobs until all are complete.

import sys
import multiprocessing as mp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from chunk_compare import comparechunk

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
                self.task_queue.task_done()
                break
            print '%s: %s' % (proc_name, next_task)
            answer = comparechunk(next_task[0], next_task[1], 
                                  next_task[2], next_task[3],
                                  next_task[4], next_task[5])
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return

def main():
    """
    Parses command line arguments for a query video and database video. Needs to
    be modified to take in a *directory* of database videos instead. Generates
    jobs for consumer threads, starts each consumer, waits for all to complete.
    """
    if len(sys.argv) != 3:
        print "Usage: python producer.py input.mp4 source.mp4"
        exit(1)

    queryPath = sys.argv[1]
    dbPath    = sys.argv[2]
    queryVid = FFMPEG_VideoReader(queryPath)
    dbVid    = FFMPEG_VideoReader(dbPath)
    jobQueue      = mp.JoinableQueue()
    resultsQueue  = mp.Queue()
    boundaries = []

    # Make ranges that are twice the length of the input video, overlapping by
    # length of input video,
    # e.g., input = 50, db = 250; boundaries = 0-100, 50-150, 100-200, 150-250
    width = 2 * queryVid.nframes
    startFrame = 0
    endFrame = width
    boundaries.append([startFrame, endFrame])

    while endFrame < dbVid.nframes:
        startFrame += queryVid.nframes
        endFrame = startFrame + width
        boundaries.append([startFrame, endFrame])

    num_consumers = len(boundaries) # This can be easily modified
    num_jobs      = len(boundaries)

    print 'Creating %d consumers' % num_consumers
    consumers = [ Consumer(jobQueue, resultsQueue)
                  for i in xrange(num_consumers) ]

    # Prepare the workers to consume jobs
    for worker in consumers:
        worker.start()

    # Now we need to make a job queue. A job must have all of the arguments for 
    # comparechunk.
    for item in boundaries:
        jobQueue.put([queryPath, dbPath, item[0], item[1], None, 30])

    # This technique forces each thread to eventually consume a job that tells
    # them to stop, allowing us to join safely afterwards.
    for i in boundaries:
        jobQueue.put(None)

    # Wait for all of the tasks to finish
    jobQueue.join()
    
    # Print resultsQueue
    while num_jobs:
        result = resultsQueue.get()
        print 'Result:', result
        num_jobs -= 1

    return 0

if __name__ == '__main__':
    main()