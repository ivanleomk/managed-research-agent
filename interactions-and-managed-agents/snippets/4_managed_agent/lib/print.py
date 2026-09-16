"""Pretty-print managed agent stream events."""
import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

console = Console(highlight=False)
_default_state: dict = {"buffers": {}}


def print_prompt(prompt: str) -> None:
    console.print()
    console.print(Panel(prompt.strip(), title="prompt", border_style="bright_blue"))
    console.print()


def print_event(event, state: dict | None = None) -> None:
    state = state if state is not None else _default_state
    buffers = state.setdefault("buffers", {})

    if event.event_type == "interaction.created":
        buffers.clear()
        return

    if event.event_type == "interaction.completed":
        interaction = event.interaction
        state["id"] = interaction.id
        state["environment_id"] = interaction.environment_id
        return

    if event.event_type == "step.start":
        buffers[event.index] = {"type": event.step.type, "step": event.step}
        return

    if event.event_type == "step.delta":
        delta = event.delta
        buffer = buffers.setdefault(event.index, {"type": delta.type})
        if delta.type == "thought_summary":
            buffer["text"] = getattr(delta.content, "text", "") if delta.content else ""
        elif delta.type in {"code_execution_call", "google_search_call"}:
            buffer["args"] = delta.arguments
        elif delta.type in {"code_execution_result", "google_search_result"}:
            buffer["result"] = delta.result
        elif delta.type == "text":
            buffer.setdefault("text", "")
            buffer["text"] += delta.text
        return

    if event.event_type != "step.stop":
        return

    buffer = buffers.get(event.index, {})
    step_type = buffer.get("type")
    text = (buffer.get("text") or "").strip()

    if step_type in {"thought", "thought_summary"} and text:
        console.print(f"[dim italic]{text[:240]}[/dim italic]\n")

    elif step_type == "code_execution_call":
        step = buffer.get("step")
        args = buffer.get("args")
        console.print(f"\n[cyan]tool_called[/cyan] code_execution [dim]({getattr(step, 'id', '')})[/dim]")
        code = getattr(args, "code", None) if not isinstance(args, dict) else args.get("code")
        lang = getattr(args, "language", None) if not isinstance(args, dict) else args.get("language")
        lang = lang or "bash"
        if code:
            console.print(Syntax(code, lang, theme="monokai", line_numbers=False))
        console.print()

    elif step_type == "code_execution_result":
        result = (buffer.get("result") or "").strip()
        if result:
            console.print("[green]tool_result[/green]")
            try:
                console.print(Syntax(json.dumps(json.loads(result), indent=2), "json", theme="monokai"))
            except json.JSONDecodeError:
                console.print(result[:400] + ("..." if len(result) > 400 else ""))
            console.print()

    elif step_type == "google_search_call":
        args = buffer.get("args")
        queries = getattr(args, "queries", None)
        if queries is None and isinstance(args, dict):
            queries = args.get("queries") or args.get("query")
        if queries is None and hasattr(args, "query"):
            queries = getattr(args, "query")
        if queries is None:
            queries = args

        if isinstance(queries, list):
            formatted = ", ".join(f'"{q}"' for q in queries)
        elif isinstance(queries, str):
            formatted = f'"{queries}"'
        elif hasattr(queries, "model_dump"):
            formatted = json.dumps(queries.model_dump())
        else:
            try:
                formatted = json.dumps(queries)
            except (TypeError, ValueError):
                formatted = str(queries)
        console.print(f"\n[cyan]google_search[/cyan] {formatted}\n")

    elif step_type == "google_search_result":
        console.print("[dim]google_search_result[/dim]\n")

    elif step_type == "model_output" and text:
        console.print()
        console.print(Markdown(text))
        console.print()
