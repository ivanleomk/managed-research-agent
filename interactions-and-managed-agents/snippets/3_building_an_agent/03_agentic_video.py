"""
03 — Coding Agent: bash + agentic-video skill

GEMINI_API_KEY is loaded into the shell env for bash subprocesses — the model
is told the key exists but never receives it. Follow the skill via bash.
"""

import os
from datetime import date

from dotenv import load_dotenv
from google import genai
from rich import print

from agent import ROOT, Agent, BASH_TOOL

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
SKILL = ROOT / ".agents/skills/agentic-video/SKILL.md"
PROMPT = (
    "Use the agentic-video skill to summarize "
    "https://youtu.be/7Z5Vy9JBANs in one sentence."
)

agent = Agent(
    client,
    MODEL,
    {"bash": BASH_TOOL},
    f"You are a coding assistant with bash access to {ROOT}. "
    f"GEMINI_API_KEY is available in your shell — use it via scripts, never echo or print it. "
    f"When asked about video, read and follow {SKILL}. "
    f"Run `.agents/skills/agentic-video/analyze_video.py` via bash. "
    f"Today's date is {date.today().isoformat()}.",
)


while True:
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break
    if not user_input or user_input.lower() in {"exit", "quit"}:
        break

    agent.run(user_input)
