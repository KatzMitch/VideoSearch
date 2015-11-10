import multiprocessing as mp
import threading
from pngdiff import png_rmse

running_avg = mp.Value('l')
avg_lock = threading.Lock()

def comparechunk_sequential(orig_vid_name, comp_vid_name, comp_vid_start, comp_vid_end):
	# for frame in comp_vid
		# get png_rmse(0O, xC)
		# if above threshold
			# call startpoint_compare

def comparechunk_multithread(orig_vid_name, comp_vid_name, comp_vid_start, comp_vid_end):
	# for frame in comp_vid
		# spawn process to
			# get png_rmse(0O, xC)
			# if above threshold
				# call startpoint_compare
		# join thread

def startpoint_compare(orig_vid, comp_vid, comp_vid_start):
	# we have a start point worth pursuing
	# processes = []
	# for frame in frames
		# processes.append(target=diff_png, args=[frameO, frameC])
	# for p in processes
		# p.start()
	# for p in processes
		# p.join()
	# write (avg / frametotal) to interpreter

def diff_png(frameA, frameB):
	global running_avg, avg_lock
	score = png_rmse(frameA, frameB)
	avg_lock.acquire()
	running_avg += score
	avg_lock.release()