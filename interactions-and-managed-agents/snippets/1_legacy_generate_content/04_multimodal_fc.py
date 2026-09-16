"""
04 — Multimodal Function Calling in generate_content: Schema Limitations

Pain point: FunctionResponse only accepts a JSON dict (`response={...}`).
Returning an image from a tool means base64-encoding it into a string field—
no native image Part—and manually hunting through parts for the function_call.
"""

import base64
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich import print

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
img_path = Path(__file__).resolve().parents[2] / "assets" / "london.png"
tools = [
    {
        "function_declarations": [
            {
                "name": "read_image",
                "description": "Read an image file from disk.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            }
        ]
    }
]

prompt = f"Read the image at {img_path} and describe what you see."

res1 = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(tools=tools),
)
fc = next(
    part.function_call
    for part in res1.candidates[0].content.parts
    if part.function_call
)
print({"name": fc.name, "id": fc.id, "args": fc.args})

image_b64 = base64.b64encode(img_path.read_bytes()).decode()
tool_result = {
    "text": f"path is {img_path}",
    "image": image_b64,
}
print({**tool_result, "image": f"{tool_result['image'][:40]}..."})

res2 = client.models.generate_content(
    model=MODEL,
    contents=[
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
        res1.candidates[0].content,
        types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(name=fc.name, response=tool_result)
            ],
        ),
    ],
    config=types.GenerateContentConfig(tools=tools),
)

print(res2)
