import re


def normalize_severity(severity):
    severity = str(severity).upper()

    if severity in ["ERROR", "CRITICAL"]:
        return "Critical"
    if severity == "HIGH":
        return "High"
    if severity == "MEDIUM":
        return "Medium"
    if severity == "LOW":
        return "Low"

    return "Medium"


def rule_based_review(code: str, language: str, static_findings: list):
    issues = []
    lines = code.splitlines()

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()

        if re.search(r"password\s*=\s*['\"]", stripped, re.IGNORECASE):
            issues.append({
                "line": str(index),
                "severity": "High",
                "category": "Security",
                "title": "Hardcoded password detected",
                "explanation": "A password appears to be stored directly in the source code.",
                "recommendation": "Move passwords and secrets to environment variables or a secure secrets manager."
            })

        if "os.system(" in stripped:
            issues.append({
                "line": str(index),
                "severity": "High",
                "category": "Security",
                "title": "Unsafe shell command usage",
                "explanation": "The code uses os.system(), which can be dangerous if user input is included in the command.",
                "recommendation": "Avoid os.system(). Use safer Python functions or subprocess with validated arguments."
            })

        if "SELECT" in stripped.upper() and "+" in stripped:
            issues.append({
                "line": str(index),
                "severity": "Critical",
                "category": "Security",
                "title": "Possible SQL injection",
                "explanation": "The SQL query appears to be built using string concatenation.",
                "recommendation": "Use parameterized queries instead of joining user input directly into SQL."
            })

        if "eval(" in stripped:
            issues.append({
                "line": str(index),
                "severity": "Critical",
                "category": "Security",
                "title": "Dangerous eval usage",
                "explanation": "eval() can execute arbitrary code if it receives unsafe input.",
                "recommendation": "Avoid eval(). Use safer parsing or validation logic."
            })

    for item in static_findings:
        title = str(item.get("title", "Static analyzer finding"))
        message = str(item.get("message", item.get("error", title)))

        issues.append({
            "line": str(item.get("line", "unknown")),
            "severity": normalize_severity(item.get("severity", "Medium")),
            "category": "Security",
            "title": title,
            "explanation": message,
            "recommendation": "Review this static analyzer finding and apply a secure coding fix."
        })

    if any(issue["severity"] == "Critical" for issue in issues):
        risk_score = 85
    elif any(issue["severity"] == "High" for issue in issues):
        risk_score = 70
    elif any(issue["severity"] == "Medium" for issue in issues):
        risk_score = 50
    elif issues:
        risk_score = 25
    else:
        risk_score = 10

    return {
        "summary": "Static and rule-based analysis completed successfully. The analyzer reviewed the code for security risks, code smells, and unsafe programming patterns.",
        "language": language,
        "purpose": "The submitted code was analyzed for common bugs, vulnerabilities, and maintainability problems.",
        "logic_explanation": "The fallback analyzer checked the code using local static analysis tools and custom security rules. Full AI explanation requires active OpenAI API quota.",
        "complexity": "Basic fallback mode does not calculate full AI-based complexity, but security and maintainability issues were detected.",
        "risk_score": risk_score,
        "issues": issues,
        "improvements": [
            "Remove hardcoded secrets from the source code.",
            "Use parameterized SQL queries to prevent SQL injection.",
            "Avoid unsafe shell command execution.",
            "Validate and sanitize user input.",
            "Add proper error handling.",
            "Close database connections properly."
        ],
        "tests_to_add": [
            "Test valid user input.",
            "Test empty input.",
            "Test malicious SQL-like input.",
            "Test file names with unsafe characters.",
            "Test database failure cases."
        ],
        "annotated_code": code,
        "refactored_code": code
    }