Notes about this branch:

The main modification here is to immediately break out of the chunk comparison
if any comparison average falls below the threshold. This parallelizes well! Two examples:
  - 5s query, 30s db: 1:20 single threaded, 0:40 7-process
  - 0.8s query, 30s db: 2:23 single threaded, 1:30 32-process

However, this required me to dial back the parallelization of frame_diff. In
fact, frame_diff works best when single-threaded, with a denominator of 32 to
seriously downsize the images. A multi-threaded solution (32*16 = 512
concurrent processes) took 1:47, which is a demonstration that a large amount
of processes can exist all at the same time.

For reference, a denominator of 4 in the 32-consumer system led to a runtime of 
12:17. Denominator is the single biggest optimization that we have, but it
also is a sort of cheat.