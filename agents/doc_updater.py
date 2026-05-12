# agents/doc_updater.py

from crewai import Agent, LLM
from dotenv import load_dotenv
from tools.git_tools import commit_and_push_changes

import os

load_dotenv()

# LLM Configuration
gemini_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Documentation Writer Agent
doc_updater_agent = Agent(
    role="Technical Documentation Writer",

    goal="""
    Read the code analysis summary and write clear,
    accurate, professional Markdown documentation
    that reflects the current state of the code.
    """,

    backstory="""
    You are a senior technical writer who specializes
    in software documentation. You receive a structured
    analysis of Python code and produce clean developer-friendly
    Markdown documentation.

    You always document every function with:
    - purpose
    - parameters
    - return value
    - usage examples

    Your output is always ready to be saved directly
    into a README file.
    """,

    llm=gemini_llm,
    verbose=False,
    allow_delegation=False
)


def save_documentation_and_push(
    documentation_text: str,
    repo_path: str
):
    """
    Saves generated documentation into README.md
    and DOCUMENTATION.md, then pushes changes to GitHub.
    """

    try:

        # File paths
        readme_path = os.path.join(repo_path, "README.md")

        documentation_path = os.path.join(
            repo_path,
            "DOCUMENTATION.md"
        )

        # Write README.md
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(documentation_text)

        # Write DOCUMENTATION.md
        with open(documentation_path, "w", encoding="utf-8") as f:
            f.write(documentation_text)

        print("\nDocumentation files updated successfully.\n")

        # Commit and push to GitHub
        push_result = commit_and_push_changes(
            repo_path=repo_path,
            commit_message="AI updated documentation automatically"
        )

        print(push_result)

        return {
            "status": "success",
            "message": "Documentation updated and pushed successfully."
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }