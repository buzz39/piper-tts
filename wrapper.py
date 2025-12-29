import sys
import os
import wave
import base64
import io
import json
import numpy as np
from piper import PiperVoice

def text_to_speech_base64(text, model="en_US-lessac-medium.onnx"):
    if not os.path.exists(model):
        # Fallback to absolute path if not in CWD but in the common location
        if os.path.exists(os.path.join(os.getcwd(), model)):
            model = os.path.join(os.getcwd(), model)
        else:
            raise FileNotFoundError(f"Model file not found: {model}")
        
    voice = PiperVoice.load(model)
    
    # 1. Phonemize
    # phonemize returns an iterator/list of list of phonemes (one list per sentence)
    sentence_phonemes = list(voice.phonemize(text))
    
    all_audio = []
    
    for phonemes in sentence_phonemes:
        # 2. Convert to IDs
        phoneme_ids = voice.phonemes_to_ids(phonemes)
        
        # 3. Generate Audio (float32 numpy array)
        audio = voice.phoneme_ids_to_audio(phoneme_ids)
        all_audio.append(audio)
        
    if not all_audio:
        return ""

    # 4. Concatenate all sentences
    final_audio = np.concatenate(all_audio)
    
    # 5. Convert to int16
    # Clip to be safe
    final_audio = np.clip(final_audio, -1.0, 1.0)
    # Convert to 16-bit PCM
    audio_int16 = (final_audio * 32767).astype(np.int16)
    
    # 6. Write to WAV
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2) # 16-bit
        
        # Get sample rate from config
        sample_rate = 22050
        if hasattr(voice, 'config') and hasattr(voice.config, 'sample_rate'):
             sample_rate = voice.config.sample_rate
        
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
        
    wav_bytes = wav_buffer.getvalue()
    base64_string = base64.b64encode(wav_bytes).decode('utf-8')
    return base64_string

if __name__ == "__main__":
    text_input = "This is a test."
    if len(sys.argv) > 1:
        text_input = " ".join(sys.argv[1:])
        
    try:
        b64 = text_to_speech_base64(text_input)
        print(b64)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
