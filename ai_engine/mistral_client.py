import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Explain clearly in detail with steps and examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()

        if not answer:
            return "AI returned empty response."

        return answer

    except Exception as e:
        print("AI ERROR:", e)
        return "AI engine unavailable."