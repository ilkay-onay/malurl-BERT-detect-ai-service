FROM python:3.10-slim

WORKDIR /app

# Install build dependencies for PyTorch optimizations
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
