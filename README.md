# LLM Patent Infringement Analysis

## Introduction
This is a web application that allows users to analyze patent infringement using LLM. The frontend is built with React and the backend is built with FastAPI. LLM is using Ollama, model can be changed in `docker-compose.yml`. The default model is `mistral`(7B).

## Demo
Since running ollama on docker can be extreamly slow and cause timeout, I running it on terminal for demo.
<video width="100%" controls>
  <source src="demo.mp4" type="video/mp4">
</video>

## Run 
```
docker-compose up --build
```
This will start three containers:
- frontend
- backend
- ollama (LLM model server)

Downoading model can take a long time, please be patient.

## Usage
Visit http://localhost:80 to see the frontend
Visit http://localhost:8000/docs to see the backend swagger api docs

## Issue Tracker
- Ollama running on docker can be extreamly slow and can cause timeout(> 5 minutes), running on terminal is slightly better.
- The analysis result is not very good due to LLM's capability.
- The model can be changed in `docker-compose.yml`, but small model like `phi` has limite token number, so it's not suitable for patent infringement analysis. 
- Use local LLM model might not be a good idea, because the patent infringement analysis is a complex task, and the model may not have enough knowledge to do the analysis. It also have more restriction on deployment environment.

## Future Work
- Use OpenAI API to replace ollama to improve performance
- Prompt can be optimized
- Add error handling
- Integrate with database to store the analysis result and company, patent information