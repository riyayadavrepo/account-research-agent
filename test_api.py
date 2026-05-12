import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://chat.dartmouth.edu/api",
    api_key=os.getenv("DARTMOUTH_CHAT_API_KEY")
)

response = client.chat.completions.create(
    model="anthropic.claude-sonnet-4-5-20250929",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'hello, agent builder' in 5 words or fewer."}]
)

print(response.choices[0].message.content)
