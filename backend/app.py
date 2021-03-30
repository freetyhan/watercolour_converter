import os
from flask import Flask, render_template, request
from flask_dropzone import Dropzone
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_ALLOWED_FILE_CUSTOM = True,
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*, video/*',
    #DROPZONE_REDIRECT_VIEW = {{ dropzone.config(redirect_url=url_for('endpoint', foo=bar)) }},
    DROPZONE_INVALID_FILE_TYPE = "Please upload a photo or video",
    DROPZONE_UPLOAD_MULTIPLE = False,
    DROPZONE_TIMEOUT = 5*60*1000)



@app.route('/',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'],f.filename))
    return render_template('index.html')

#@app.route('/results/')
#def result():
#     return "result"

if __name__ == '__main__':
    app.run(debug=True)