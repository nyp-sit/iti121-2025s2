# Annotate using Label Studio and Grounding Dino

In this guide, we will only describe how to run the Label Studio and the ML backend (Grounding Dino) as docker containers. 
Please refer to `https://labelstud.io/guide/install.html' for more install options. 

## Pre-requisites

Download the docker-compose.yml file to a chosen directory which you will use to store data from Label Studio and the ML backend.  Change to that directory (e.g. c:\mydata on windows), and create two subdirectory:  `labelstudio_data` and `grnddino_data`. 

```powershell
cd c:\mydata
mkdir labelstudio_data
mkdir grnddino_data
```

## Label Studio

Start the Label Studio docker container first by doing the following: 

```bash
podman compose up -d labelstudio
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

## Machine Learning Backend

[Grounding Dino](https://github.com/IDEA-Research/GroundingDINO) is is a zero-shot object detection model. We can use the model to help us annotate our images. 

Before we can run the ML backend, we need to change the following line in the `podman compose.yml, and replace with your actual legacy token you created earlier. 
```
- LABEL_STUDIO_ACCESS_TOKEN=your_access_token
```

Now start the ML backend by typing: 

```powershell
podman compose up -d grnddino
```

### Integrate Label Studio with Machine Learning Backend 

Open the project in Label Studio, and click "settings" on the top right corner.

![project_setting](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/project_settings.png?raw=true)


### Model Setting 

In *Model* setting, click "Connect Model", and in the setting page, enter the name, and URL of the backend ML (i.e. `http://grnddino:9090`) ,and toggle on interactive preannotations.  

For example: 

![model setting](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/model_setting.png?raw=true)

Click Validate and Save. There should not be any error and you should see that the model is connected: 

![model status](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/model_connected_status.png?raw=true)

### Annotation Settings

Now navigate to *Annotation*. In *Annotation* settings, toggle on *Use predictions to prelabel tasks* and select "grounding dino" model as the prediction model. 

![annotation settings](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/annotation_settings.png?raw=true)


### Auto-Labelling using Grounding Dino

Now you can try out the auto-labelling using Grounding Dino you setup earlier. Open the Project and select any image to label.  

![prompt](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/prompt.png?raw=true)

Make sure the *Auto-Annotation* is enabled. You can also optionally toggle on *Auto-accept Suggestions*. 

Now select the label `'goldfish 1'` below, and type `goldfish` in the prompt text box.  Click *Add* button.  Now wait for the predictions to be returned from backend (you should see a loading spinner at the bottom of the screen while waiting for backend prediction). 

You should see the following after a while: 

![label result](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/label_result.png?raw=True)

Togge the accept button to accept the suggested annotation (alternatively you can just click the green tick to accept all suggestions). 

The bounding box will change to solid color (in this case our label color is green) and you can then click Submit button to submit the labelling to complete the labelling process for this image. 

![final result](https://github.com/nyp-sit/iti121-2025s2/blob/main/L7/assets/final_result.png?raw=True)

### Export

After you finished annotating, you can export the data.  Unfortunately, Label Studio does not support exporting to Ultralytics YOLO11 format. You can choose to export as **YOLO with Images**, and then reorganize the files into train and validate (and optionally test) folders, and to create a data.yaml file to provide information about the folder location of test and validation set:

```
<root folder>
--train
----images
----labels
--valid
----images
----labels
data.yaml
```  

The data.yaml file should specify the following:

```
train: ../train/images
val: ../valid/images
test: ../test/images

names:
    0: goldfish
```

You can then zip up the entire folder and upload to Google Colab and unzip back into the same folder structure, ready for training. 


## Shutdown docker contains 

you can shutdown both containers all at one by: 

```bash
podman compose down
```

After the initial setup, the next time you can just start all containers at once by:

```bash
podman compose up
```











