"""
videoSearch.py is a short wrapper for the console entry point to the producer
module.
File written by Mitchell Katz

"""

import producer
import sys

def percentToThresh(percent):
    """
    Translate a percentage threshold (passed by client) into a parameter within
    the range 10-60
    """
    return (percent/3) + 10


if __name__ == "__main__":
    """
    Calls the console entry function in the producer module and parses command
    line input
    """
    if len(sys.argv) != 4:
        print "Usage: python videoSearch.py input.mp4 /path/to/database threshold"
        exit(1)

    queryPath = sys.argv[1]
    dbPath    = sys.argv[2]
    threshold = percentToThresh(int(sys.argv[3]))
    producer.consoleEntry(queryPath, dbPath, threshold)