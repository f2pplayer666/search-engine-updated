# test_ai.py
from groq import Groq

client = Groq(api_key="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")

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain photosynthesis"}]
)

print(response.choices[0].message.content)