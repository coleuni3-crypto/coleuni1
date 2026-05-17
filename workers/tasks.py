# =====================================================
# COLEUNI BACKGROUND TASKS (PDF + VIDEO PROCESSING)
# =====================================================

from celery import Celery
import requests
import tempfile
import os
import subprocess

from vector_store import store_embedding

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# CELERY INIT
# =====================================================
celery = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# =====================================================
# TEXT CHUNKING
# =====================================================
def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

# =====================================================
# PDF PROCESSING
# =====================================================
@celery.task
def process_pdf_task(file_url, institution_id):

    try:
        import PyPDF2

        response = requests.get(file_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(response.content)
            pdf_path = f.name

        reader = PyPDF2.PdfReader(pdf_path)

        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""

        chunks = chunk_text(full_text)

        for chunk in chunks:
            store_embedding(institution_id, chunk)

        return "PDF processed successfully"

    except Exception as e:
        return f"PDF processing failed: {e}"

# =====================================================
# VIDEO PROCESSING (TRANSCRIBE → EMBED)
# =====================================================
@celery.task
def process_video_task(video_url, institution_id):

    try:
        # Download video
        video_data = requests.get(video_url).content

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(video_data)
            video_path = f.name

        # Extract audio
        audio_path = video_path.replace(".mp4", ".wav")

        subprocess.run([
            "ffmpeg", "-i", video_path, audio_path
        ])

        # Transcribe audio
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )

        text = transcript.text

        chunks = chunk_text(text)

        for chunk in chunks:
            store_embedding(institution_id, chunk)

        return "Video processed successfully"

    except Exception as e:
        return f"Video processing failed: {e}"