"""00 — Managed Agent: Quickstart"""
from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",
    stream=True,
    input="What is 2+2?",
)

for event in stream:
    print(event)
