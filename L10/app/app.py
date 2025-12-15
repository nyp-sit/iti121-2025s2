#------------------------------------------------------------------------------
# To run your web server, open up your terminal / command prompt
# and type:
#    cd <path to this file>
#    python practical-03c-deployment.py
#
#------------------------------------------------------------------------------

from flask import Flask, flash, request, redirect, url_for, Response
import requests
import os
import json
import torch
import numpy as np

# Configure our application 
#
model_dir = 'model'

# Initialize our Flask app.
# NOTE: Flask is used to host our app on a web server, so that
# we can call its functions over HTTP/HTTPS.
#
#app = Flask(__name__)
labels = ["JUMPING", "JUMPING_JACKS", "BOXING", "WAVING_2HANDS", "WAVING_1HAND", "CLAPPING_HANDS"]

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

if torch.cuda.is_available():
    device = 'cuda'
elif torch.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'
    
model_name = "activity_model_ts.pt"
model_path = os.path.join(model_dir, model_name)
model = torch.jit.load(model_path, map_location=device)

model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    print('receiving keypoints')
    json_data = request.get_json()
    x_str = json_data['instances']
    X = torch.tensor(np.array(x_str), dtype=torch.float32).to(device)
    logits = model(X)
    pred = torch.softmax(logits, dim=1).detach().cpu().numpy()
    # print(pred[0])
    index = np.argmax(pred[0])
    if pred[0][index] < 0.97:
        activity = ""
    else:
        # print(pred[0][index])
        activity = labels[index]
    return Response(activity)


#------------------------------------------------------------------------------
# This starts our web server.
# Although we are running this on our local machine,
# this can technically be hosted on any VM server in the cloud!
#------------------------------------------------------------------------------
if __name__ == "__main__":
    # Only for debugging while developing

    app.run(host="0.0.0.0", debug=True, port=80)


