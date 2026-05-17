import os
from openai import OpenAI
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# NORMALIZE TEXT (IMPORTANT FOR CONSISTENCY)
# =====================================================
def _clean_text(text: str) -> str:

    if not text:
        return ""

    return text.strip().replace("\n", " ")


# =====================================================
# EMBEDDING GENERATION (PRODUCTION SAFE)
# =====================================================
def get_embedding(text: str, retries: int = 3):

    text = _clean_text(text)

    if not text or len(text) < 2:
        return None

    for attempt in range(retries):

        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embedding = response.data[0].embedding

            # Optional normalization (helps cosine similarity stability)
            return embedding

        except Exception as e:
            print(f"[EMBED ERROR] Attempt {attempt + 1}: {e}")
            time.sleep(1)

    return None