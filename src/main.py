import multiprocessing as mp
from chunk_video import chunkVideo

NUM_PROCS = 10

def main_func(queryVideoPath, dbVideoPath):
	processes = []
	lock = mp.Condition()
	processes.append(mp.Process(target=chunkVideo, args=[queryVideoPath, dbVideoPath, lock]))
	for i in range(NUM_PROCS):
		processes.append(mp.Process(target=consumer, args=[]))

	for process in processes:
		process.start()

	lock.wait()

	for process in processes:
		process.join()