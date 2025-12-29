
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import wave
import io
import base64
import numpy as np
import logging
from typing import Optional
from piper import PiperVoice
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global cache for loaded voices to avoid reloading on every request
# Key: model_path, Value: PiperVoice object
voice_cache = {}

VOICES_DIR = os.environ.get("PIPER_VOICE_DIR", os.getcwd())

class SynthesisRequest(BaseModel):
    text: str
    voice: Optional[str] = "en_US-lessac-medium"

def get_voice_path(voice_name):
    # Check if full path provided
    if os.path.exists(voice_name):
        return voice_name
    
    # Check in VOICES_DIR (e.g., en_US-lessac-medium.onnx)
    # We accept voice name with or without .onnx
    model_name = voice_name if voice_name.endswith(".onnx") else f"{voice_name}.onnx"
    path = os.path.join(VOICES_DIR, model_name)
    
    if os.path.exists(path):
        return path
    
    return None

def load_voice(model_path):
    if model_path in voice_cache:
        return voice_cache[model_path]
    
    logger.info(f"Loading model: {model_path}")
    voice = PiperVoice.load(model_path)
    voice_cache[model_path] = voice
    return voice

@app.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    model_path = get_voice_path(request.voice)
    if not model_path:
        # Try to find any .onnx file if default fails?
        # For now, return error
        raise HTTPException(status_code=404, detail=f"Voice '{request.voice}' not found in {VOICES_DIR}")

    try:
        voice = load_voice(model_path)
    except Exception as e:
        logger.error(f"Failed to load voice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load voice: {str(e)}")

    try:
        # 1. Phonemize
        sentence_phonemes = list(voice.phonemize(request.text))
        
        all_audio = []
        for phonemes in sentence_phonemes:
            phoneme_ids = voice.phonemes_to_ids(phonemes)
            audio = voice.phoneme_ids_to_audio(phoneme_ids)
            all_audio.append(audio)
            
        if not all_audio:
            return {"audio": ""}

        # 4. Concatenate
        final_audio = np.concatenate(all_audio)
        
        # 5. Convert to int16
        final_audio = np.clip(final_audio, -1.0, 1.0)
        audio_int16 = (final_audio * 32767).astype(np.int16)
        
        # 6. Write to WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            
            sample_rate = 22050
            if hasattr(voice, 'config') and hasattr(voice.config, 'sample_rate'):
                 sample_rate = voice.config.sample_rate
            
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
            
        wav_bytes = wav_buffer.getvalue()
        base64_string = base64.b64encode(wav_bytes).decode('utf-8')
        
        return {"audio": base64_string}

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def list_voices():
    # List available .onnx files in VOICES_DIR
    voices = []
    if os.path.exists(VOICES_DIR):
        for f in os.listdir(VOICES_DIR):
            if f.endswith(".onnx"):
                voices.append(f.replace(".onnx", ""))
    return {"voices": voices}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
