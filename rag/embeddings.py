import os
import time
import random
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 🪵 LOGGING
# ==============================
logger = logging.getLogger("coleuni.embeddings")


# =====================================================
# 🧼 NORMALIZE TEXT (CONSISTENCY LAYER)
# =====================================================
def _clean_text(text: str) -> str:

    if not text:
        return ""

    return " ".join(text.strip().split())


# =====================================================
# 📊 EMBEDDING GENERATION (PRODUCTION SAFE V4)
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

            if not embedding:
                return None

            return embedding

        except Exception as e:

            wait_time = (2 ** attempt) + random.uniform(0, 0.5)

            logger.warning(
                f"[EMBEDDING ERROR] attempt={attempt+1} error={str(e)} retry_in={wait_time:.2f}s"
            )

            time.sleep(wait_time)

    logger.error("[EMBEDDING FAILED] All retries exhausted")
    return None