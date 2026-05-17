# =====================================================
# CELERY WORKER (PDF INGESTION PIPELINE)
# =====================================================

from celery import Celery

celery = Celery(
    "ai_tasks",
    broker="redis://redis:6379/0"
)

@celery.task
def process_pdf_task(file_url: str, institution_id: str):

    print(f"Processing PDF: {file_url}")

    # STEP 1: download PDF
    # STEP 2: extract text
    # STEP 3: chunk text
    # STEP 4: create embeddings
    # STEP 5: store in pgvector

    return {"status": "processed"}