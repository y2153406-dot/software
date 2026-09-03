import json
import os

from google import genai
from dotenv import load_dotenv


load_dotenv()


def analyze_risks(
    requirements,
    solution_text,
):

    client = genai.Client(
        api_key=os.getenv(
            "GEMINI_API_KEY"
        )
    )

    requirements_data = []

    for requirement in requirements:

        requirements_data.append(
            {
                "id": requirement.id,
                "requirement_text": (
                    requirement.requirement_text
                ),
                "is_mandatory": (
                    requirement.is_mandatory
                ),
                "category": (
                    requirement.category
                ),
            }
        )

    prompt = f"""
You are an expert tender risk analyst.

Analyze ALL tender requirements against the
proposed project solution.

Your task is to identify the implementation
and compliance risk for every requirement.

TENDER REQUIREMENTS:

{json.dumps(requirements_data, indent=2)}

PROJECT SOLUTION:

{solution_text}

Analyze every requirement individually.

Return ONLY valid JSON in this exact format:

{{
    "results": [
        {{
            "requirement_id": 1,
            "risk_level": "high",
            "risk_score": 85,
            "explanation": "Short explanation of the risk.",
            "recommendation": "Short recommendation to reduce the risk."
        }}
    ]
}}

IMPORTANT RULES:

1. Return exactly one result for EVERY requirement.

2. requirement_id must match the original requirement ID.

3. risk_level must be exactly one of:

- low
- medium
- high

4. risk_score must be a number between 0 and 100.

5. A higher risk_score means greater risk.

6. Consider the following while analyzing risk:

- Missing solution features
- Partial compliance
- Mandatory requirements
- Technical complexity
- Implementation difficulty
- Eligibility issues
- Financial constraints
- Legal requirements

7. explanation must clearly explain the risk.

8. recommendation must explain how the project
team can reduce the risk.

9. Do not return markdown.

10. Do not add any text outside the JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    response_text = response.text.strip()

    result = json.loads(
        response_text
    )

    return result