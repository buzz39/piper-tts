FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir piper-tts[http]
RUN python -m piper.download_voices en_US-lessac-medium

EXPOSE 5000

CMD ["python", "-m", "piper.http_server", "-m", "en_US-lessac-medium", "--host", "0.0.0.0", "--port", "5000"]
