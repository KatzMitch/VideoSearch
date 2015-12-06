import datetime
import time

"""Converts a timestamp of the form H:M:S to the total number of seconds
thanks to stackoverflow post
http://stackoverflow.com/questions/10663720/converting-a-time-string-to-seconds-in-python
and user Burhan Kahlid for this code"""
def timestampToSeconds(timestamp):
    x = time.strptime(timestamp, '%H:%M:%S')
    delta = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec)
    return int(delta.total_seconds())

def secondsToTimestamp(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return ("%02d:%02d:%02d" % (h, m, s))