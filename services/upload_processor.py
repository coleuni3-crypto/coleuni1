import os
from openai import OpenAI
from core.supabase_http import insert

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 📂 MAIN PROCESSOR
# =====================================================
async def process_upload(file_text: str, title: str, topic: str, user):

    institution_id = user["institution_id"]
    teacher_id = user["user_id"]

    # =================================================
    # 🧠 1. AI CONTENT UNDERSTANDING
    # =================================================
    prompt = f"""
You are ColeUni AI Education Engine.

Analyze this learning material:

TITLE: {title}
TOPIC: {topic}

CONTENT:
{file_text}

TASKS:
1. Summarize in simple student language
2. Extract key concepts
3. Create flashcards (Q&A format)
4. Generate 5 exam questions
5. Explain why this topic is important in syllabus
6. Suggest weak areas students may struggle with

Return JSON format:
{
  "summary": "",
  "key_concepts": [],
  "flashcards": [
    {"q": "", "a": ""}
  ],
  "quiz": [
    {"q": "", "a": ""}
  ],
  "importance": "",
  "weak_points": []
}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert education AI."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_output = res.choices[0].message.content


    # =================================================
    # 💾 2. SAVE TO SUPABASE
    # =================================================
    record = insert("learning_materials", {
        "title": title,
        "topic": topic,
        "content_raw": file_text,
        "ai_output": ai_output,
        "teacher_id": teacher_id,
        "institution_id": institution_id
    })


    # =================================================
    # 📊 3. RETURN RESULT
    # =================================================
    return {
        "success": True,
        "message": "AI processing complete",
        "material_id": record["id"],
        "ai": ai_output
    }