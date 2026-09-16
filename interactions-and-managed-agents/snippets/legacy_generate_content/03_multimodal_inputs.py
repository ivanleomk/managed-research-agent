"""
03 — Multimodal Inputs in generate_content: Payload Bloat

Pain point: In multi-turn chat, the client must keep re-sending raw image bytes
in every follow-up turn in `contents`, multiplying client memory and network payloads.
"""

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
img_path = Path(__file__).resolve().parents[2] / "assets" / "london.png"
image_part = types.Part.from_bytes(data=img_path.read_bytes(), mime_type="image/png")

history = [
    types.Content(
        role="user",
        parts=[
            image_part,
            types.Part.from_text(text="Describe this London scene in detail."),
        ],
    )
]

# Turn 1: Send image + question
res1 = client.models.generate_content(model=MODEL, contents=history)
history.append(res1.candidates[0].content)

# Turn 2: Follow-up question — image bytes remain in history and ride along again
history.append(
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text="Which famous landmark is on the left, and what river is in the foreground?"
            )
        ],
    )
)
res2 = client.models.generate_content(model=MODEL, contents=history)

print(res2.text)
# Output:
# Big Ben and the Houses of Parliament are on the left, with the River Thames in the foreground.
