
# Render HTML templates and access data sent by POST using
# the request object from flask. Redirect and url_for will
# be used to redirect the user once the upload is done and
# send_from_directory or play.html (depending on view) will 
# help us to send/show on the browser the file that the user 
# just uploaded


import sys
sys.path.insert(0, './src')
import producer
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'static/query'
app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('format.html')

# Route that will process the file upload
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


# 2 VIEW OPTIONS about how to show the video in browser once uploaded
        
        # # VIEW 1
        # # Redirect the user to the uploaded_file route, which
        # # will basically show on the browser the uploaded file
        # # VIEW: video takes up the browser space
        # return redirect(url_for('uploaded_file',
        #                          filename=filename))

        # Redirect the user to the video route, which
        # will play the uploaded video
        # VIEW: specs in the play.html file
        return redirect(url_for('video',
                                filename=filename))
    # else:
    # return page_not_found(404) <-----------------------------------error handler


# ROOT FOR: VEIW 1
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ROOT FOR: VEIW 2
@app.route('/<filename>')
def video(filename):
    return render_template('play.html',
                        title = filename,
                        video_file = filename)

# need to actually code this this is an on-line example of an error handler and 
# I need to make this work for our program along with a few other error handlers

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()