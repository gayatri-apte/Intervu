import os

from dotenv import load_dotenv
from google import genai


load_dotenv("backend/.env")

api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")

print("Model:", model)
print("API key loaded:", bool(api_key))

if not api_key:
    raise ValueError("LLM_API_KEY is missing")

if not model:
    raise ValueError("LLM_MODEL is missing")

client = genai.Client(api_key=api_key)

print("Sending request...")

response = client.models.generate_content(
    model=model,
    contents="Reply with exactly: GEMINI_TEST_OK",
)

print("Response received:")
print(response.text)