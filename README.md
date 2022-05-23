# Watercolour Converter Website
## How to run the website locally
1. If you do not have it already, download [pip](https://pip.pypa.io/en/stable/installing/) and 64-bit [python](https://www.python.org/downloads/release/python-395/)
2. Check this project’s backend directory and make sure that the following folders and files exist (other folders may exist but they are not as important)
    - uploads
    - results
    - images
    - templates
    - app.py
    - model.pkl
3. Run the following commands in order
    - cd backend
    - py -3 -m venv venv
    - pip install Flask
    - pip install flask-dropzone
    - pip3 install torch==1.8.1+cpu torchvision==0.9.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
    - python app.py
4. Once you run the last command a link will likely show up (it does at least in VS code and cmd). Follow it and the website should show up. 
![site](https://user-images.githubusercontent.com/70041708/118384868-c5b02080-b5be-11eb-8407-6e20b6327e82.jpg)

**NOTE:** If the images are not loading on the webpage, change line 133 and 138 in /backend/app.py from 

    133: return send_from_directory(app.config['RESULT_PATH'], filename=os.listdir(app.config['RESULT_PATH'])[0])

    138: return send_from_directory(directory=app.config['IMAGES_PATH'], filename=filename)
to

    133: return send_from_directory(app.config['RESULT_PATH'], path=os.listdir(app.config['RESULT_PATH'])[0])

    138: return send_from_directory(directory=app.config['IMAGES_PATH'], path=filename)

This project was done as part of 2020W CPEN291 final project.\n
Machine Learning model developer: Harjot Grewal, Adrienne Chu\n
Backend developer: Adriana Castro\n
Frontend developer: Han Cho\n
