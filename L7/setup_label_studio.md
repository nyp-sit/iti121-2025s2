# Label Studio 

## Installation of Label Studio 


### Docker 

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

Project Name
enter a project name, and (optionally) a project description.

Once complete, you can click Save to create the project, or you can complete the other tabs.

Data Import
From here, you can upload files into Label Studio. You can do this now or after the project has been created.

Labeling Setup
Here, it allows you to set up the user interface for labelling task. In this case, let us select Objet Detecton with Bounding Boxes as a template: 


### Labelling UI setup 

In the Labelling UI setup, choose `Code` option and paste the following into the:


```xml

<View>
  <Header value="Enter a prompt for object detection:"/>
  <TextArea name="prompt" toName="image" editable="true" maxSubmissions="1" showSubmitButton="true" rows="2"/>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="apple" background="yellow"/>
  </RectangleLabels>
</View>

```

The TextArea is required as we will be connecting Label Studio to the backend ML model Grounding Dino for auto-labelling to ease your labelling job. Grounding Dino is a zero-shot object detection model. 

Click *Save* to save the Labelling UI. 

### Integrate with Machine Learning Model 

Open the project, and click "settings" on the top right corner.


In Annotation settings:

- Toggle on Use predictions to prelabel tasks

In Model setting, click "Edit"

toggle on interactive preannotations


# Integration with Grounding Dino 

To integrate with Grounding Dino, you will need to setup the ML backend with the Grounding Dino model.  

There is a bug in the backend, in that model returns predictions as numpy type float32, and the backend is trying to jsonify the predictions, which causes the backend to crash. I have done a quick fix, and you can check out the main branch from https://github.com/khengkok/label-studio-ml-backend.git

building a docker container

First git checkout the codebase at https://github.com/khengkok/label-studio-ml-backend.git.

Change directory to the following

