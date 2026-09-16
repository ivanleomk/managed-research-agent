"""02 — Managed Agent: HN crawl (code execution)"""
from dotenv import load_dotenv
from google import genai

from lib.print import print_event, print_prompt

load_dotenv(override=True)
client = genai.Client()

PROMPT = "Crawl Hacker News and return a list of 10 top stories with title and URL."

print_prompt(PROMPT)

stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",
    stream=True,
    input=PROMPT,
)

for event in stream:
    print_event(event)
