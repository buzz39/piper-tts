FROM python:3.11-slim

WORKDIR /app

# Install Piper HTTP
RUN pip install --no-cache-dir piper-tts[http]

# Optional: download a default voice at build time (can be overridden)
RUN python -m piper.download_voices en_US-lessac-medium

# Configurable via env
ENV PIPER_VOICE=en_US-lessac-medium
ENV PIPER_DATA_DIR=/app/voices

# Create entrypoint script
RUN mkdir -p /app
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/docker-entrypoint.sh"]