# Auto Code Analyzer

## Live Demo

https://auto-code-analyzer-pujit.streamlit.app/


Auto Code Analyzer is a Streamlit-based code review assistant that analyzes source code for bugs, security issues, code smells, and maintainability problems.

## Features

- Upload or paste source code
- Detect programming language
- Run static analysis using Bandit and Semgrep
- Rule-based vulnerability detection
- Severity filter
- Dashboard charts
- Markdown and JSON report download
- Optional OpenAI API-based AI analysis
- Fallback mode when API quota is unavailable

## Tech Stack

- Python
- Streamlit
- Pandas
- Bandit
- Semgrep
- OpenAI API

## How to Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py