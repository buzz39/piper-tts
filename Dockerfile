FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by piper-tts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create voices directory
ENV PIPER_VOICE_DIR=/app/voices
RUN mkdir -p "$PIPER_VOICE_DIR"

# Download default voice (with better error handling)
RUN python -m piper.download_voices en_US-lessac-medium --download-dir "$PIPER_VOICE_DIR" || \
    (echo "Voice download failed but continuing..." && exit 0)

# Copy application code
COPY server.py .

EXPOSE 8000

# Healthcheck using curl
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/voices || exit 1

CMD ["python", "server.py"]
