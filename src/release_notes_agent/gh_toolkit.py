from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit

#Create a GitHubToolkit for accessinjg the GitHub tools.
def make_github_toolkit(include_release_tools: bool = True) -> GitHubToolkit:

    gh = GitHubAPIWrapper()
    tk = GitHubToolkit.from_github_api_wrapper(
        gh, include_release_tools=include_release_tools
    )
    return tk

#List all available Github tools
def list_tool_names() -> list[str]:

    toolkit = make_github_toolkit()
    return [tool.name for tool in toolkit.get_tools()]

if __name__ == "__main__":
    # Debug run: print all tools
    print("Available GitHub tools:")
    for name in list_tool_names():
        print(" -", name)
