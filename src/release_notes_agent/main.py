#Libraries for interacting with system,env variables..
import os
from typing import TypedDict, List
from dotenv import load_dotenv

# GitHub + AI + Workflow libraries
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

# Load environment variables (API keys, Github app keys) from the .env file
load_dotenv()

# Defining what info our workflow will keep track of.
class ReleaseState(TypedDict):
    release_info: str
    prs_and_commits: List[str]
    release_notes: str


# ---------- SETUP ----------
# LLM: Grok
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

# GitHub Toolkit
github = GitHubAPIWrapper()    # Fetch repo details
toolkit = GitHubToolkit.from_github_api_wrapper(github, include_release_tools=True) #Prebuilt Github tools
tools = toolkit.get_tools()
tools_map = {t.name: t for t in tools}
# Print tools_map to see available tools
# print("\nTools Map (name → tool):\n")
# for name, tool in tools_map.items():
#     print(f"- {name} → {tool}")


#  NODES
#  Steps in the workflow, (Do this then do this kind of.... A->B->C->....)

#Step 1 - Fetch Latest Release info from the repo
def get_latest_release(state: ReleaseState) -> ReleaseState:
    tool = tools_map.get("Get latest release")
    if not tool:
        raise RuntimeError("GitHub tool 'Get latest release' not found.")
    result = tool.run({"repo": os.getenv("GITHUB_REPOSITORY")})
    state["release_info"] = str(result)
    #print(f"Release info: {state['release_info']}")
    return state

#Step 2 - Collecting closed PRs and commits since the last release ( for ex. changes from Version 1 -> Version 2)
def collect_prs_commits(state: ReleaseState) -> ReleaseState:
    tool = tools_map.get("List open pull requests (PRs)")
    if not tool:
        raise RuntimeError("GitHub tool 'List pull requests' not found.")
    result = tool.run({"repo": os.getenv("GITHUB_REPOSITORY"), "state": "closed"})
    state["prs_and_commits"] = [str(result)]
    return state


def generate_release_notes(state: ReleaseState) -> ReleaseState:
    prompt = f"""
    You are a release notes generator.
    Latest release info: {state['release_info']}
    PRs & commits since last release: {state['prs_and_commits']}
    Generate release notes for version {state['release_info'].split('v')[-1]}.
    Write professional release notes in Markdown format.
    """
    response = llm.invoke(prompt)
    state["release_notes"] = response.content
    return state


# Graph
graph = StateGraph(ReleaseState)

graph.add_node("get_latest_release", get_latest_release)
graph.add_node("collect_prs_commits", collect_prs_commits)
graph.add_node("generate_release_notes", generate_release_notes)

graph.add_edge(START, "get_latest_release")
graph.add_edge("get_latest_release", "collect_prs_commits")
graph.add_edge("collect_prs_commits", "generate_release_notes")
graph.add_edge("generate_release_notes", END)

app = graph.compile()


# Generating Release Notes.....
if __name__ == "__main__":
    final_state = app.invoke({})
    print("\n Generated Release Notes:\n")
    print(final_state["release_notes"])
