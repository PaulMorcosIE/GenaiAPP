"""
azure_speech_utils.py ── Azure Speech-to-Text and Text-to-Speech utilities.
Requires:
    pip install azure-cognitiveservices-speech python-dotenv
"""

import os
import io
import wave
import tempfile
import contextlib
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# ─────────────────────── Load .env credentials ───────────────────────
load_dotenv()

speech_key = os.getenv("AZURE_SPEECH_KEY")
speech_region = os.getenv("AZURE_SPEECH_REGION")

if not (speech_key and speech_region):
    raise EnvironmentError("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env.")

speech_config = speechsdk.SpeechConfig(
    subscription=speech_key,
    region=speech_region
)
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = "en-US-AndrewMultilingualNeural"

# ─────────────────────── Voice → Text ───────────────────────
def speech_to_text(pcm_bytes: bytes) -> Optional[str]:
    """Convert raw PCM bytes to valid WAV and return transcript."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        with contextlib.closing(wave.open(tmp, 'wb')) as wf:
            wf.setnchannels(1)         # mono
            wf.setsampwidth(2)         # 16-bit PCM
            wf.setframerate(16000)     # 16 kHz sample rate
            wf.writeframes(pcm_bytes)

        audio_input = speechsdk.AudioConfig(filename=tmp.name)
        recognizer = speechsdk.SpeechRecognizer(speech_config, audio_input)
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        return None

# ─────────────────────── Text → Voice ───────────────────────
def text_to_speech(text: str) -> bytes:
    """Convert text to speech and return WAV byte stream."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_out = speechsdk.audio.AudioOutputConfig(filename=tmp.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config, audio_out)

        result = synthesizer.speak_text_async(text).get()

        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError(f"TTS failed: {result.reason}")

        with open(tmp.name, "rb") as f:
            return f.read()

