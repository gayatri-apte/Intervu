import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv("backend/.env")

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

print("Model:", model)
print("API key loaded:", bool(api_key))

if not api_key:
    raise ValueError("GROQ_API_KEY is not set.")

if not model:
    raise ValueError("GROQ_MODEL is not set.")


client = Groq(api_key=api_key)

print("Sending request...")

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Reply with exactly: GROQ_TEST_OK"
        }
    ],
)

print("Response:")
print(response.choices[0].message.content)