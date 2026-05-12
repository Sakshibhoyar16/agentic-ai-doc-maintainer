````python id="4jam4"
# main.py

from crewai import Crew, Task, Process, LLM

from agents.repo_monitor import (
    repo_monitor_agent,
    detect_changes_tool
)

from agents.code_analyzer import (
    code_analyzer_agent,
    analyze_file_tool
)

from agents.doc_updater import (
    doc_updater_agent,
    save_documentation_and_push
)

from tools.ast_tools import extract_code_structure

from dotenv import load_dotenv

import os

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

REPO_PATH = os.getenv(
    "TARGET_REPO_PATH",
    "./agentic-test-repo"
)

print("=" * 60)
print("   Automated Documentation Maintainer")
print("=" * 60)

# ---------------------------------------------------
# STEP 1 — Scan ALL Python Files
# ---------------------------------------------------

print("\n[Step 1] Scanning all Python files...\n")

analysis_results = []

for root, dirs, files in os.walk(REPO_PATH):

    for file in files:

        if file.endswith(".py"):

            file_path = os.path.join(root, file)

            result = extract_code_structure(file_path)

            analysis_results.append(result)

            print(f"Analyzed file: {file}")

print("\nCode analysis completed successfully.\n")

analysis_summary = str(analysis_results)

# ---------------------------------------------------
# STEP 2 — Generate Documentation Using CrewAI
# ---------------------------------------------------

task3 = Task(
    description=f"""
    Write professional Markdown documentation for the following
    Python code analysis:

    {analysis_summary}

    For every function include:

    - Function Name
    - Description
    - Parameters
    - Return Value
    - Example Usage

    Format Example:

    ## function_name

    **Description:** what the function does

    **Parameters:**
    - param1: description
    - param2: description

    **Returns:** what it returns

    **Example:**

    ```python
    result = function_name(param1, param2)
    ```
    """,

    expected_output="""
    Complete professional Markdown documentation
    ready for README.md and DOCUMENTATION.md.
    """,

    agent=doc_updater_agent
)

crew = Crew(
    agents=[
        doc_updater_agent
    ],

    tasks=[
        task3
    ],

    process=Process.sequential,

    verbose=False,

    llm=groq_llm
)

print("\n[Step 2] Generating documentation with AI...\n")

result = crew.kickoff()

print("\nDocumentation generated successfully.\n")

# ---------------------------------------------------
# STEP 3 — Save Documentation + Push To GitHub
# ---------------------------------------------------

print("\n[Step 3] Saving documentation and pushing to GitHub...\n")

save_result = save_documentation_and_push(
    documentation_text=str(result),
    repo_path=REPO_PATH
)

# ---------------------------------------------------
# STEP 4 — Final Status
# ---------------------------------------------------

print("\n" + "=" * 60)
print("   DOCUMENTATION UPDATE STATUS")
print("=" * 60)

print(save_result)

print("\nWorkflow completed successfully.\n")
````
