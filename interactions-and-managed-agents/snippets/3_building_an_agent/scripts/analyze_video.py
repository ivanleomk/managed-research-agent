"""Agentic video helper — reads GEMINI_API_KEY from the shell, not from argv."""
import os
import sys

from google import genai

if len(sys.argv) != 3:
    print("usage: analyze_video.py <video_uri> <question>", file=sys.stderr)
    sys.exit(1)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=[
        {"type": "video", "uri": sys.argv[1], "processing": "agentic"},
        {"type": "text", "text": sys.argv[2]},
    ],
)
print(interaction.output_text)
