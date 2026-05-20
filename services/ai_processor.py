import fitz  # PyMuPDF
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


# =====================================================
# 📄 EXTRACT TEXT FROM PDF (ROBUST VERSION)
# =====================================================
def extract_text_from_pdf(file_bytes: bytes):

    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages_text = []

    for page in doc:
        text = page.get_text()
        if text:
            pages_text.append(text)

    full_text = "\n".join(pages_text)

    return full_text[:20000]  # safety limit for SaaS scaling


# =====================================================
# 🧠 SAFE AI CALL
# =====================================================
def safe_ai_call(messages):

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4
        )

        content = res.choices[0].message.content

        try:
            return json.loads(content)
        except:
            return {
                "notes": content,
                "summary": content[:300],
                "flashcards": [],
                "quiz": [],
                "audio_text": content
            }

    except Exception as e:
        return {
            "error": str(e),
            "notes": "",
            "summary": "",
            "flashcards": [],
            "quiz": [],
            "audio_text": ""
        }


# =====================================================
# 🧠 AI LEARNING PACKAGE GENERATOR (V2 CORE)
# =====================================================
def generate_learning_package(text: str):

    if not text:
        return {
            "success": False,
            "error": "No text provided"
        }

    # =========================
    # 📦 SAFE INPUT LIMIT
    # =========================
    clean_text = text[:12000]

    # =========================
    # 🌍 AI PROMPT ENGINE
    # =========================
    prompt = f"""
You are ColeUni AI Learning Engine.

Convert this study material into STRICT JSON ONLY:

{{
  "summary": "short exam-focused summary",
  "notes": "structured study notes with headings",
  "key_points": ["point1", "point2", "point3"],

  "flashcards": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ],

  "quiz": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "..."
    }}
  ],

  "audio_text": "simple teaching explanation for students"
}}

RULES:
- Make it easy for exam revision
- Focus on understanding, not copying text
- Extract real concepts
- Keep language simple

MATERIAL:
{clean_text}
"""

    result = safe_ai_call([
        {
            "role": "system",
            "content": "You are a strict educational AI. Output ONLY valid JSON."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    # =========================
    # 🧱 SAFE RESPONSE STRUCTURE
    # =========================
    return {
        "success": True,
        "summary": result.get("summary", ""),
        "notes": result.get("notes", ""),
        "key_points": result.get("key_points", []),
        "flashcards": result.get("flashcards", []),
        "quiz": result.get("quiz", []),
        "audio_text": result.get("audio_text", ""),
        "engine": "coleuni-learning-pipeline-v2"
    }