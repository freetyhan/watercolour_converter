import os
import logging
import pickle
import torch, torch.nn as nn, torch.optim as optim
import torchvision.transforms as xforms, torchvision.datasets, torchvision.utils
from PIL import Image
import PIL
from torchvision.utils import save_image
from torchvision import datasets, models, transforms
from flask import send_from_directory
from flask import Flask, render_template, request, redirect
from flask_dropzone import Dropzone

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        # got rid of vgg layers, changed kernal size to 4x4
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 64, 4, 1, 1),
            nn.LeakyReLU(),
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 128, 4, 1, 1),
            nn.LeakyReLU(),
            nn.BatchNorm2d(128),
            nn.Conv2d(128, 256, 4, 1, 1),
            nn.LeakyReLU(),
            nn.BatchNorm2d(256)
        )

        # 9 resnet blocks
        self.resnet_layers = nn.Sequential(
            BasicBlock(256, 256),
            BasicBlock(256, 256),
            BasicBlock(256, 256),
            BasicBlock(256, 256),
            BasicBlock(256, 256),
            BasicBlock(256, 256),
        )

        # the 3 transposed convolution layers
        self.tconv_layers = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 1, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(),

            nn.ConvTranspose2d(128, 64, 4, 1, 1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(),

            nn.ConvTranspose2d(64, 3, 4, 1, 1),
            nn.LeakyReLU(),
            nn.Tanh()
        )

        def init_layer(layer):
            if type(layer).__name__[:4] == 'Conv':
                nn.init.xavier_uniform_(layer.weight)
            elif layer.__class__.__name__[:9] == 'BatchNorm':
                nn.init.normal_(layer.weight, 1.0, 0.02)
                nn.init.constant_(layer.bias, 0.0)
            elif type(layer).__name__[:5] == "Basic":
                nn.init.xavier_uniform_(layer.conv1.weight)
                nn.init.xavier_uniform_(layer.conv2.weight)
                


        self.tconv_layers.apply(init_layer)
        self.resnet_layers.apply(init_layer)
        self.conv_layers.apply(init_layer)

        
    def forward(self, samples):
        # pass sample through all the layers
        out = self.conv_layers(samples)
        out = self.resnet_layers(out)
        out = self.tconv_layers(out)
        return out

model = pickle.load(open(os.path.join(basedir,'model.pkl'), 'rb'))

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
    DROPZONE_TIMEOUT = 5*60*1000,
    SEND_FILE_MAX_AGE_DEFAULT = 1)

dropzone = Dropzone(app)

# -------------------------------------------- Viewable Pages -------------------------------------------- #

# Home page
@app.route('/',methods=['POST','GET']) 
def upload():
    if request.method == 'POST':
        deletefile()
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], "upload.jpg"))
    return render_template('WaterColourConverter.html')

# Result page  
@app.route('/results/')
def resultPage():
    device = 'cpu'
    # transforms needed to pass the image through the model. Can change 128, 128 to another number to resize as needed
    
    tr = xform_none = torchvision.transforms.Compose([torchvision.transforms.ToTensor(), torchvision.transforms.Resize((400,400)), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    MEAN = torch.tensor([0.5, 0.5, 0.5])
    STD = torch.tensor([0.5, 0.5, 0.5])
    img = tr(Image.open(os.path.join(app.config['UPLOADED_PATH'], "upload.jpg"))).unsqueeze(0).to(device)
    # gen is the tensor with the transformed image
    
    gen = model(img).cpu() * STD[:, None, None] + MEAN[:, None, None]
    save_image(gen, os.path.join(app.config['RESULT_PATH'], "result.jpg"))
    return render_template('index.html')


# -------------------------------------------- Pages for image management ------------------------------ #

# Used to return final result image
@app.route('/resultImage/', methods=['GET', 'POST'])
def download():
    return send_from_directory(app.config['RESULT_PATH'], os.listdir(app.config['RESULT_PATH'])[0])

# Used to return images for webpage so frontend can display any image stored on the server
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def displayImage(filename):
    return send_from_directory(directory=app.config['IMAGES_PATH'], filename=filename)
        
# Delete all uploaded and result files and reroutes to main page
@app.route('/deleteUploads', methods=['GET', 'POST'])
def deletefile():

    for filename in os.listdir(app.config['UPLOADED_PATH']):
        file_path = os.path.join(app.config['UPLOADED_PATH'], filename)
        os.remove(file_path)
    
    for filename in os.listdir(app.config['RESULT_PATH']):
        file_path = os.path.join(app.config['RESULT_PATH'], filename)
        os.remove(file_path)

    return redirect("/")

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == "__main__":
    app.run(debug=True)