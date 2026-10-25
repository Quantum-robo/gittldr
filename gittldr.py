#!/usr/bin/env python3
"""gittldr.py - AI-powered Git diff summarizer and message generator."""

import os
import subprocess
import sys
from typing import Optional

import click
from google import genai
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

DIFF_CHAR_LIMIT = 8000

PROMPTS = {
    "commit": (
        "You are an expert software developer and Git specialist. Analyze the following git diff "
        "and generate a concise, high-quality commit message following the Conventional Commits specification "
        "(e.g., feat(scope): description, fix(scope): description, chore, refactor, docs, test, etc.).\n\n"
        "Rules:\n"
        "- The first line must be the summary header in Conventional Commits format, under 72 characters, lowercase/imperative mood.\n"
        "- Follow with an empty line and a bulleted list of key changes if helpful.\n"
        "- Return ONLY the commit message without Markdown code fences, backticks wrapping the whole response, or extra conversational text."
    ),
    "pr": (
        "You are an expert software engineer and technical lead. Analyze the following git diff and generate "
        "a comprehensive GitHub Pull Request description in clean GitHub-flavored Markdown.\n\n"
        "Include the following sections:\n"
        "## Summary\nA concise paragraph explaining what changes were made and why.\n\n"
        "## Type of Change\n- [ ] Bug fix\n- [ ] New feature\n- [ ] Refactoring\n- [ ] Documentation / Chore\n\n"
        "## Key Changes\nBullet points describing the important modifications.\n\n"
        "## Impact & Testing Considerations\nWhat might be affected and how to verify these changes.\n\n"
        "Format the output strictly as valid GitHub Markdown."
    ),
    "summary": (
        "You are a friendly technical communicator. Analyze the following git diff and provide a clear, "
        "concise summary in plain English suitable for non-technical stakeholders (product managers, designers, executives).\n\n"
        "Rules:\n"
        "- Avoid jargon, internal variable names, and implementation-level trivia.\n"
        "- Explain what user-facing or business outcome changed and why it matters.\n"
        "- Keep it brief (2 to 4 bullet points or a short paragraph).\n"
        "- Format nicely with Markdown."
    ),
}

TITLES = {
    "commit": "Conventional Commit Message",
    "pr": "GitHub Pull Request Description",
    "summary": "Non-Technical Summary",
}


def get_git_diff(staged: bool = False) -> str:
    """Fetch unstaged or staged git diff using subprocess."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--staged")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        console.print(
            Panel(
                "[bold red]Git is not installed or not found on PATH.[/bold red]\n"
                "Please ensure Git is installed and available in your environment.",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or "Failed to run git diff."
        if "not a git repository" in error_msg.lower():
            console.print(
                Panel(
                    "[bold red]Not a Git repository.[/bold red]\n"
                    "Please run this command from inside a Git repository, or initialize one with [cyan]git init[/cyan].",
                    title="Git Error",
                    border_style="red",
                )
            )
        else:
            from rich.text import Text
            content = Text()
            content.append("Git Error: ", style="bold red")
            content.append(error_msg)
            console.print(
                Panel(
                    content,
                    title="Git Command Failed",
                    border_style="red",
                )
            )
        sys.exit(result.returncode)

    return result.stdout.strip()


def truncate_diff(diff_text: str, limit: int = DIFF_CHAR_LIMIT) -> str:
    """Truncate git diff to limit characters to prevent token overflow."""
    if len(diff_text) <= limit:
        return diff_text

    notice = f"\n\n... [Diff truncated to {limit} characters to prevent token overflow] ..."
    allowed_length = max(0, limit - len(notice))
    return diff_text[:allowed_length] + notice


def get_gemini_api_key(api_key_arg: Optional[str] = None) -> str:
    """Retrieve Gemini API key from option, environment, or interactive prompt."""
    if api_key_arg and api_key_arg.strip():
        return api_key_arg.strip()

    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    console.print(
        Panel(
            "[bold yellow]Gemini API key not found in environment (GEMINI_API_KEY / GOOGLE_API_KEY).[/bold yellow]\n"
            "Please enter your Google Gemini API key below to continue.",
            title="Gemini Key Required",
            border_style="yellow",
        )
    )

    try:
        entered_key = Prompt.ask("[bold cyan]Enter your Gemini API Key[/bold cyan]", password=True)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled.[/dim]")
        sys.exit(1)

    if not entered_key or not entered_key.strip():
        console.print(
            Panel(
                "[bold red]No API key provided.[/bold red]\n"
                "You can also set it via [cyan]export GEMINI_API_KEY=\"your_key\"[/cyan] or pass [cyan]--api-key[/cyan].",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)

    return entered_key.strip()


def generate_llm_response(diff_content: str, output_type: str, model: str, api_key: str) -> str:
    """Send diff to Google Gemini and return generated response."""
    client = genai.Client(api_key=api_key)

    system_prompt = PROMPTS[output_type]
    user_prompt = f"{system_prompt}\n\nHere is the git diff:\n\n```diff\n{diff_content}\n```"

    with console.status(
        f"[bold cyan]Generating {output_type} with {model}...[/bold cyan]",
        spinner="dots",
    ):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
            )
        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Gemini Request Failed:[/bold red]\n{str(e)}",
                    title="API Error",
                    border_style="red",
                )
            )
            sys.exit(1)

    content = response.text or ""
    return content.strip()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--staged",
    is_flag=True,
    default=False,
    help="Inspect staged changes (`git diff --staged`) instead of unstaged changes.",
)
@click.option(
    "-t",
    "--type",
    "output_type",
    type=click.Choice(["commit", "pr", "summary"], case_sensitive=False),
    default="commit",
    show_default=True,
    help="Type of output to generate: 'commit' (Conventional Commit), 'pr' (GitHub PR Markdown), or 'summary' (concise non-technical summary).",
)
@click.option(
    "-m",
    "--model",
    default=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    show_default="gemini-2.5-flash (or $GEMINI_MODEL)",
    help="Gemini model to use.",
)
@click.option(
    "--api-key",
    envvar="GEMINI_API_KEY",
    default=None,
    help="Gemini API Key (optional, can also be set via GEMINI_API_KEY / GOOGLE_API_KEY or entered interactively).",
)
def main(staged: bool, output_type: str, model: str, api_key: Optional[str]) -> None:
    """CLI tool that generates commit messages, PR descriptions, and summaries from git diffs."""
    output_type = output_type.lower()
    diff_kind = "staged" if staged else "unstaged"

    # 1. Fetch git diff
    raw_diff = get_git_diff(staged=staged)

    # 2. Check if diff is empty
    if not raw_diff:
        flag_hint = "--staged" if not staged else "unstaged without --staged"
        console.print(
            Panel(
                f"[bold yellow]No {diff_kind} git changes found![/bold yellow]\n\n"
                f"There are currently no {diff_kind} differences in this repository.\n"
                f"[dim]Tip: Check with [bold]git status[/bold] or try running with [bold]{flag_hint}[/bold].[/dim]",
                title="Warning: No Diff Found",
                border_style="yellow",
            )
        )
        return

    # 3. Truncate if diff exceeds character limit
    original_len = len(raw_diff)
    truncated = original_len > DIFF_CHAR_LIMIT
    diff_to_process = truncate_diff(raw_diff, limit=DIFF_CHAR_LIMIT)

    if truncated:
        console.print(
            f"[dim yellow]Warning: Diff size ({original_len} chars) exceeds the {DIFF_CHAR_LIMIT} character limit. Truncating...[/dim yellow]"
        )

    # 4. Ensure API key is present (checks flag, env, and prompts interactively if missing)
    gemini_key = get_gemini_api_key(api_key_arg=api_key)

    # 5. Generate Gemini response
    result_text = generate_llm_response(
        diff_content=diff_to_process,
        output_type=output_type,
        model=model,
        api_key=gemini_key,
    )

    # 6. Render styled output
    panel_title = f"{TITLES.get(output_type, output_type.title())} ({diff_kind} diff)"
    markdown_content = Markdown(result_text)

    console.print()
    console.print(
        Panel(
            markdown_content,
            title=f"[bold green]{panel_title}[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    main()
