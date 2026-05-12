# tools/ast_tools.py

import ast
import os

def extract_code_structure(file_path: str) -> dict:
    """
    Reads a Python file and extracts all functions and classes
    along with their parameters and docstrings.

    Why we need this:
    Knowing a file changed is not enough. The Documentation Update
    Agent needs to know WHAT is inside the file — function names,
    what parameters they take, and what they are supposed to do.
    This is the 'brain scanner' of the system.
    """

    # Check if the file actually exists before trying to read it
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "functions": [],
            "classes": []
        }

    try:
        # Read the raw source code from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not read file: {str(e)}",
            "functions": [],
            "classes": []
        }

    try:
        # ast.parse() converts the source code text into a tree structure
        # Every function, class, variable becomes a 'node' in this tree
        # We can then walk through the tree and find what we need
        tree = ast.parse(source_code)

    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Syntax error in file: {str(e)}",
            "functions": [],
            "classes": []
        }

    functions = []
    classes   = []

    # ast.walk() visits every single node in the entire tree
    for node in ast.walk(tree):

        # If this node is a function definition
        if isinstance(node, ast.FunctionDef):

            # Extract all parameter names
            params = [arg.arg for arg in node.args.args]

            # Extract the docstring (the text in triple quotes below def)
            # Returns None if there is no docstring
            docstring = ast.get_docstring(node) or "No docstring provided"

            functions.append({
                "name":      node.name,
                "params":    params,
                "docstring": docstring,
                "line":      node.lineno     # which line it starts on
            })

        # If this node is a class definition
        elif isinstance(node, ast.ClassDef):

            # Get all method names inside the class
            methods = [
                n.name for n in ast.walk(node)
                if isinstance(n, ast.FunctionDef)
            ]

            classes.append({
                "name":      node.name,
                "methods":   methods,
                "docstring": ast.get_docstring(node) or "No docstring provided",
                "line":      node.lineno
            })

    return {
        "status":    "success",
        "file":      file_path,
        "functions": functions,
        "classes":   classes,
        "summary":   f"Found {len(functions)} functions and {len(classes)} classes"
    }