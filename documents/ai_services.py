import json

from django.conf import settings
from google import genai


def extract_requirements_with_ai(tender_text):

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )

    prompt = f"""
You are an AI assistant for tender compliance analysis.

Your task is to extract important requirements from the tender document.

Identify requirements related to:

- Technical requirements
- Financial requirements
- Eligibility requirements
- Legal or compliance requirements
- Other important requirements

Return ONLY valid JSON.

Use exactly this format:

{{
    "requirements": [
        {{
            "category": "technical",
            "requirement_text": "Clear and concise requirement",
            "is_mandatory": true
        }}
    ]
}}

Rules:

1. category must be one of:
   technical
   financial
   eligibility
   legal
   other

2. requirement_text must contain one complete requirement.

3. is_mandatory must be true for mandatory requirements.

4. Do not add explanations outside JSON.

Tender Document:

{tender_text}
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    response_text = interaction.output_text

    return json.loads(response_text)