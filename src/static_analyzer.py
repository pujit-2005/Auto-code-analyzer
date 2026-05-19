import json
import subprocess
import tempfile
from pathlib import Path


def run_command(command: list, timeout: int = 30):
    """
    Runs a terminal command safely and captures output.
    Handles cases where stdout or stderr may be None.
    """

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        stdout = completed.stdout if completed.stdout is not None else ""
        stderr = completed.stderr if completed.stderr is not None else ""

        return {
            "success": True,
            "returncode": completed.returncode,
            "stdout": stdout.strip(),
            "stderr": stderr.strip()
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "Command not found: " + command[0],
            "stdout": "",
            "stderr": ""
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "stdout": "",
            "stderr": ""
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }


def run_bandit_scan(file_path: Path):
    """
    Runs Bandit only for Python files.
    """

    if file_path.suffix.lower() != ".py":
        return []

    result = run_command(
        [
            "bandit",
            "-f",
            "json",
            "-q",
            str(file_path)
        ],
        timeout=30
    )

    if not result.get("success"):
        return [
            {
                "tool": "bandit",
                "error": result.get("error", "Bandit failed")
            }
        ]

    output = result.get("stdout", "")

    if not output:
        return []

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        return [
            {
                "tool": "bandit",
                "error": "Could not parse Bandit output",
                "raw_output": output,
                "stderr": result.get("stderr", "")
            }
        ]

    findings = []

    for item in parsed.get("results", []):
        findings.append(
            {
                "tool": "bandit",
                "line": item.get("line_number"),
                "severity": item.get("issue_severity"),
                "confidence": item.get("issue_confidence"),
                "title": item.get("test_name"),
                "message": item.get("issue_text")
            }
        )

    return findings


def run_semgrep_scan(file_path: Path):
    """
    Runs Semgrep for supported languages.
    If Semgrep is not installed or fails, the app will continue.
    """

    result = run_command(
        [
            "semgrep",
            "scan",
            "--config",
            "auto",
            "--json",
            str(file_path)
        ],
        timeout=60
    )

    if not result.get("success"):
        return [
            {
                "tool": "semgrep",
                "error": result.get("error", "Semgrep failed")
            }
        ]

    output = result.get("stdout", "")

    if not output:
        return []

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        return [
            {
                "tool": "semgrep",
                "error": "Could not parse Semgrep output",
                "raw_output": output,
                "stderr": result.get("stderr", "")
            }
        ]

    findings = []

    for item in parsed.get("results", []):
        extra = item.get("extra", {})
        start = item.get("start", {})

        findings.append(
            {
                "tool": "semgrep",
                "line": start.get("line"),
                "severity": extra.get("severity"),
                "title": extra.get("message"),
                "rule_id": item.get("check_id"),
                "path": item.get("path")
            }
        )

    return findings


def run_static_analysis(code: str, filename: str):
    """
    Saves uploaded code temporarily, runs static analysis tools,
    then returns findings.
    The uploaded code is not executed.
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / filename
        file_path.write_text(code, encoding="utf-8")

        findings = []

        findings.extend(run_bandit_scan(file_path))
        findings.extend(run_semgrep_scan(file_path))

        return findings