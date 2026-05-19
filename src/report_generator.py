import json
import textwrap
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    PageBreak,
)


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


def _safe_paragraph(text):
    return escape(str(text or ""))


def _wrap_code(code: str, width: int = 95):
    wrapped_lines = []

    for line in str(code or "").splitlines():
        if len(line) <= width:
            wrapped_lines.append(line)
        else:
            wrapped_lines.extend(
                textwrap.wrap(
                    line,
                    width=width,
                    replace_whitespace=False,
                    drop_whitespace=False
                )
            )

    return "\n".join(wrapped_lines)


def generate_pdf_report(result: dict, static_findings: list, original_code: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        spaceAfter=16,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Code"],
        fontSize=7,
        leading=9,
        leftIndent=6,
        rightIndent=6,
        spaceBefore=6,
        spaceAfter=6,
    )

    story = []

    story.append(Paragraph("Auto Code Analyzer Report", title_style))
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        normal_style
    ))

    summary_table = Table(
        [
            ["Language", str(result.get("language", "Unknown"))],
            ["Risk Score", f"{result.get('risk_score', 0)}/100"],
            ["Issues Found", str(len(result.get("issues", [])))],
            ["Static Findings", str(len(static_findings))],
        ],
        colWidths=[1.8 * inch, 4.8 * inch]
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(Spacer(1, 10))
    story.append(summary_table)

    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(_safe_paragraph(result.get("summary")), normal_style))

    story.append(Paragraph("Purpose", heading_style))
    story.append(Paragraph(_safe_paragraph(result.get("purpose")), normal_style))

    story.append(Paragraph("Logic Explanation", heading_style))
    story.append(Paragraph(_safe_paragraph(result.get("logic_explanation")), normal_style))

    story.append(Paragraph("Complexity", heading_style))
    story.append(Paragraph(_safe_paragraph(result.get("complexity")), normal_style))

    story.append(Paragraph("Detected Issues", heading_style))

    issues = result.get("issues", [])

    if not issues:
        story.append(Paragraph("No major issues detected.", normal_style))
    else:
        for index, issue in enumerate(issues, start=1):
            issue_title = (
                f"Issue {index}: {issue.get('severity', 'Unknown')} - "
                f"{issue.get('title', 'Untitled issue')}"
            )

            story.append(Paragraph(_safe_paragraph(issue_title), styles["Heading4"]))
            story.append(Paragraph(
                _safe_paragraph(f"Line: {issue.get('line', 'unknown')}"),
                normal_style
            ))
            story.append(Paragraph(
                _safe_paragraph(f"Category: {issue.get('category', 'Unknown')}"),
                normal_style
            ))
            story.append(Paragraph(
                _safe_paragraph(f"Explanation: {issue.get('explanation', '')}"),
                normal_style
            ))
            story.append(Paragraph(
                _safe_paragraph(f"Recommendation: {issue.get('recommendation', '')}"),
                normal_style
            ))
            story.append(Spacer(1, 6))

    story.append(Paragraph("Suggested Improvements", heading_style))

    improvements = result.get("improvements", [])

    if improvements:
        for item in improvements:
            story.append(Paragraph(_safe_paragraph(f"- {item}"), normal_style))
    else:
        story.append(Paragraph("No improvements suggested.", normal_style))

    story.append(Paragraph("Tests to Add", heading_style))

    tests_to_add = result.get("tests_to_add", [])

    if tests_to_add:
        for item in tests_to_add:
            story.append(Paragraph(_safe_paragraph(f"- {item}"), normal_style))
    else:
        story.append(Paragraph("No test suggestions.", normal_style))

    story.append(PageBreak())

    story.append(Paragraph("Static Analyzer Findings", heading_style))
    static_text = json.dumps(static_findings, indent=2)
    story.append(Preformatted(_wrap_code(static_text), code_style))

    story.append(Paragraph("Original Code", heading_style))
    story.append(Preformatted(_wrap_code(original_code), code_style))

    doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data