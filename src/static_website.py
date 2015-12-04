from flask import Flask, url_for, render_template, request, Response
import time

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('format.html')


def stream_template(template_name, **context):
    #print 'word'
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    #rv.enable_buffering(2)
    #print 'computer'
    return rv

@app.route('/results2/', methods=['POST', 'GET'])
def results2():
    def generate(word):
        for target in ['hello', 'world', 'hi']: #this is where the iterator will go
            yield str(word.find(target))+'\n'
            time.sleep(1)
    words = generate(request.form['word'])
    #print 'hello'
    return Response(stream_template('results2.html', words=words))


if __name__ == '__main__':
    app.run(debug = True)