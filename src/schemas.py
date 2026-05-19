CODE_REVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {
            "type": "string"
        },
        "language": {
            "type": "string"
        },
        "purpose": {
            "type": "string"
        },
        "logic_explanation": {
            "type": "string"
        },
        "complexity": {
            "type": "string"
        },
        "risk_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "line": {
                        "type": "string"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High", "Critical"]
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "Bug",
                            "Security",
                            "Performance",
                            "Code Smell",
                            "Maintainability",
                            "Style"
                        ]
                    },
                    "title": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "recommendation": {
                        "type": "string"
                    }
                },
                "required": [
                    "line",
                    "severity",
                    "category",
                    "title",
                    "explanation",
                    "recommendation"
                ]
            }
        },
        "improvements": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "tests_to_add": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "annotated_code": {
            "type": "string"
        },
        "refactored_code": {
            "type": "string"
        }
    },
    "required": [
        "summary",
        "language",
        "purpose",
        "logic_explanation",
        "complexity",
        "risk_score",
        "issues",
        "improvements",
        "tests_to_add",
        "annotated_code",
        "refactored_code"
    ]
}