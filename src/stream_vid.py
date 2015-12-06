import os
from flask import Flask, request, render_template, request, Response, stream_with_context
import time

video_dir = 'static/video/'

app = Flask(__name__)
#Both index and streamed index will give you a list of files in video_dir with the names
# being hyper links that play the video you click on in a new window
        #THE DIFFERENCE: 
        #    index creates a list of video files in the directory and 
        #       then renders the template
        #    streamed_index post the hyper-links as it goes though the video directory
        #          (to see this uncomment out the time.sleep line)


# I will have to write some java-script to embed a video player that allows the
# live stream of results on a section of the page and a video player as well.
# This will allow the user to be able to play a video while the results are 
# still coming in
#@app.route('/')
@app.route('/home')
def index():
    video_files = [f for f in os.listdir(video_dir) if f.endswith('mp4')]
    video_files_number = len(video_files)
    return render_template("index.html",
                        title = 'Home',
                        video_files_number = video_files_number,
                        video_files = video_files)


@app.route('/', methods=['POST', 'GET'])
def streamed_index():
    video_file = generate_vids()
    return Response(stream_template('index2.html', video_files=video_file))


def stream_template(template_name, **context):
    app.update_template_context(context)
    template = app.jinja_env.get_template(template_name)
    print "t", template 
    rv = template.stream(context)
    return rv

def generate_vids():
    for f in os.listdir(video_dir):
        if f.endswith('mp4'):
            yield f
            time.sleep(0.8)


#play files in our video_dir
@app.route('/<filename>')
def video(filename):
    return render_template('play.html',
                        title = filename,
                        video_file = filename)

if __name__ == '__main__':
    app.run(debug = True, port=9090)

