from groq import Groq
import os

def ask_ai(prompt):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Explain clearly with steps and examples."},
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
        return None