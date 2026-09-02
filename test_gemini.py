import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=api_key,
)


interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Reply with exactly: Gemini connection successful",
)


print(interaction.output_text)