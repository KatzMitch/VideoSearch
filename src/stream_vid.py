import os
from flask import Flask, request, render_template, request, Response, stream_with_context
import time

video_dir = 'static/video/'

app = Flask(__name__)

# first view function: will give you a list of files in video_dir the names
# will be hyper links to the results page that plays the video you click on

# The goal will be to have these links streamed as the results come in. 
# I will have to write some java-script to embed a video player that allows the
# live stream of results on a section of the page and a video player as well.
# This will allow the user to be able to play a video while the results are 
# still coming in
@app.route('/')
@app.route('/home')
def index():
    video_files = [f for f in os.listdir(video_dir) if f.endswith('mp4')]
    video_files_number = len(video_files)
    return render_template("index.html",
                        title = 'Home',
                        video_files_number = video_files_number,
                        video_files = video_files)




# THIS CODE DOESNT WORK BELOW--------------------------------------------
# def stream_template(template_name, **context):
#     print 'word'
#     app.update_template_context(context)
#     t = app.jinja_env.get_template(template_name)
#     rv = t.stream(context)
#     #rv.enable_buffering(2)
#     print 'computer'
#     return rv

# @app.route('/', methods=['POST', 'GET'])
# def streamed_index():

#     def generate():
#         #yield 'word'
#         for f in os.listdir(video_dir):
#             #if f.endswith('mp4'):
#             yield f
#             time.sleep(3)
#     video_file= generate()
#     print 'hello'
#     return Response(stream_template('index2.html', video_file=video_file))






#second view function: play files in our video_dir
@app.route('/<filename>')
def video(filename):
    return render_template('play.html',
                        title = filename,
                        video_file = filename)

if __name__ == '__main__':
    app.run(debug = True)

