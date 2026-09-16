"""04 — Managed Agent: Persistent environment_id"""
import uuid

from dotenv import load_dotenv
from google import genai

from lib.print import print_event, print_prompt

load_dotenv(override=True)
client = genai.Client()

TOKEN = str(uuid.uuid4())
WRITE = f"Write exactly this UUID to notes.txt and nothing else: {TOKEN}"
READ = "Run `cat notes.txt` (or `echo $(cat notes.txt)`) and show me the output."

print_prompt(WRITE)
stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",
    stream=True,
    input=WRITE,
)

last = None
for event in stream:
    print_event(event)
    last = event

print_prompt(READ)
stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment=last.interaction.environment_id,
    previous_interaction_id=last.interaction.id,
    stream=True,
    input=READ,
)
for event in stream:
    print_event(event)
