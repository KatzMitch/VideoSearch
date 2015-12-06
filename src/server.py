# webserver
# URL     http://localhost:1010/


import sys
sys.path.insert(0, './src')
from producer import serverEntry
import multiprocessing as mp
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
from werkzeug import secure_filename

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'static/query'
app.config['DATABASE'] = 'static/video'
app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])


#Home page:
#     User can: upload a video 
@app.route('/')
def index():
    return render_template('home.html')

# Route that will process the file upload and then render the search options page
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

        return render_template('search_options.html', search_video = filename)
    # else:
    # return page_not_found(404) <-----------------------------------------------error handler

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# start the search process
@app.route('/search/<search_video>/', methods=['POST', 'GET'])
def search(search_video):
    resultsQueue = mp.Queue()
    # we do not know how many matches there will be so we use the number of jobs
    quaryPath = 'static/query' + '/' + search_video
    database = app.config['DATABASE']
    threshold = request.form['threshold']
    numJobs = serverEntry(quaryPath, database, threshold, resultsQueue)
    return numJobs



# NEED TO BE MODIFIED FOR THIS
# @app.route('/', methods=['POST', 'GET'])
# def streamed_index():
#     video_file = generate_vids()
#     return Response(stream_template('index2.html', video_files=video_file))


# def stream_template(template_name, **context):
#     app.update_template_context(context)
#     template = app.jinja_env.get_template(template_name)
#     print "t", template 
#     rv = template.stream(context)
#     return rv

# def generate_vids():
#     for f in os.listdir(video_dir):
#         if f.endswith('mp4'):
#             yield f
#             time.sleep(0.8)






# # ROOT FOR: VEIW 2
# @app.route('/<filename>')
# def video(filename):
#     return render_template('play.html',
#                         title = filename,
#                         video_file = filename)




# need to actually code this this is an on-line example of an error handler and 
# I need to make this work for our program along with a few other error handlers

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug = True, port=9090)