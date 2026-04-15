FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    langchain \
    langchain-community \
    langchain-core \
    langchain-groq \
    langchain-text-splitters \
    faiss-cpu \
    mlflow \
    python-dotenv \
    groq \
    sentence-transformers \
    requests

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]