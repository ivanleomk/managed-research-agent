"""
05 — Multimodal Input: Raw Video

Pass a video URI + question. Static processing loads the full video into context.
"""
from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
VIDEO_URI = "https://youtu.be/7Z5Vy9JBANs"
PROMPT = "In one sentence: what is this video about?"

input_items = [
    {"type": "video", "uri": VIDEO_URI},
    {"type": "text", "text": PROMPT},
]
print(input_items)

interaction = client.interactions.create(model=MODEL, input=input_items)
print(interaction.output_text)
print({"total_tokens": interaction.usage.total_tokens})
