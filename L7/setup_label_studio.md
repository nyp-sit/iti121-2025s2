# Label Studio 

## Installation of Label Studio 


### Docker 

#### Pre-requisites

You can use Docker to run Label Studio. Make sure you have Docker (desktop) installed on your machine.

On Linux: 

```bash
docker run -it -p 8080:8080 -v $(pwd)/mydata:/label-studio/data heartexlabs/label-studio:latest
```

On Windows, modify the path for `-v` accordingly using Windows path convention.

```
docker run -it -p 8080:8080 -v $(pwd)/mydata:/label-studio/data heartexlabs/label-studio:latest
```

This will start Label Studio at http://localhost:8080, and mount the local directory ./mydata into the container, where all labeling data will be stored. 



### Pip install 

Install Label Studio in a clean Python environment. You can either create a virtual environment using venv or conda to reduce the likelihood of package conflicts or missing packages.

```bash
python3 -m venv env
source env/bin/activate
python -m pip install label-studio
```

or 

```bash
conda create -n env
conda activate env 
python -m pip install label-studio
```

After install, you can start the Label Studio server by using the following command: 

```bash 
label-studio
```

The default web browser will automatically open at http://localhost:8080 with Label Studio


### Other options 

Please refer to `https://labelstud.io/guide/install.html' for more install options. 


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

The TextArea is required as we will be connecting Label Studio to the backend ML model Grounding Dino for auto-labelling to ease your labelling job. Grounding Dino is a zero-shot object detection model. 

Click *Save* to save the Labelling UI. 

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

Locate the file `docker-compose.yaml` and change the following two lines
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

![label result](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/label_result.png?raw=true)



