"""
01 — Coding Agent: bash only

Port of aie-workshop-2026-singapore/solutions/07-coding-agent.ts — stripped
to one tool. You host the loop; bash runs on your machine.
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
    f"Today's date is {date.today().isoformat()}.",
)

print(f"Working directory: {ROOT}")
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
