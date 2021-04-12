import os
from flask import send_from_directory
from flask import Flask, render_template, request
from flask_dropzone import Dropzone
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    RESULT_PATH= os.path.join(basedir,'results'),
    IMAGES_PATH= os.path.join(basedir,'images'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_ALLOWED_FILE_CUSTOM = True,
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*, video/*',
    DROPZONE_DEFAULT_MESSAGE = "",
    DROPZONE_INVALID_FILE_TYPE = "Please upload a photo or video",
    DROPZONE_MAX_FILES = 1,
    DROPZONE_MAX_FILE_EXCEED = "",
    DROPZONE_TIMEOUT = 5*60*1000)

dropzone = Dropzone(app)

# -------------------------------------------- Viewable Pages -------------------------------------------- #

# Home page
@app.route('/',methods=['POST','GET']) 
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('WaterColourConverter.html')

# Result page  
@app.route('/results/')
def resultPage():
     return render_template('index.html')


# -------------------------------------------- Pages for image management -------------------------------------------- #

# hopefully will delete images server side


# Used to return final result image
@app.route('/results/<filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=app.config['RESULT_PATH'], filename=filename)

# Used to return images for webpage
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def displayImage(filename):
    return send_from_directory(directory=app.config['IMAGES_PATH'], filename=filename)

if __name__ == "__main__":
    app.run(debug=True)