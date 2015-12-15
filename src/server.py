"""
COMP50CP Final Project- Video Search
server.py

Created by Isabelle Sennett

To use: (1) run "python server.py" 
        (2) go to a web browser type in this URL http://localhost:9090/

Creates a server that maintains the web-based user interface. The server 
interacts with both the search engine and the client. It processes requests 
from the client such as rerouting to the about or help page while also handling
 data that the client posts to the server. The server starts the search engine 
"""

# Uses the following html templates:
#       home.html
#       streaming_results.html
#       about.html
#       help.html

import sys
sys.path.insert(0, './src')
from producer import serverEntry
import multiprocessing as mp
import os
from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context
from werkzeug import secure_filename

app = Flask(__name__)

# The file the user uploads will get saved here so we can access it
app.config['UPLOAD_FOLDER'] = 'static/query'
app.config['DATABASE'] = 'static/video'
app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])


#Home page:
#     User can: upload a video and select a threshold, 
#               they also have access to the about and help pages 
@app.route('/')
def index():
    return render_template('home.html')

# Purpose: process the file upload and then redirect the user to the results page
@app.route('/upload/', methods=['POST', 'GET'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    threshold = request.form['threshold']

    return redirect(url_for('streamResults', 
                                threshold=threshold, 
                                queryFilename = filename))


# PURPOSE: For a given file, return whether it's an allowed type or not
# NOTE: our test database doesn't have anything besides mp4 files so this isn't
#       really necessary but if this project were to be developed further this  
#       can be used to check whether the the file is an allowed type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



# Start the search process and then handle live streaming the results
@app.route('/results/<threshold>/<queryFilename>/', methods=['POST', 'GET'])
def streamResults(threshold, queryFilename):
    
    resultsQueue = mp.Queue()
    quaryPath = 'static/query' + '/' + queryFilename
    database = app.config['DATABASE'] + '/'

    # Start the search process: serverEntry function is in the producer file,
    # we do not know how many matches there will be so we use the number of jobs
    numJobs = serverEntry(quaryPath, database, int(threshold), resultsQueue)

    # live stream the results
    result = generate_results(numJobs, resultsQueue)
    return Response(stream_template('streaming_results.html', 
                                        video_files = result))

# Helper function for StreamResults
def stream_template(template_name, **context):
    app.update_template_context(context)
    template = app.jinja_env.get_template(template_name)
    print "t", template 
    rv = template.stream(context)
    return rv


# Gets results off of the results queue as they get added
def generate_results(numJobs, resultsQueue):
    while numJobs > 0:
        result = resultsQueue.get(True)
        if result != []:
            print "Result is", result
            video = os.path.basename(result[0]["Video Name"])
            timestamp = result[0]["Timestamp"]
            frame_number = result[0]["Frame Number"]
            score = result[0]["Score"]
            yield [video, timestamp, frame_number, score]
        numJobs = numJobs - 1

# redirects user to about page
@app.route('/about/', methods=['POST', 'GET'])
def about():
    return render_template('about.html')

# redirects user to help page
@app.route('/help/', methods=['POST', 'GET'])
def help():
    return render_template('help.html')


# Runs the application on a local server. If the debug flag is set 
# the server will automatically reload for code changes and show a debugger in 
# case an exception happened.
if __name__ == '__main__':
    app.run(port=9090)
    # app.run(debug = True, port=9090)