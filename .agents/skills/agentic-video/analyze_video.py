#!/usr/bin/env -S uv run python
"""Analyze a video with agentic processing. Reads GEMINI_API_KEY from the shell."""
import os
import sys

from google import genai

if len(sys.argv) != 3:
    print("usage: analyze_video.py <video_uri> <question>", file=sys.stderr)
    sys.exit(1)

video_uri, question = sys.argv[1], sys.argv[2]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=[
        {"type": "video", "uri": video_uri, "processing": "agentic"},
        {"type": "text", "text": question},
    ],
)
print(interaction.output_text)
