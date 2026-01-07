from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

resp = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="OK"
)

print(resp.text)
