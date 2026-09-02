import json
import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


def analyze_compliance(requirements, solution_text):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    requirements_data = []

    for requirement in requirements:

        requirements_data.append(
            {
                "id": requirement.id,
                "requirement_text": requirement.requirement_text,
            }
        )

    prompt = f"""
You are an expert tender compliance analyst.

Analyze the proposed project solution against ALL tender
requirements provided below.

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
            "status": "compliant",
            "confidence_score": 85,
            "explanation": "Short explanation"
        }}
    ]
}}

IMPORTANT RULES:

1. Return exactly one result for EVERY requirement.

2. requirement_id must match the original requirement ID.

3. STATUS must be exactly one of:

- compliant
- partial
- non_compliant

4. confidence_score must be a number between 0 and 100.

5. explanation should briefly explain why the requirement
is compliant, partially compliant, or non-compliant.

6. Do not return markdown.

7. Do not add any text outside the JSON.
"""

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            response_text = response.text.strip()

            # Remove markdown code fences
            if response_text.startswith("```"):

                lines = response_text.splitlines()

                if lines[0].startswith("```"):
                    lines = lines[1:]

                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]

                response_text = "\n".join(
                    lines
                ).strip()

            result = json.loads(
                response_text
            )

            return result

        except Exception as error:

            error_message = str(
                error
            )

            print(
                f"Gemini API attempt "
                f"{attempt + 1} failed:",
                error,
            )

            # Do NOT retry if API quota is exhausted
            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "quota" in error_message.lower()
            ):

                raise Exception(
                    "Gemini API quota has been exhausted. "
                    "Please wait for the quota to reset or "
                    "check your Gemini API plan and billing."
                ) from error

            # Retry only temporary server errors
            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                if attempt < max_retries - 1:

                    time.sleep(
                        5 * (attempt + 1)
                    )

                    continue

            # Stop retrying for other errors
            raise Exception(
                "AI analysis failed. "
                "Please try again later."
            ) from error

    raise Exception(
        "AI service is temporarily unavailable."
    )