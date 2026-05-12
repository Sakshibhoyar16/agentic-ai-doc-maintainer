# main.py

from crewai import Crew, Task, Process, LLM
from agents.doc_updater import doc_updater_agent
from tools.ast_tools import extract_code_structure
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

# ---------------------------------------------------
# LLM Configuration
# ---------------------------------------------------
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------------------------------
# Repository Path
# ---------------------------------------------------
REPO_PATH = os.getenv("TARGET_REPO_PATH", "./agentic-test-repo")

print("=" * 60)
print("   Automated Documentation Maintainer")
print("=" * 60)

# ---------------------------------------------------
# STEP 1 — Scan ALL Python Files Recursively
# ---------------------------------------------------
print("\n[Step 1] Scanning all Python files...\n")

analysis_results = []

for root, dirs, files in os.walk(REPO_PATH):
    # Skip hidden folders like .git
    dirs[:] = [d for d in dirs if not d.startswith('.')]

    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            relative = os.path.relpath(file_path, REPO_PATH)
            result = extract_code_structure(file_path)

            if result['status'] == 'success' and result['functions']:
                result['relative_path'] = relative
                analysis_results.append(result)
                print(f"  Analyzed: {relative}")

print(f"\nTotal files with functions: {len(analysis_results)}")

if not analysis_results:
    print("No Python files with functions found. Exiting.")
    exit(0)

# Build a clean readable summary for the LLM
analysis_text = ""
for file_result in analysis_results:
    analysis_text += f"\n\n--- File: {file_result['relative_path']} ---\n"
    analysis_text += f"Summary: {file_result['summary']}\n"
    for func in file_result['functions']:
        analysis_text += f"\nFunction: {func['name']}({', '.join(func['params'])})\n"
        analysis_text += f"Docstring: {func['docstring']}\n"
        analysis_text += f"Line: {func['line']}\n"
    for cls in file_result['classes']:
        analysis_text += f"\nClass: {cls['name']}\n"
        analysis_text += f"Methods: {', '.join(cls['methods'])}\n"
        analysis_text += f"Docstring: {cls['docstring']}\n"

# ---------------------------------------------------
# STEP 2 — Generate Documentation Using CrewAI
# ---------------------------------------------------
print("\n[Step 2] Generating documentation with AI...\n")

task = Task(
    description=f"""
    Write complete professional Markdown documentation for
    this Python repository based on the following code analysis:

    {analysis_text}

    Rules:
    1. Start with: # API Documentation
    2. Group by filename as a section header like: ## calculator.py
    3. For each function use this exact format:

    ### function_name
    **Description:** what the function does
    **Parameters:**
    - param1: description
    - param2: description
    **Returns:** what it returns
    **Example:**
```python
    result = function_name(param1, param2)
```

    4. If a file has classes, document each class and its methods.
    5. Keep it clean, professional, and ready for GitHub.
    """,
    expected_output="Complete professional Markdown documentation for the repository.",
    agent=doc_updater_agent
)

crew = Crew(
    agents=[doc_updater_agent],
    tasks=[task],
    process=Process.sequential,
    verbose=False,
    llm=groq_llm
)

result = crew.kickoff()
documentation = str(result)
print("\nDocumentation generated successfully.\n")

# ---------------------------------------------------
# STEP 3 — Save Documentation Files
# ---------------------------------------------------
print("\n[Step 3] Saving documentation files...\n")

# Save DOCUMENTATION.md
doc_path = os.path.join(REPO_PATH, "DOCUMENTATION.md")
with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(documentation)
print("DOCUMENTATION.md saved.")

# Save README.md
readme_path = os.path.join(REPO_PATH, "README.md")
readme_content = """# agentic-test-repo

This repository is automatically documented by the
[Agentic AI Documentation Maintainer](https://github.com/Sakshibhoyar16/agentic-ai-doc-maintainer).

## What is this?

Every time code is pushed to this repository, an AI system
automatically reads the Python files, understands the functions,
and updates the documentation — with zero human effort.

## Documentation

See [DOCUMENTATION.md](./DOCUMENTATION.md) for full API documentation.

## How it works

1. Developer pushes new code
2. AI system detects the change
3. AST parser reads all Python functions
4. Groq LLM writes the documentation
5. DOCUMENTATION.md is automatically updated

*Last updated automatically by AI Documentation Bot.*
"""
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme_content)
print("README.md updated.")

print("\n" + "=" * 60)
print("   DOCUMENTATION GENERATION COMPLETE")
print("=" * 60)
