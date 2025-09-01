import typer
from pathlib import Path
from .graph import build_graph, State

# ✅ create a Typer application
app = typer.Typer(help="Release Notes Generator CLI")

# ✅ register "generate" as a subcommand
@app.command("generate")
def generate(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository in owner/name format (e.g. user/repo)"),
    since: str = typer.Option(None, help="Start point (tag, SHA, or leave blank for auto)"),
    output: Path = typer.Option(None, help="Save notes to this file instead of printing"),
):
    """Generate release notes for a repo."""
    agent = build_graph()

    state: State = {
        "repo": repo,
        "since_ref": since,
        "until_ref": "HEAD",
        "since_date": None,
        "merged_prs": [],
        "commits": [],
        "grouped": {},
        "markdown": "",
    }

    out = agent.invoke(state)
    notes = out["markdown"]

    if output:
        output.write_text(notes, encoding="utf-8")
        typer.echo(f"✅ Release notes saved to {output}")
    else:
        typer.echo("\n===== RELEASE NOTES =====\n")
        typer.echo(notes)


if __name__ == "__main__":
    app()
