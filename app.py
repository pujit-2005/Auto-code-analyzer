import streamlit as st
import pandas as pd

from src.language_detector import detect_language
from src.static_analyzer import run_static_analysis
from src.llm_analyzer import analyze_code_with_llm
from src.report_generator import (
    generate_markdown_report,
    generate_json_report,
    generate_pdf_report,
)
from src.rule_based_analyzer import rule_based_review


st.set_page_config(
    page_title="Auto Code Analyzer",
    page_icon="🧠",
    layout="wide"
)


def get_severity_color(severity: str):
    severity = str(severity)

    if severity == "Critical":
        return "🔴"
    if severity == "High":
        return "🟠"
    if severity == "Medium":
        return "🟡"
    if severity == "Low":
        return "🟢"

    return "⚪"


def create_issues_dataframe(issues: list):
    if not issues:
        return pd.DataFrame(
            columns=[
                "Severity",
                "Category",
                "Line",
                "Title",
                "Explanation",
                "Recommendation"
            ]
        )

    rows = []

    for issue in issues:
        rows.append(
            {
                "Severity": issue.get("severity", "Unknown"),
                "Category": issue.get("category", "Unknown"),
                "Line": issue.get("line", "unknown"),
                "Title": issue.get("title", "Untitled issue"),
                "Explanation": issue.get("explanation", ""),
                "Recommendation": issue.get("recommendation", "")
            }
        )

    return pd.DataFrame(rows)


def show_issue_card(issue):
    severity = issue.get("severity", "Low")
    title = issue.get("title", "Untitled issue")
    emoji = get_severity_color(severity)

    if severity in ["Critical", "High"]:
        st.error(f"{emoji} {severity}: {title}")
    elif severity == "Medium":
        st.warning(f"{emoji} {severity}: {title}")
    else:
        st.info(f"{emoji} {severity}: {title}")

    st.write(f"**Line:** {issue.get('line')}")
    st.write(f"**Category:** {issue.get('category')}")
    st.write(f"**Explanation:** {issue.get('explanation')}")
    st.write(f"**Recommendation:** {issue.get('recommendation')}")


st.title("🧠 Auto Code Analyzer")

st.write(
    "Upload or paste source code to get security review, bug detection, "
    "rule-based analysis, static analyzer findings, downloadable reports, "
    "and optional AI-powered explanations."
)


with st.sidebar:
    st.header("⚙️ Settings")

    run_static = st.checkbox("Run static analyzers", value=True)

    analysis_depth = st.selectbox(
        "Analysis depth",
        ["Quick Review", "Deep Review"]
    )

    st.divider()

    st.subheader("About")
    st.write(
        "This app uses Bandit, Semgrep, custom rules, and optional OpenAI API analysis."
    )

    st.warning(
        "Do not upload private production code unless you are allowed to send it to an AI API."
    )

    if st.button("Clear Analysis"):
        st.session_state.clear()
        st.rerun()


input_tab, sample_tab = st.tabs(["📤 Upload / Paste Code", "🧪 Sample Test Code"])


with input_tab:
    uploaded_file = st.file_uploader(
        "Upload a source code file",
        type=[
            "py", "js", "jsx", "ts", "tsx", "java", "cpp", "c",
            "cs", "go", "rb", "php", "rs", "html", "css", "sql"
        ]
    )

    manual_code = st.text_area(
        "Or paste your code here",
        height=300,
        placeholder="Paste your code here..."
    )


with sample_tab:
    st.write("Use this sample code to test whether the analyzer detects vulnerabilities.")

    sample_code = """import sqlite3
import os

password = "admin123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    result = conn.execute(query)
    return result.fetchall()

def delete_file(filename):
    os.system("rm " + filename)

name = input("Enter username: ")
print(get_user(name))
"""

    st.code(sample_code, language="python")

    if st.button("Use sample vulnerable code"):
        st.session_state["sample_code"] = sample_code


filename = "pasted_code.py"
code = ""


if uploaded_file is not None:
    max_size_mb = 2
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > max_size_mb:
        st.error("File too large. Please upload a file smaller than 2 MB.")
        st.stop()

    filename = uploaded_file.name
    code = uploaded_file.read().decode("utf-8", errors="ignore")

elif manual_code.strip():
    code = manual_code
    filename = "pasted_code.py"

elif "sample_code" in st.session_state:
    code = st.session_state["sample_code"]
    filename = "vulnerable_python.py"


language = detect_language(filename, code)


st.divider()

metric_col1, metric_col2, metric_col3 = st.columns(3)

metric_col1.metric("Detected Language", language)
metric_col2.metric("Input Type", "File" if uploaded_file else "Pasted / Sample Code")
metric_col3.metric("Static Analysis", "Enabled" if run_static else "Disabled")


if code:
    with st.expander("Preview Code"):
        st.code(code, language=language.lower())


analyze_button = st.button("Analyze Code", type="primary")


if analyze_button:
    if not code.strip():
        st.error("Please upload, paste, or select sample code first.")
        st.stop()

    with st.spinner("Analyzing code..."):
        static_findings = []
        analysis_mode = "AI + Static Analysis"

        if run_static:
            static_findings = run_static_analysis(code, filename)

        try:
            result = analyze_code_with_llm(
                code=code,
                language=language,
                static_findings=static_findings
            )

            st.success("AI-powered analysis completed successfully.")

        except Exception:
            analysis_mode = "Static + Rule-Based Analysis"

            st.info(
                "AI analysis is currently unavailable. "
                "Using local static and rule-based analysis instead."
            )

            result = rule_based_review(
                code=code,
                language=language,
                static_findings=static_findings
            )

        st.session_state["analysis_result"] = result
        st.session_state["static_findings"] = static_findings
        st.session_state["original_code"] = code
        st.session_state["language"] = language
        st.session_state["analysis_mode"] = analysis_mode


if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    static_findings = st.session_state["static_findings"]
    original_code = st.session_state["original_code"]
    language = st.session_state.get("language", "text")
    analysis_mode = st.session_state.get("analysis_mode", "Unknown")

    issues = result.get("issues", [])
    issues_df = create_issues_dataframe(issues)

    st.divider()

    st.header("📊 Analysis Results")

    result_col1, result_col2, result_col3, result_col4, result_col5 = st.columns(5)

    result_col1.metric("Risk Score", f"{result.get('risk_score', 0)}/100")
    result_col2.metric("Issues Found", len(issues))
    result_col3.metric("Static Findings", len(static_findings))

    critical_count = len(
        [issue for issue in issues if issue.get("severity") == "Critical"]
    )

    result_col4.metric("Critical Issues", critical_count)
    result_col5.metric("Analysis Mode", analysis_mode)

    overview_tab, issues_tab, dashboard_tab, code_tab, architecture_tab, report_tab = st.tabs(
        [
            "📌 Overview",
            "🐞 Issues",
            "📈 Dashboard",
            "💻 Code Review",
            "🏗️ Architecture",
            "📥 Reports"
        ]
    )

    with overview_tab:
        st.subheader("Summary")
        st.write(result.get("summary"))

        st.subheader("Purpose")
        st.write(result.get("purpose"))

        st.subheader("Logic Explanation")
        st.write(result.get("logic_explanation"))

        st.subheader("Complexity")
        st.write(result.get("complexity"))

        st.subheader("Suggested Improvements")

        improvements = result.get("improvements", [])

        if improvements:
            for item in improvements:
                st.write(f"- {item}")
        else:
            st.write("No improvements suggested.")

        st.subheader("Tests to Add")

        tests_to_add = result.get("tests_to_add", [])

        if tests_to_add:
            for item in tests_to_add:
                st.write(f"- {item}")
        else:
            st.write("No test suggestions.")

    with issues_tab:
        st.subheader("Detected Issues")

        if issues_df.empty:
            st.success("No major issues detected.")
        else:
            available_severities = ["Critical", "High", "Medium", "Low"]

            selected_severities = st.multiselect(
                "Filter by severity",
                options=available_severities,
                default=available_severities
            )

            filtered_issues = [
                issue for issue in issues
                if issue.get("severity", "Low") in selected_severities
            ]

            st.write(f"Showing **{len(filtered_issues)}** issue(s).")

            if not filtered_issues:
                st.info("No issues match the selected severity filter.")
            else:
                for issue in filtered_issues:
                    show_issue_card(issue)
                    st.divider()

            with st.expander("View issues as table"):
                filtered_df = create_issues_dataframe(filtered_issues)
                st.dataframe(filtered_df, use_container_width=True)

    with dashboard_tab:
        st.subheader("Dashboard Charts")

        if issues_df.empty:
            st.success("No issue data available for charts.")
        else:
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.write("### Issues by Severity")

                severity_order = ["Critical", "High", "Medium", "Low"]

                severity_counts = (
                    issues_df["Severity"]
                    .value_counts()
                    .reindex(severity_order)
                    .fillna(0)
                    .astype(int)
                )

                st.bar_chart(severity_counts)

            with chart_col2:
                st.write("### Issues by Category")

                category_counts = (
                    issues_df["Category"]
                    .value_counts()
                    .sort_values(ascending=False)
                )

                st.bar_chart(category_counts)

            st.write("### Issue Table")
            st.dataframe(issues_df, use_container_width=True)

            st.write("### Static Analyzer Summary")

            if static_findings:
                static_df = pd.DataFrame(static_findings)

                if "tool" in static_df.columns:
                    tool_counts = static_df["tool"].value_counts()
                    st.bar_chart(tool_counts)

                st.dataframe(static_df, use_container_width=True)
            else:
                st.info("No static analyzer findings available.")

    with code_tab:
        st.subheader("Annotated Code")

        st.code(
            result.get("annotated_code", ""),
            language=language.lower()
        )

        st.subheader("Refactored Code")

        st.code(
            result.get("refactored_code", ""),
            language=language.lower()
        )

        st.subheader("Original Code")

        st.code(
            original_code,
            language=language.lower()
        )

    with architecture_tab:
        st.subheader("System Architecture")

        st.write(
            "Auto Code Analyzer uses a layered architecture. "
            "The app can work with or without AI API access."
        )

        st.code(
            """User uploads or pastes code
        ↓
Streamlit frontend reads the code
        ↓
Language detector identifies the programming language
        ↓
Static analyzers run locally
        ↓
Rule-based analyzer checks common vulnerability patterns
        ↓
Optional OpenAI API analysis generates deeper explanations
        ↓
Results are displayed in tabs
        ↓
Reports are exported as Markdown, JSON, and PDF""",
            language="text"
        )

        st.subheader("Main Components")

        architecture_data = pd.DataFrame(
            [
                {
                    "Component": "Streamlit UI",
                    "Purpose": "Provides upload, paste, tabs, charts, filters, and downloads."
                },
                {
                    "Component": "Language Detector",
                    "Purpose": "Detects programming language from file extension or code patterns."
                },
                {
                    "Component": "Static Analyzer",
                    "Purpose": "Runs Bandit and Semgrep to find known security issues."
                },
                {
                    "Component": "Rule-Based Analyzer",
                    "Purpose": "Detects common risky patterns like hardcoded passwords, SQL injection, and unsafe shell commands."
                },
                {
                    "Component": "OpenAI Analyzer",
                    "Purpose": "Optionally generates AI explanations, refactoring suggestions, and deeper review."
                },
                {
                    "Component": "Report Generator",
                    "Purpose": "Exports analysis results as Markdown, JSON, and PDF."
                },
            ]
        )

        st.dataframe(architecture_data, use_container_width=True)

        st.subheader("Fallback Design")

        st.info(
            "If OpenAI API quota is unavailable, the app automatically switches "
            "to Static + Rule-Based Analysis so the project still works."
        )

    with report_tab:
        st.subheader("Download Reports")

        markdown_report = generate_markdown_report(
            result=result,
            static_findings=static_findings,
            original_code=original_code
        )

        json_report = generate_json_report(
            result=result,
            static_findings=static_findings,
            original_code=original_code
        )

        pdf_report = generate_pdf_report(
            result=result,
            static_findings=static_findings,
            original_code=original_code
        )

        report_col1, report_col2, report_col3 = st.columns(3)

        with report_col1:
            st.download_button(
                label="Download Markdown Report",
                data=markdown_report,
                file_name="auto_code_analysis_report.md",
                mime="text/markdown"
            )

        with report_col2:
            st.download_button(
                label="Download JSON Report",
                data=json_report,
                file_name="auto_code_analysis_report.json",
                mime="application/json"
            )

        with report_col3:
            st.download_button(
                label="Download PDF Report",
                data=pdf_report,
                file_name="auto_code_analysis_report.pdf",
                mime="application/pdf"
            )

        with st.expander("Static Analyzer Raw Findings"):
            st.json(static_findings)