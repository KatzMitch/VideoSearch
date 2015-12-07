COMP50 Parallel Reverse Video Search Engine

Mitchell Katz, Alex King, Isabelle Sennett, Matthew Yaspan

Sunday, December 6, 2015

Summary:
The Parallel Reverse Video Search Engine takes a video and searches a database
to see whether the query video is a clip from one of the existing videos within
the database.

This product could be used as a reverse search engine in case someone wanted to
find what video a gif came from or as copywright protection, for example.

Algorithm:
The Video Search is based off of a frame-to-frame root mean squared error
function. The RMSE function calculates the difference in brightness between
every pixel in two images. Final results are based off of the mean RMSE score
for two images. We have parallelized the search so that multiple videos can be
searched at once, and multiple chunks of a video can be searched in parallel.

Currently, our program works reliably on identical clips from a video, however
it does have trouble accounting for things like letterboxing, resolution
differences, and transformations (such as flipping across an axis)

Files:
Reverse Search Engine Files:
* framediff.py - Calculates a RMSE difference for 2 PNG images
* chunkCompare.py - Calculates a close matching segment between a query video
  and a comparison video by calculating the mean RMSE score for a segment
* producer.py - Creates chunks to call chunkCompare on
* timeConvert.py - Short module to convert between timestamps and second count

Web Application Files:
* server.py - Code to set up server
* static_website.py - Flask code to interact with website
* stream_vid.py - Code to handle streaming videos
* upload.py - Code to handle user video uploads

Note that this application relies on the MoviePy module, created by GitHub user
Zulko https://github.com/Zulko, which in turn calls the FFMPEG file