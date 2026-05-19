import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# 🧠 REAL AI LEARNING ENGINE
# =====================================================
def generate_ai_lesson(text: str):

    prompt = f"""
    You are an expert tutor.

    Convert the following content into:

    1. Simple study notes
    2. Flashcards (Q/A format JSON list)
    3. Quiz (MCQ with answers JSON list)
    4. Short audio explanation text

    CONTENT:
    {text}

    Return ONLY JSON with keys:
    notes, flashcards, quiz, audio_text
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a world-class AI tutor."},
            {"role": "user", "content": prompt}
        ]
    )

    return res.choices[0].message.content


# =====================================================
# 🧠 STUDENT ADAPTIVE EXPLANATION
# =====================================================
def explain_difficult_topic(topic: str, level: str = "basic"):

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a patient teacher that adapts to student level."
            },
            {
                "role": "user",
                "content": f"""
                Explain this topic: {topic}
                Student level: {level}

                Make it simple, step-by-step, with examples.
                """
            }
        ]
    )

    return res.choices[0].message.content