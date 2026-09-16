"""00 — Validate Setup. Verify API key and list models."""
import os
import sys
from dotenv import load_dotenv
from google import genai
from rich import print


def validate_setup():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[red]✗ GEMINI_API_KEY not found in environment[/red]")
        return False

    print("[green]✓ GEMINI_API_KEY exists in shell[/green]")

    client = genai.Client(api_key=api_key)
    try:
        models = list(client.models.list())
        print(f"[green]✓ Can call list_models ({len(models)} models found)[/green]")
        return True
    except Exception as e:
        print(f"[red]✗ Failed to call list_models: {e}[/red]")
        return False


if __name__ == "__main__":
    if not validate_setup():
        sys.exit(1)
