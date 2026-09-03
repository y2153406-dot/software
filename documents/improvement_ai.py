import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate_improvement_suggestions(
    failed_results,
    solution_text,
):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    requirements_data = []

    for result in failed_results:

        requirements_data.append(
            {
                "requirement_id": result.requirement.id,
                "requirement_text": (
                    result.requirement.requirement_text
                ),
                "current_status": result.status,
                "current_analysis": result.explanation,
            }
        )

    prompt = f"""
You are an expert tender compliance consultant.

Your task is to suggest practical improvements to a project
solution so that it can better satisfy tender requirements.

TENDER REQUIREMENTS THAT NEED IMPROVEMENT:

{json.dumps(requirements_data, indent=2)}

CURRENT PROJECT SOLUTION:

{solution_text}

Generate one practical improvement suggestion for every
requirement provided.

Return ONLY valid JSON in this exact format:

{{
    "suggestions": [
        {{
            "requirement_id": 1,
            "suggestion": "Specific practical improvement",
            "priority": "high"
        }}
    ]
}}

IMPORTANT RULES:

1. Return exactly one suggestion for EVERY requirement.

2. requirement_id must match the original requirement ID.

3. priority must be exactly one of:

- high
- medium
- low

4. The suggestion must be specific and actionable.

5. Explain what should be added, modified, or improved
in the project solution.

6. Do not return markdown.

7. Do not add any text outside the JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    response_text = response.text.strip()

    return json.loads(
        response_text
    )