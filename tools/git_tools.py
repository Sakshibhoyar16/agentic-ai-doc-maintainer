# tools/git_tools.py

import git
import os
from dotenv import load_dotenv

load_dotenv()


def get_changed_files(repo_path: str) -> dict:
    """
    Opens a local Git repo and compares the latest commit
    to the previous one. Returns which Python files changed.
    """

    try:
        repo = git.Repo(repo_path)

    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not open repo at {repo_path}. Error: {str(e)}",
            "changed_files": []
        }

    commits = list(repo.iter_commits('HEAD', max_count=2))

    if len(commits) < 2:
        return {
            "status": "only_one_commit",
            "message": "Need at least 2 commits to detect changes.",
            "changed_files": []
        }

    latest_commit = commits[0]
    previous_commit = commits[1]

    diffs = previous_commit.diff(latest_commit)

    changed_python_files = []

    for diff in diffs:

        if diff.b_path and diff.b_path.endswith('.py'):

            changed_python_files.append({
                "file": diff.b_path,
                "change_type": diff.change_type
            })

    return {
        "status": "success",
        "commit_hash": str(latest_commit.hexsha)[:8],
        "commit_message": latest_commit.message.strip(),
        "author": str(latest_commit.author),
        "changed_files": changed_python_files
    }


def commit_and_push_changes(repo_path: str, commit_message: str) -> dict:
    """
    Automatically stages documentation files,
    commits them, and pushes them to GitHub.
    """

    try:

        # Open the git repository
        repo = git.Repo(repo_path)

        # Stage documentation files
        repo.git.add("README.md")
        repo.git.add("DOCUMENTATION.md")

        # Create commit
        repo.index.commit(commit_message)

        # Push changes to GitHub
        origin = repo.remote(name='origin')
        origin.push()

        return {
            "status": "success",
            "message": "Documentation successfully pushed to GitHub."
        }

    except Exception as e:

        return {
            "status": "error",
            "message": f"Push failed: {str(e)}"
        }