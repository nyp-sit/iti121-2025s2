# Annotate using Label Studio and Grounding Dino

In this guide, we will only describe how to run the Label Studio and the ML backend (Grounding Dino) as docker containers. 
Please refer to `https://labelstud.io/guide/install.html' for more install options. 

## Pre-requisites

Download the docker-compose.yml file to a chosen directory which you will use to store data from Label Studio and the ML backend.  Change to that directory. 

## Label Studio

Start the Label Studio docker container first by doing the following: 

```bash
docker-compose up -d labelstudio
```

This will start Label Studio at http://localhost:8080, and mount the local directory ./label-studio-data into the container, where all labeling data will be stored.

## Create Access Token

### Enable Legacy Tokens 

You need to create an access token for ML backend to access the images stored in Label Studio.  

Click on the Label Studio home icon and click Organization to go to organization page:

![organization](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/organization.png?raw=true)

and then click on API Token Settings and enable Legacy Tokens: 

![api token setting](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/api_token_settings.png?raw=true)

Save the changes. 

### Create legacy tokens

Now go to your Accounts & Settings (found on the top right corner), then navigate to Legacy Token to create a token: 

![legacy token](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/legacy_token.png?raw=true)

Copy the token to be used later when you are setting up the ML backend. 

## Create Annotation Project 


From Label Studio, click Create Project in the upper right. A window opens with three tabs:

![settings](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/create_project.png?raw=true)

*Project Name*

enter a project name, and (optionally) a project description. Once complete, you can click Save to create the project, or you can complete the other tabs.

*Data Import*

From here, you can upload files into Label Studio. You can do this now or after the project has been created.

*Labeling Setup*

Here, it allows you to set up the user interface for labelling task. In this case, let us select Objet Detecton with Bounding Boxes as a template: 


### Labelling UI setup 

In the Labelling UI setup, choose `Code` option and paste the following into the:


```xml

<View>
  <Header value="Enter a prompt for object detection:"/>
  <TextArea name="prompt" toName="image" editable="true" maxSubmissions="1" showSubmitButton="true" rows="2"/>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="goldfish" background="yellow"/>
  </RectangleLabels>
</View>

```

If you have more than one object class, you can just add additional label like below: 

```xml
....
  <RectangleLabels name="label" toName="image">
    <Label value="goldfish" background="yellow"/>
    <Label value="prawn" background="blue"/>
  </RectangleLabels>
....

```

The TextArea is required as we will be connecting Label Studio to the backend ML model Grounding Dino for auto-labelling, by using text prompt, to ease your labelling job. Grounding Dino is a zero-shot object detection model. 

Click *Save* to save the Labelling UI. 




# Machine Learning Backend

[Grounding Dino](https://github.com/IDEA-Research/GroundingDINO) is is a zero-shot object detection model. We can use the model to help us annotate our images. 

To integrate with Grounding Dino, you will need to setup the ML backend with the Grounding Dino model.  

## Installation of ML backend

There is a bug in the ML backend integration with Grounding Dino, in that model returns predictions as numpy type float32, and the backend is trying to jsonify the predictions, which causes the backend to crash, as numpy array cannot be serialize. I have done a quick fix, and you can check out the main branch from https://github.com/khengkok/label-studio-ml-backend.git

### Build a ML Backend Docker container 

You will need to build a docker container image. 

First git checkout the codebase from this [link](https://github.com/khengkok/label-studio-ml-backend.git).

Change directory to the following: 

`label-studio-ml-backend/label_studio_ml/examples/grounding_dino` 

Locate the file `docker-compose.yml` and change the following two lines
```
- LABEL_STUDIO_HOST=https://app.heartex.com/
- LABEL_STUDIO_ACCESS_TOKEN=your_access_token
```

Replace the url to point to your Label Studio url, for example: https://192.168.100.100:8080.  You CANNOT use localhost in the url. To find the local ip address of your machine, you can either use `ipconfig` (on MacOS, Windows), or `ip addr show` (for linux). 

Replace the Access token with the legacy token you created earlier in Label Studio. 


Now build the docker using the following command at the command prompt:

```bash
docker-compose build
```

the build will take a while, if this is the first time the docker image is built. After the build complete, run the following command to start the docker: 

```bash 
docker-compose up
```

Now the ML backend server is started and listen on port 9090. 


### Change of IP address

If your ip address changes (which happens when you connect your laptop to different wifi), you can update the ip address in the docker-compose.yaml and just stop the current container (CTRL-C) and restart the container using `docker-compose up`. 


### (Alternative) Run the pre-built docker directly

You can also run a pre-built docker directly.  First you need to create an environment file that contains the following environment variables: 

```
MODEL_DIR=/data/models
WORKERS=2
THREADS=4
LOG_LEVEL=DEBUG

# change the following to your local ip address
LABEL_STUDIO_HOST=http://<YOUR IP>:8080
# change the following to the access token you created in label studio
LABEL_STUDIO_ACCESS_TOKEN=<YOUR TOKEN>
BOX_THRESHOLD=0.30
TEXT_THRESHOLD=0.25
```

and the run the docker by typing the following command: 

For Windows, use the following docker image:

```powershell
docker run --env-file ./app.env  -v ./data/server:/data -p 9090:9090 ainyp/label-studio-ml-backend:grnddino-windows
```

For MacOS (silicon), use the following docker image: 

```bash
docker run --env-file ./app.env  -v ./data/server:/data -p 9090:9090 ainyp/label-studio-ml-backend:grnddino-macos
```

# Integrate Label Studio with Machine Learning Backend 

Open the project, and click "settings" on the top right corner.

![project_setting](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/project_settings.png?raw=true)


## Model Setting 

In *Model* setting, click "Connect Model", and in the setting page, enter the name, and URL of the backend ML, and toggle on interactive preannotations.  

For example: 

![model setting](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/model_setting.png?raw=true)

Click Validate and Save. There should not be any error and you should see that the model is connected: 

![model status](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/model_connected_status.png?raw=true)

## Annotation Settings

Now navigate to *Annotation*. In *Annotation* settings, toggle on *Use predictions to prelabel tasks* and select "grounding dino" model as the prediction model. 

![annotation settings](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/annotation_settings.png?raw=true)


# Auto-Labelling using Grounding Dino

Now you can try out the auto-labelling using Grounding Dino you setup earlier. Open the Project and select any image to label.  


![prompt](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/prompt.png?raw=true)

Make sure the *Auto-Annotation* is enabled. You can also optionally toggle on *Auto-accept Suggestions*. 

Now select the label `'goldfish 1'` below, and type `goldfish` in the prompt text box.  Click *Add* button.  Now wait for the predictions to be returned from backend (you should see a loading spinner at the bottom of the screen while waiting for backend prediction). 

You should see the following after a while: 

![label result](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/label_result.png?raw=True)

Togge the accept button to accept the suggested annotation (alternatively you can just click the green tick to accept all suggestions). 

The bounding box will change to solid color (in this case our label color is green) and you can then click Submit button to submit the labelling to complete the labelling process for this image. 

![final result](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/final_result.png?raw=True)

# Export

After you finished annotating, you can export the data.  Unfortunately, Label Studio does not support exporting to Ultralytics YOLO11 format. You can choose to export as **YOLO with Images**, and then reorganize the files into train and validate (and optionally test) folders, and to create a data.yaml file to provide information about the folder location of test and validation set:

<root folder>
--train
----images
----labels
--valid
----images
----labels
data.yaml
  

The data.yaml file should specify the following:

train: ../train/images
val: ../valid/images
test: ../test/images

names:
    0: goldfish

You can then zip up the entire folder and upload to Google Colab and unzip back into the same folder structure, ready for training. 












