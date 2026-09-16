"""
05 — Audio Generation in generate_content: Raw PCM Wrangling

Pain point: Standard models fail with 400 ('only supports text output').
Requires a dedicated TTS model, response_modalities config, and returns raw,
headerless 24kHz PCM bytes (audio/L16) that you must manually wrap in a WAV header.
"""

import wave
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents="Good morning, welcome to Builders Night.",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"),
            ),
        ),
    ),
)

# Pain: Audio is buried in inline_data as raw headerless PCM bytes
part = response.candidates[0].content.parts[0]
raw_pcm = part.inline_data.data  # audio/l16; rate=24000; channels=1

# Developer must manually synthesize a WAV header and write it to disk
out_dir = Path(__file__).resolve().parents[2] / "assets"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "builders_night.wav"

with wave.open(str(out_path), "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(raw_pcm)

print(f"Saved: {out_path}")
print(
    f"Mime: {part.inline_data.mime_type}, PCM size: {len(raw_pcm)} bytes, WAV size: {out_path.stat().st_size} bytes"
)
