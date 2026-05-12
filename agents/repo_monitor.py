# agents/repo_monitor.py

from crewai import Agent, LLM
from crewai.tools import tool
from tools.git_tools import get_changed_files
from dotenv import load_dotenv
import os

load_dotenv()

gemini_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

@tool("Detect code changes in repository")
def detect_changes_tool(repo_path: str) -> str:
    """
    Checks a Git repository for the latest commit and returns
    which Python files were modified, added, or deleted.
    Input: path to the local git repository folder.
    Output: dictionary with commit details and changed files.
    """
    result = get_changed_files(repo_path)
    return str(result)


repo_monitor_agent = Agent(
    role="Repository Monitor",
    goal="""Detect new commits in the target GitHub repository
    and identify exactly which Python source files were changed
    in the most recent commit.""",
    backstory="""You are a vigilant code watcher responsible for
    monitoring a software repository 24/7. The moment any developer
    pushes new code, you detect exactly what changed and produce
    a clear structured report so the documentation team can
    immediately take action. You are precise and never miss a file.""",
    tools=[detect_changes_tool],
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False
)