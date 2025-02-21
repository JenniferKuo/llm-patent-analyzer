# LLM Patent Infringement Analysis

## Introduction
This is a web application that allows users to analyze patent infringement using LLM. The frontend is built with React and the backend is built with FastAPI. LLM is using Ollama, model can be changed in `docker-compose.yml`. The default model is `mistral`(7B).

## Run 
```
docker compose up --build
```

## Usage
Visit http://localhost:80 to see the frontend
Visit http://localhost:8000 to see the backend

## Issue Tracker
- 使用Ollama or OpenAI API
- 每個產品分開request LLM，後來發現這樣prompt很慢，改成把所有產品一次prompt，不過如果產品很多應該需要優化成批次的做法
- Ollama的api call非常慢，但terminal因為是stream所以看起來比較快，可思考如何優化
- ollama的API模式好像有點笨，terminal的沒什麼問題，找不到原因，比方說product_name老是不一致，也許prompt還要調
- 卡在回傳的Json不顧的應，但其實可以指定schema
- 改善效能
- fuzzy matcher的matcher調整了一下
- ollama在docker環境很慢，terminal算是正常
- ollama小的模型對token數量有限制，可能要分批prompt
