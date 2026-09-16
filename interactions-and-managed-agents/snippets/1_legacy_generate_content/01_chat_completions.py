"""
01 — Chat Completions in generate_content: The History Trap

Pain point: generate_content is strictly stateless. The client must manually
accumulate every single turn and re-serialize the entire conversation on every request.
"""
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)
client = genai.Client()
history = []

# Turn 1
history.append(types.Content(role="user", parts=[types.Part.from_text(text="Hi, I am Alice.")]))
res1 = client.models.generate_content(model="gemini-3.8-flash", contents=history)
history.append(res1.candidates[0].content)

# Turn 2: Must re-send all previous turns across the wire
history.append(types.Content(role="user", parts=[types.Part.from_text(text="What is my name?")]))
res2 = client.models.generate_content(model="gemini-3.8-flash", contents=history)

print(res2.text)
# Output:
# Your name is Alice.
