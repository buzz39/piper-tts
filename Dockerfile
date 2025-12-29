
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any (none strictly needed for minimal piper, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create voices directory
ENV PIPER_VOICE_DIR=/app/voices
RUN mkdir -p "$PIPER_VOICE_DIR"

# Download default voice into the voices directory
RUN python -m piper.download_voices en_US-lessac-medium --download-dir "$PIPER_VOICE_DIR"

# Copy application code
COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
