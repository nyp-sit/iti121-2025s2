# Deploy Custom LLM Model locally

In this exercise, you will learn how to deploy the model locally using Ollama

## Download the Model

To download the model from huggingface, we can use the huggingface cli command to do so.  Let's first install the huggingface cli by the following: 

On macOS and Linux:

```
curl -LsSf https://hf.co/cli/install.sh | bash
```

On Windows:

```
powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"
```

Once installed, you can download the model using the following.  First create a folder or go to an existing folder when you want to download your model to and execute the following command: 

```
hf download khengkok/mental_health_gguf_model
```

## Run the model using Ollama   

Ollama is a very popular platform to run your local LLM. It exposes OpenAI compatible API, so you can easily migrate your existing applications built for OpenAI easily to Ollama-hosted models


### Installation

Follow the instructions [here](https://github.com/ollama/ollama/tree/main) for installation for MacOS, Linux and Windows.


### Download your model

In the directory when you downloaded the model, you should already have a sample Modelfile created for you.  You can import the finetuned model to Ollama using the following steps:

1. First change to the directory where you download Modelfile and gguf model is. 
2. Now run ollama create from the directory where the Modelfile was created:

```
ollama create mymodel 
```

3. Lastly test the model 

```
ollama run mymodel
```
