from core.supabase_http import insert, select
from rag.embeddings import get_embedding
import math


# =====================================================
# 🧠 STORE EMBEDDING (SAFE + VALIDATED)
# =====================================================
def store_embedding(institution_id: str, content: str):

    if not content or len(content.strip()) < 5:
        return None

    embedding = get_embedding(content)

    if not embedding or not isinstance(embedding, list):
        return None

    return insert("embeddings", {
        "institution_id": institution_id,
        "content": content,
        "embedding": embedding
    })


# =====================================================
# 📐 COSINE SIMILARITY ENGINE (V4 SAFE)
# =====================================================
def cosine_similarity(a, b):

    if not a or not b:
        return 0.0

    if len(a) != len(b):
        return 0.0

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


# =====================================================
# 🔍 SMART VECTOR SEARCH (RAG ENGINE V4)
# =====================================================
def search_vectors(institution_id: str, query: str, top_k: int = 5):

    if not query or len(query.strip()) < 2:
        return []

    query_embedding = get_embedding(query)

    if not query_embedding or not isinstance(query_embedding, list):
        return []

    data = select("embeddings", {
        "institution_id": institution_id
    }) or []

    scored_results = []

    for row in data:

        try:
            content = row.get("content", "")
            embedding = row.get("embedding")

            if not content or not embedding:
                continue

            # ensure embedding is valid list
            if not isinstance(embedding, list):
                continue

            score = cosine_similarity(query_embedding, embedding)

            # skip irrelevant results early
            if score <= 0:
                continue

            scored_results.append({
                "content": content,
                "video_url": row.get("video_url"),
                "start_time": row.get("start_time"),
                "score": round(score, 4)
            })

        except Exception:
            continue

    # sort by relevance
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    return scored_results[:top_k]