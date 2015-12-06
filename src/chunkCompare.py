"""
COMP50CP Final Project- Video Search
chunk_compare.py
File written by Mitchell Katz
"""

from __future__ import division

from framediff import frame_rmse
from timeConvert import secondsToTimestamp
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from multiprocessing import Semaphore
from pprint import pprint

def comparechunk(queryVidName, dbVidName, dbStart, dbEnd, thresh):
    """
    This function takes the names of the files to compare, and where in the
    comparison file to begin checking from. Threshold is a user determined value
    that they chose qualitatively, and the GUI turned into a quantitative number
    Args: path to query video, path to comparison video, start frame number, 
    endframe number, callback to process results, RMSE threshold (a number from 
    0-255, realistically should be between 10-50)
    """
    # Create the FFMPEG class variables
    dbVid = FFMPEG_VideoReader(dbVidName)
    queryVid = FFMPEG_VideoReader(queryVidName)

    # Skip to the correct frames in the video
    frameQ = queryVid.get_frame(0)
    dbVid.skip_frames(dbStart)
    frameD = dbVid.read_frame()

    scores = []

    # Compare the first frame in the query video to every frame in the chunk
    belowThresh = []
    for i in range(dbStart, dbEnd):
        score = frame_rmse(frameQ, frameD)
        # Immediately look at startframes below the threshold
        if frame_rmse(frameQ, frameD) < thresh:
            print "Found a frame below the threshold. Scanning sequence..."
            score = startpointCompare(queryVidName, dbVidName, i)
            if score < thresh and score is not None:
                scores.append(({"Video Name":dbVidName},
                               {"Timestamp":secondsToTimestamp(i / dbVid.fps)},
                               {"Frame Number": i},
                               {"Score":score}))
                return scores
            else:
                print "A sequence had a poor score of", score, ". Moving on..."
        frameD = dbVid.read_frame()

    return scores

def startpointCompare(queryVidName, dbVidName, dbStart):
    """
    Startpoint compare take a frame number worth pursuing, and calculates the
    average rmse value for the duration of the video starting at that point
    """
    #Create the FFMPEG class variables
    dbVid = FFMPEG_VideoReader(dbVidName)
    queryVid = FFMPEG_VideoReader(queryVidName)
    length = queryVid.nframes

    # Skip to the startpoint frame
    dbVid.skip_frames(dbStart)
    frameD = dbVid.read_frame()
    frameQ = queryVid.read_frame()

    runAvg = 0

    # Calculate the RMSE for each frame
    for i in xrange(0, length):
        runAvg += frame_rmse(frameD, frameQ)
        frameQ = queryVid.read_frame()
        frameD = dbVid.read_frame()

    # Return the average RMSE score
    return runAvg / length