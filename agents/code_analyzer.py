# agents/code_analyzer.py

from crewai import Agent, LLM
from crewai.tools import tool
from tools.ast_tools import extract_code_structure
from dotenv import load_dotenv
import os

load_dotenv()

gemini_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

@tool("Analyze Python file structure")
def analyze_file_tool(file_path: str) -> str:
    """
    Parses a Python file and extracts all function names,
    parameters, and docstrings using AST parsing.
    Input: path to the Python file.
    Output: structured dictionary of functions and classes.
    """
    result = extract_code_structure(file_path)
    return str(result)


code_analyzer_agent = Agent(
    role="Code Change Analyst",
    goal="""Analyze modified Python files to produce a detailed
    structured summary of all functions and classes including
    their names, parameters, and what they do.""",
    backstory="""You are a meticulous code reviewer with deep
    Python expertise. Given a list of modified files, you read
    each one carefully and build a complete picture of the code
    structure so the documentation team knows exactly what needs
    to be updated.""",
    tools=[analyze_file_tool],
    llm=gemini_llm,
    verbose=True,
    allow_delegation=False
)