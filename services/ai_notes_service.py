# =====================================================
# 🧠 AI NOTES GENERATOR (MVP)
# Later replace with OpenAI
# =====================================================

def generate_ai_notes(text: str):

    # shorten huge PDFs for MVP
    short_text = text[:3000]

    # =================================================
    # SIMPLE AI LOGIC (MVP)
    # =================================================
    notes = f"""
    AI Study Notes

    Summary:
    {short_text[:1000]}

    Important Concepts:
    - Understanding the core topic
    - Key academic principles
    - Exam-focused learning
    """

    flashcards = [
        {
            "question": "What is the main topic?",
            "answer": short_text[:120]
        },
        {
            "question": "Why is this topic important?",
            "answer": "It is important for understanding exam concepts."
        }
    ]

    quiz = [
        {
            "question": "What is the focus of this material?",
            "options": [
                "Main academic concept",
                "Random data",
                "Entertainment",
                "None"
            ],
            "answer": "Main academic concept"
        }
    ]

    audio_text = f"""
    Welcome to ColeUni AI Learning.
    Today's lesson discusses:
    {short_text[:500]}
    """

    return {
        "notes": notes,
        "flashcards": flashcards,
        "quiz": quiz,
        "audio_text": audio_text
    }