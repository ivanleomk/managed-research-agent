---
name: agentic-video
description: Analyze a video URL with agentic processing via the Interactions API.
---

# Agentic video understanding

`GEMINI_API_KEY` is already in the shell — scripts read it from the environment.
Do not echo, print, or pass the key on the command line.

Agentic processing (`processing: "agentic"`) lets the model navigate the video timeline server-side instead of loading the full video into context.

## Run

From the repo root:

```bash
uv run python .agents/skills/agentic-video/analyze_video.py \
  "https://youtu.be/7Z5Vy9JBANs" \
  "In one sentence: what is this video about?"
```

Swap the URI and question as needed.

## Reference script

Minimal Interactions API call — save as `analyze_video.py` or run the copy in this skill folder:

```python
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
```

Key API shape:

```python
input=[
    {"type": "video", "uri": "<youtube or gs:// uri>", "processing": "agentic"},
    {"type": "text", "text": "<your question>"},
]
```
