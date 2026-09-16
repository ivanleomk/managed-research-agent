"""Shared agent loop — Singapore workshop pattern."""
import json
import os
import subprocess
from pathlib import Path

from rich.console import Console

ROOT = Path(__file__).resolve().parents[3]
console = Console()


def run_bash(args: dict) -> str:
    try:
        proc = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT,
            env=os.environ,
        )
        if proc.returncode != 0:
            return f"exit {proc.returncode}\n{proc.stderr or proc.stdout}"
        return proc.stdout.strip() or "ok (no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out"


BASH_TOOL = {
    "definition": {
        "type": "function",
        "name": "bash",
        "description": "Execute a bash command and return stdout or stderr.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    "function": run_bash,
}


def _preview(text: str, max_len: int = 500) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "... [truncated]"


def _thought_text(step) -> str | None:
    summary = getattr(step, "summary", None)
    if not summary:
        return None
    if isinstance(summary, str):
        return summary.strip() or None
    texts = [part.text for part in summary if getattr(part, "text", None)]
    joined = "\n".join(texts).strip()
    return joined or None


def _model_text(step) -> str | None:
    content = getattr(step, "content", None) or []
    texts = [part.text for part in content if getattr(part, "type", None) == "text"]
    joined = "\n".join(texts).strip()
    return joined or getattr(step, "text", None)


def _google_search_queries(step) -> list[str]:
    args = getattr(step, "arguments", None) or {}
    if not isinstance(args, dict):
        return []
    queries = args.get("queries") or args.get("query")
    if isinstance(queries, str):
        return [queries]
    if isinstance(queries, list):
        return queries
    return []


def print_step(step) -> None:
    step_type = step.type

    if step_type == "thought":
        text = _thought_text(step)
        if text:
            console.print(f"[dim italic]{_preview(text, 240)}[/dim italic]")

    elif step_type == "function_call":
        console.print(f"* [cyan]tool_called[/cyan] {step.name} {json.dumps(step.arguments)}")

    elif step_type == "google_search_call":
        console.print(f"* [cyan]google_search[/cyan] {json.dumps(_google_search_queries(step))}")

    elif step_type == "google_search_result":
        console.print("* [dim]google_search_result[/dim]")

    elif step_type == "url_context_call":
        args = getattr(step, "arguments", None) or {}
        urls = args.get("urls") or args.get("url") if isinstance(args, dict) else None
        console.print(f"* [cyan]url_context[/cyan] {json.dumps(urls or args)}")

    elif step_type == "url_context_result":
        console.print("* [dim]url_context_result[/dim]")

    elif step_type == "model_output":
        text = _model_text(step)
        if text:
            console.print(f"* {text}")


class Agent:
    def __init__(
        self,
        client,
        model: str,
        tools: dict[str, dict],
        system_instruction: str = "You are a helpful coding assistant.",
        builtin_tools: list[dict] | None = None,
    ):
        self.client = client
        self.model = model
        self.tools = tools
        self.system_instruction = system_instruction
        self.builtin_tools = builtin_tools or []
        self.previous_interaction_id = None

    def run(self, current_input):
        tools = [t["definition"] for t in self.tools.values()] + self.builtin_tools
        response = self.client.interactions.create(
            model=self.model,
            input=current_input,
            tools=tools,
            system_instruction=self.system_instruction,
            previous_interaction_id=self.previous_interaction_id,
        )
        self.previous_interaction_id = response.id

        function_calls = []
        for step in response.steps or []:
            if step.type == "function_call":
                function_calls.append(step)
                continue
            print_step(step)

        results = []
        for step in function_calls:
            console.print(f"* [cyan]tool_called[/cyan] {step.name} {json.dumps(step.arguments)}")
            result = self.tools[step.name]["function"](step.arguments) if step.name in self.tools else "Error: Tool not found"
            console.print(f"* [green]tool_result[/green] {_preview(result)}")
            results.append(
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(result)}],
                }
            )

        if results:
            console.print()
            return self.run(results)

        if not any(step.type == "model_output" for step in response.steps or []):
            text = (response.output_text or "").strip()
            if text:
                console.print(f"* {text}")

        console.print()
        return response
