"""
02 — Coding Agent: bash + built-in Google tools

Port of aie-workshop-2026-singapore/solutions/08-google-tools.ts — add
google_search and url_context to the tools list; server runs them for you.
"""
from datetime import date

from dotenv import load_dotenv
from google import genai
from rich import print

from agent import ROOT, Agent, BASH_TOOL

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
agent = Agent(
    client,
    MODEL,
    {"bash": BASH_TOOL},
    f"You are a coding assistant with bash access to {ROOT}. "
    f"You also have Google Search and URL context. "
    f"Today's date is {date.today().isoformat()}.",
    builtin_tools=[{"type": "google_search"}, {"type": "url_context"}],
)

print(f"Working directory: {ROOT}")
print("Try: 'What's the weather in London?' or 'Summarize https://en.wikipedia.org/wiki/Artificial_intelligence'")
print("Type 'exit' or 'quit' to stop.\n")

while True:
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not user_input or user_input.lower() in {"exit", "quit"}:
        break

    agent.run(user_input)
