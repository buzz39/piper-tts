
# Piper TTS API Deployment on Coolify

## Overview
This repository provides a fast, local neural text-to-speech API using [Piper](https://github.com/rhasspy/piper). It exposes a generic HTTP endpoint compatible with various clients.

## Deployment Instructions

1.  **Repository**: Connect this repository to your Coolify instance.
2.  **Build Pack**: Select **Docker**.
3.  **Port**: The API listens on port `8000`. Coolify should auto-detect this from the Dockerfile, or you can specify it manually.

## Persistent Storage (Optional but Recommended)
To persist voices and add new ones without redeploying:

1.  **Volume Mount**: Add a volume mount in your Coolify service configuration.
    *   **Source**: (Any local path on your server, e.g., `/data/coolify/services/piper/voices`)
    *   **Destination**: `/app/voices`
2.  **Adding Voices**:
    *   Download `.onnx` and `.onnx.json` voice files from [Hugging Face](https://huggingface.co/rhasspy/piper-voices).
    *   Place them in the mounted directory.
    *   The API will automatically detect new voices.

## API Usage

### 1. List Voices
**GET** `/voices`

Response:
```json
{
  "voices": [
    "en_US-lessac-medium",
    "en_GB-alan-medium"
  ]
}
```

### 2. Synthesize Speech
**POST** `/synthesize`

Request Body:
```json
{
  "text": "Hello, welcome to my text to speech service.",
  "voice": "en_US-lessac-medium"
}
```

*   `voice` is optional. Defaults to `en_US-lessac-medium`.

Response:
```json
{
  "audio": "UklGRu..." // Base64 encoded WAV audio
}
```

## Testing
You can decode the base64 output to a wav file to verify.
