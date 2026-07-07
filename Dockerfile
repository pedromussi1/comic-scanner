# Base Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Writable dirs for the CLIP model download (cover recognition) and runtime uploads.
ENV HF_HOME=/tmp/hf
RUN mkdir -p uploads /tmp/hf && chmod -R 777 uploads /tmp/hf

EXPOSE 8000

# 2 workers keeps memory reasonable (each loads its own CLIP model on first cover scan);
# long timeout covers the one-time model download.
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "300", "app:app"]
