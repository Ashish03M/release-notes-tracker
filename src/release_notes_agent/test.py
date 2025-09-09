# Libraries for interacting with system, env variables..
import os
import json
import re
from typing import TypedDict, List, Any, Dict
from dotenv import load_dotenv

# GitHub + AI + Workflow libraries
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

# Load environment variables (API keys, Github app keys) from the .env file
load_dotenv()

# ---------- VALIDATION ----------
REPO = os.getenv("GITHUB_REPOSITORY")  # expected "owner/repo"
if not REPO or "/" not in REPO:
    raise RuntimeError("GITHUB_REPOSITORY must be set as 'owner/repo' in your .env")

# if not os.getenv("GROQ_API_KEY"):
#     raise RuntimeError("GROQ_API_KEY must be set in your .env for ChatGroq")
#
# # Optional but recommended: a GitHub token (PAT or app installation token)
# if not os.getenv("GITHUB_API_TOKEN") and not os.getenv("GITHUB_ACCESS_TOKEN") and not os.getenv("GITHUB_TOKEN"):
#     print("WARNING: No GitHub token found. You may hit rate limits or get incomplete data.")

# Defining what info our workflow will keep track of.
class ReleaseState(TypedDict):
    repo: str
    latest_tag: str
    default_branch: str
    release_info: Dict[str, Any]
    prs_and_commits: Dict[str, Any]
    release_notes: str

# ---------- HELPERS ----------
def _to_json(obj: Any) -> Dict[str, Any]:
    """Best-effort conversion of tool result to JSON/dict."""
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except Exception:
            # last resort: try to scrape a tag_name from text
            m = re.search(r"'tag_name':\s*'([^']+)'", obj) or re.search(r'"tag_name"\s*:\s*"([^"]+)"', obj)
            return {"__raw__": obj, "tag_name": m.group(1) if m else None}
    return {"__raw__": str(obj)}

def _extract_latest_tag(latest_release_obj: Dict[str, Any]) -> str:
    # Common GitHub schema: tag_name, name
    tag = latest_release_obj.get("tag_name")
    if tag:
        return tag
    # sometimes “name” carries it
    name = latest_release_obj.get("name")
    if name and re.match(r"^v?\d+\.\d+\.\d+", name):
        return name
    # fallback
    return ""

def _safe_get(d: Dict[str, Any], key: str, default=""):
    val = d.get(key)
    return val if val is not None else default

# ---------- SETUP ----------
# LLM: make deterministic + concise
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile", temperature=0)

# GitHub Toolkit
github = GitHubAPIWrapper()  # Will use env tokens if present
toolkit = GitHubToolkit.from_github_api_wrapper(github, include_release_tools=True)
tools = toolkit.get_tools()
tools_map = {t.name: t for t in tools}

# Uncomment to inspect available tools
# print("\nTools Map (name → tool):")
# for name in tools_map.keys():
#     print("-", name)

# ---------- NODES ----------
def get_previous_release(state: ReleaseState) -> ReleaseState:
    tool = tools_map.get("Get latest release")
    if not tool:
        raise RuntimeError("GitHub tool 'Get latest release' not found.")
    raw = tool.run({"repo": REPO})
    rel = _to_json(raw)
    state["release_info"] = rel
    state["latest_tag"] = _extract_latest_tag(rel)
    # discover default branch (best effort)
    repo_tool = tools_map.get("Get repository")
    default_branch = "main"
    if repo_tool:
        repo_raw = repo_tool.run({"repo": REPO})
        repo_json = _to_json(repo_raw)
        default_branch = _safe_get(repo_json, "default_branch", default_branch)
    state["default_branch"] = default_branch
    state["repo"] = REPO
    return state

def collect_prs_commits(state: ReleaseState) -> ReleaseState:
    # Strategy:
    # - If we have a latest tag, we will still list PRs (closed) for context.
    #   Some toolkits also offer "Compare two commits"; if available, use it.
    prs_tool = tools_map.get("List pull requests (PRs)") or tools_map.get("List pull requests")
    compare_tool = tools_map.get("Compare two commits") or tools_map.get("Compare commits between two refs")
    result: Dict[str, Any] = {}

    # PRs (closed and merged are most relevant to release notes)
    if prs_tool:
        prs_raw = prs_tool.run({"repo": REPO, "state": "closed"})
        result["pull_requests"] = _to_json(prs_raw)
    else:
        result["pull_requests"] = {"warning": "PR listing tool not found"}

    # Commits since latest tag (if we can)
    if compare_tool and state["latest_tag"]:
        cmp_raw = compare_tool.run({
            "repo": REPO,
            "base": state["latest_tag"],
            "head": state["default_branch"]
        })
        result["commits_between"] = _to_json(cmp_raw)
    else:
        # fallback: if no compare tool or no tag, we skip
        result["commits_between"] = {"info": "No compare tool or no latest tag; skipping commit diff"}

    state["prs_and_commits"] = result
    return state

def generate_release_notes(state: ReleaseState) -> ReleaseState:
    repo = state["repo"]
    latest_tag = state["latest_tag"]
    default_branch = state["default_branch"]

    # We lock the title and forbid inventing numbers/names
    title = f"Release notes for {repo} (base: {latest_tag or 'initial'}) → {default_branch}"

    prompt = f"""
You are a release-notes writer. Use ONLY the provided data. DO NOT invent version names, tags, or dates.

DATA:
- repo: {repo}
- default_branch: {default_branch}
- latest_release: {json.dumps(state['release_info'], ensure_ascii=False)[:6000]}
- prs_and_commits: {json.dumps(state['prs_and_commits'], ensure_ascii=False)[:6000]}

TASK:
1) Start with the exact title:
   {title}
2) If no latest tag exists, label the section as "Unreleased".
3) Summarize changes by categories (Added, Changed, Fixed, Docs, Chore).
4) Bullet points must cite PR numbers or commit SHAs from the data when available.
5) Include a short "Contributors" list if present in the data.
6) If some info is missing, say "Not available" instead of guessing.
7) Keep it concise.

Return Markdown only.
"""
    response = llm.invoke(prompt)
    state["release_notes"] = response.content
    return state

# ---------- GRAPH ----------
graph = StateGraph(ReleaseState)
graph.add_node("get_previous_release", get_previous_release)
graph.add_node("collect_prs_commits", collect_prs_commits)
graph.add_node("generate_release_notes", generate_release_notes)

graph.add_edge(START, "get_previous_release")
graph.add_edge("get_previous_release", "collect_prs_commits")
graph.add_edge("collect_prs_commits", "generate_release_notes")
graph.add_edge("generate_release_notes", END)

app = graph.compile()

# ---------- RUN ----------
if __name__ == "__main__":
    final_state = app.invoke({})
    print("\nGenerated Release Notes:\n")
    print(final_state["release_notes"])
