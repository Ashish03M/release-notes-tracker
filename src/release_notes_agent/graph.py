from __future__ import annotations
from typing import TypedDict, Dict, List, Optional
from datetime import datetime, timezone
import json


# dual imports → works if run as module OR script
try:
    from .gh_toolkit import make_github_toolkit
    from .categorizer import label_guess, conventional_guess
    from .render import render_markdown
except ImportError:
    from gh_toolkit import make_github_toolkit
    from categorizer import label_guess, conventional_guess
    from render import render_markdown

from langgraph.graph import StateGraph, END


#"state" shared between steps
class State(TypedDict):
    repo: str
    since_ref: Optional[str]
    until_ref: str
    since_date: Optional[str]
    merged_prs: List[dict]
    commits: List[dict]
    grouped: Dict[str, List[str]]
    markdown: str


def _iso_date(dt_str: str | None) -> Optional[str]:
    """Convert ISO datetime → YYYY-MM-DD string (safe)."""
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).date().isoformat()
    except Exception:
        return None


def resolve_range(state: State) -> State:
    """Figure out 'since' point (latest release if possible)."""
    print("→ resolve_range")
    tk = make_github_toolkit(include_release_tools=True)
    tools = {t.name: t for t in tk.get_tools()}

    since = state.get("since_ref")
    since_date: Optional[str] = None

    if not since and "Get Latest Release" in tools:
        latest = tools["Get Latest Release"].invoke("") or {}
        since = latest.get("tag_name") or None
        since_date = _iso_date(latest.get("published_at") or latest.get("created_at"))

    state["since_ref"] = since or "HEAD~100"   # fallback if no release found
    state["until_ref"] = "HEAD"
    state["since_date"] = since_date
    print(f"  since_ref={state['since_ref']}, since_date={state['since_date']}")
    return state


def fetch_changes(state: State) -> State:
    """Download merged PRs from GitHub."""
    print("→ fetch_changes")
    tk = make_github_toolkit(include_release_tools=True)
    tools = {t.name: t for t in tk.get_tools()}

    search = tools.get("Search issues and pull requests")
    merged_prs: List[dict] = []

    if search:
        query = f'repo:{state["repo"]} is:pr is:merged'
        if state.get("since_date"):
            query += f' merged:>={state["since_date"]}'
        query += " sort:updated-desc"

        res_raw = search.invoke({"search_query": query}) or {}
        try:
            res = json.loads(res_raw) if isinstance(res_raw, str) else res_raw
        except Exception:
            print("Could not parse search results:", res_raw)
            res = {}
        for item in (res.get("items") or [])[:50]:
            labels = [l["name"] for l in item.get("labels", [])]
            merged_prs.append({
                "number": item.get("number"),
                "title": item.get("title"),
                "url": item.get("html_url"),
                "labels": labels,
                "merged_at": item.get("closed_at"),
                "author": (item.get("user") or {}).get("login"),
            })

    state["merged_prs"] = merged_prs
    state["commits"] = []  # placeholder for later if we fetch direct commits
    print(f"  fetched {len(merged_prs)} merged PR(s)")
    return state


def categorize(state: State) -> State:
    """Group PRs into sections."""
    print("→ categorize")
    grouped: Dict[str, List[str]] = {k: [] for k in
        ["Features", "Fixes", "Docs", "Refactors", "Perf", "Chore", "Breaking Changes", "Other"]}

    for pr in state["merged_prs"]:
        cat = label_guess(pr["labels"]) or conventional_guess(pr.get("title") or "") or "Other"
        bullet = f'{pr.get("title","")} (#{pr.get("number")}) — @{pr.get("author")} [{pr.get("url")}]'
        grouped[cat].append(bullet)

    state["grouped"] = grouped
    for k, v in grouped.items():
        if v:
            print(f"  {k}: {len(v)} item(s)")
    return state


def render(state: State) -> State:
    """Generate Markdown text."""
    print("→ render")
    state["markdown"] = render_markdown(state["grouped"], title="Release Notes")
    return state


def validate(state: State) -> State:
    """Make sure notes aren’t empty."""
    print("→ validate")
    if not state.get("markdown"):
        raise RuntimeError("No notes generated!")
    return state


def build_graph():
    """Assemble the workflow graph."""
    g = StateGraph(State)
    g.add_node("resolve_range", resolve_range)
    g.add_node("fetch_changes", fetch_changes)
    g.add_node("categorize", categorize)
    g.add_node("render", render)
    g.add_node("validate", validate)

    g.set_entry_point("resolve_range")
    g.add_edge("resolve_range", "fetch_changes")
    g.add_edge("fetch_changes", "categorize")
    g.add_edge("categorize", "render")
    g.add_edge("render", "validate")
    g.add_edge("validate", END)
    return g.compile()


# Debug: run this file directly
if __name__ == "__main__":
    agent = build_graph()
    state: State = {
        "repo": "Ashish03M/release-notes-tracker",  # 👈 your repo
        "since_ref": None,
        "until_ref": "HEAD",
        "since_date": None,
        "merged_prs": [],
        "commits": [],
        "grouped": {},
        "markdown": "",
    }
    out = agent.invoke(state)
    print("\n===== RELEASE NOTES =====\n")
    print(out["markdown"])
