from pathlib import Path


EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".rs": "Rust",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
}


def detect_language(filename: str, code: str = "") -> str:
    """
    Detects the programming language using file extension first.
    If extension is unknown, it uses simple code patterns.
    """

    suffix = Path(filename).suffix.lower()

    if suffix in EXTENSION_LANGUAGE_MAP:
        return EXTENSION_LANGUAGE_MAP[suffix]

    if "def " in code or "import " in code:
        return "Python"

    if "function " in code or "console.log" in code:
        return "JavaScript"

    if "public static void main" in code:
        return "Java"

    if "#include" in code:
        return "C/C++"

    return "Unknown"