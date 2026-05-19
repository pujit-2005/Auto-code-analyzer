import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.schemas import CODE_REVIEW_SCHEMA


load_dotenv()


SYSTEM_PROMPT = (
    "You are an expert senior software engineer and secure code reviewer. "
    "Your job is to explain code, detect bugs, vulnerabilities, code smells, "
    "maintainability problems, and performance issues. Suggest practical fixes, "
    "add useful inline comments, and provide a cleaner refactored version. "
    "Do not invent line numbers. If unsure, use 'unknown'. "
    "Focus only on defensive code review."
)


def analyze_code_with_llm(code: str, language: str, static_findings: list):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Create a .env file in the main project folder."
        )

    client = OpenAI(api_key=api_key)

    user_prompt = (
        "Analyze this source code.\n\n"
        f"Language: {language}\n\n"
        "Static analyzer findings:\n"
        f"{json.dumps(static_findings, indent=2)}\n\n"
        "Source code:\n"
        f"{code}\n\n"
        "Return a complete structured review."
    )

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "code_review",
                "schema": CODE_REVIEW_SCHEMA,
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)