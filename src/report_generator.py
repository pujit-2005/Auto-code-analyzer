import json
from datetime import datetime


def generate_markdown_report(result: dict, static_findings: list, original_code: str):
    issues_md_parts = []

    for index, issue in enumerate(result.get("issues", []), start=1):
        issue_text = [
            f"### Issue {index}: {issue.get('title')}",
            "",
            f"- **Line:** {issue.get('line')}",
            f"- **Severity:** {issue.get('severity')}",
            f"- **Category:** {issue.get('category')}",
            "",
            "**Explanation:**",
            str(issue.get("explanation")),
            "",
            "**Recommendation:**",
            str(issue.get("recommendation")),
            "",
            "---",
            ""
        ]

        issues_md_parts.append("\n".join(issue_text))

    issues_md = "\n".join(issues_md_parts)

    improvements_md = "\n".join(
        [f"- {item}" for item in result.get("improvements", [])]
    )

    tests_md = "\n".join(
        [f"- {item}" for item in result.get("tests_to_add", [])]
    )

    static_md = json.dumps(static_findings, indent=2)

    report_parts = [
        "# Auto Code Analyzer Report",
        "",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Summary",
        "",
        str(result.get("summary")),
        "",
        "## Language",
        "",
        str(result.get("language")),
        "",
        "## Purpose",
        "",
        str(result.get("purpose")),
        "",
        "## Logic Explanation",
        "",
        str(result.get("logic_explanation")),
        "",
        "## Complexity",
        "",
        str(result.get("complexity")),
        "",
        "## Risk Score",
        "",
        f"**{result.get('risk_score')}/100**",
        "",
        "---",
        "",
        "## Detected Issues",
        "",
        issues_md if issues_md else "No major issues detected.",
        "",
        "---",
        "",
        "## Suggested Improvements",
        "",
        improvements_md if improvements_md else "No improvements suggested.",
        "",
        "---",
        "",
        "## Tests to Add",
        "",
        tests_md if tests_md else "No test suggestions.",
        "",
        "---",
        "",
        "## Static Analyzer Findings",
        "",
        "```json",
        static_md,
        "```",
        "",
        "---",
        "",
        "## Annotated Code",
        "",
        "```text",
        str(result.get("annotated_code")),
        "```",
        "",
        "---",
        "",
        "## Refactored Code",
        "",
        "```text",
        str(result.get("refactored_code")),
        "```",
        "",
        "---",
        "",
        "## Original Code",
        "",
        "```text",
        original_code,
        "```",
        ""
    ]

    return "\n".join(report_parts)


def generate_json_report(result: dict, static_findings: list, original_code: str):
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "ai_review": result,
        "static_findings": static_findings,
        "original_code": original_code
    }

    return json.dumps(report_data, indent=2)