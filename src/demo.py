#coding=utf-8
import os
import time
import cPickle
import datetime
import logging
import flask
import werkzeug
import optparse
import tornado.wsgi
import tornado.httpserver
import numpy as np
import cStringIO as StringIO
import urllib
import cv2
import xhq
import species_list
from flask import Flask
from flask import render_template, redirect,url_for
from flask import request,session
import json

app = flask.Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.before_request
def before_action():
    print request.path
    if request.path.find('.ico')==-1:
        if not request.path=='/login':
            if not 'username' in session:
                session['newurl']=request.path
                return redirect(url_for('login'))

@app.route('/<path>')
def jsonReader(path):
    path=path.encode("unicode-escape")
    base_dir=os.path.dirname(__file__)+"/json"
    f=open(os.path.join(base_dir,path))
    ret=json.load(f)
    return flask.jsonify(ret)

@app.route('/')
def index():
    username=session['username']
    xsq=species_list.sq(username)
    return flask.render_template('index.html', list=xsq.select(),username=session['username'])

@app.route('/add',methods=['GET'])
def add():
    username=session['username']
    xsq=species_list.sq(username)
    xargs = flask.request.args
    if xargs.get('count','')=='':
        count=0
    else:
        count=int(xargs.get('count',''))
    if count>0:
        for i in range(count):
            keywd='name'+str(i)
            name=xargs.get(keywd,'')
            if not name=='':
                xsq.insert(name,'11')
    return flask.render_template('index.html', list=xsq.select(),username=session['username'])

@app.route('/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if not request.form['username']=='':
            session['username'] = request.form['username']
            if 'newurl' in session:
                newurl = session['newurl']
                session.pop('newurl', None)
                return redirect(newurl)
            else:
                return redirect('/')
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/classify_upload', methods=['POST'])
def classify_upload():
    try:
        # We will save the file to disk for possible data collection.
        imagefile = flask.request.files['imagefile']
        filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
            werkzeug.secure_filename(imagefile.filename)
        filename = os.path.join('.', filename_)
        imagefile.save(filename)
        logging.info('Saving to %s.', filename)
        image = cv2.imread(filename)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return flask.render_template(
           'xhq.json', has_result=True,
          result=(False, 'Cannot open uploaded image.')
    	)

    result = app.clf.classify_image(image)

    return flask.render_template(
        'xhq.json', has_result=True, result=result,
        imagesrc=filename
    )

class ImagenetClassifier(object):

    def __init__(self):
        logging.info('Loading classify and associated files...')

    def classify_image(self, image):
        try:
            starttime = time.time()

            best_result=xhq.xclass(image)
            
	    endtime = time.time()
            logging.info('best result: %s', str(best_result))

            return (True,best_result, '%.3f' % (endtime - starttime))

        except Exception as err:
            logging.info('Classification error: %s', err)
            return (False, 'Something went wrong when classifying the '
                           'image. Maybe try another one?')


def start_tornado(app, port=5000):
    http_server = tornado.httpserver.HTTPServer(
        tornado.wsgi.WSGIContainer(app))
    http_server.listen(port)
    print("Tornado server starting on port {}".format(port))
    tornado.ioloop.IOLoop.instance().start()


def start_from_terminal(app):
    """
    Parse command line options and start the server.
    """
    parser = optparse.OptionParser()
    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)
    parser.add_option(
        '-p', '--port',
        help="which port to serve content on",
        type='int', default=5000)
    parser.add_option(
        '-g', '--gpu',
        help="use gpu mode",
        action='store_true', default=False)

    opts, args = parser.parse_args()

    # Initialize classifier + warm start by forward for allocation
    app.clf = ImagenetClassifier()

    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        start_tornado(app, opts.port)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    start_from_terminal(app)