COMP 50CP Project: The Parallel Reverse Video Search Engine

Mitchell Katz, Alex King, Isabelle Sennett, Matthew Yaspan
Tufts University

Sunday, December 13, 2015

Summary ----------------------------------------------------------------------

The Parallel Reverse Video Search Engine takes a video and searches a database
to see whether the query video is a clip from one of the existing videos within
the database.

Use:
This product could be used as a reverse search engine in case someone wanted to
find what video a gif came from or as copyright protection, for example.

Algorithm:
The Video Search is based off of a frame-to-frame root mean squared error
function. The RMSE function calculates the difference in brightness between
every pixel in two images. Final results are based off of the mean RMSE score
for two images. We have parallelized the search so that multiple videos can be
searched at once, and multiple chunks of a video can be searched in parallel.

Currently, our program works reliably on identical clips from a video, however
it does have trouble accounting for things like letterboxing, resolution
differences, and transformations (such as flipping across an axis)


Files -----------------------------------------------------------------------

src directory:
* framediff.py: Frame difference module. Exports one function, frame_rmse, 
  that returns the root-mean-square error between two NumPy RGB arrays.
* chunk_compare.py: Video chunk comparison module. Exports one function, 
  chunk_compare, that returns a list of matching sequences between the 
  queried video and the specified database video.
* producer.py: Parallel database search module. Exports one function, 
  server_entry, that when given a multiprocessing Queue will return a 
  number of results for the client to expect to be added to the results 
  queue. In effect, this allows the server to call the program with a 
  query video path, watch for live additions to the results queue, and 
  know when no more jobs will be added on.
* timeConvert.py: Short module to convert b/w timestamps and second count
* videoSearch.py: Wrapper module to call producer from the command line
* server.py: Creates a server that maintains the web-based user interface. 
  The server interacts with both the search engine and the client.
* static: the directory containing all CSS and Javascript code as well as 
  the video database
    * video: a subdirectory in static containing the video database
    * query: a subdirectory in static containing the clients uploaded video
    * css: a subdirectory in static containing all css code
    * js: a subdirectory in static containing all javascript code
* templates: the directory containing all HTML code
    * home.html: template for the home page where the user can upload a 
      video and pick a threshold
    * about.html: template for the about page which has a variation of our 
      design story
    * help.html: template for help page outlining how to use videosearch
    * streaming_results.html: template for the results page
    * base.html: a base template that contains element that will be on 
      every page
TestFiles directory: includes some of our files from intermediary stages 
    in our project


How to Run ------------------------------------------------------------------

-Video Search relies on the following modules (which can be installed via PIP):
* MoviePy
* Pillow
* NumPy
* Flask
* SciPy

-First make sure you have the modules outlined above installed and that you 
are in the src directory of our project

There are two ways to run the application:

(1) Through the GUI which is created as a web application using Flask
* To do this run the command python server.py in your console, 
  then open up a web browser and go to the URL http://localhost:9090/

(2) You can also run the program via the console, using the command:

python videoSearch.py inputfile.mp4 path/to/database/ threshold

* Threshold should be a percent value between 0-100.
* With the directory system provided, this is a good sample test 
  (run from src directory)

python videoSearch.py ../static/video/Sail7s.mp4 ../static/video/ 30



Note ------------------------------------------------------------------------

This application relies on the MoviePy module, created by GitHub user
Zulko https://github.com/Zulko, which in turn calls the FFMPEG app. Also many 
of the .js files and .css files are used from elsewhere their documentation is
at the top of their files