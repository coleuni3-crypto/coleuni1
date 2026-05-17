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

    if not embedding:
        return None

    return insert("embeddings", {
        "institution_id": institution_id,
        "content": content,
        "embedding": embedding
    })


# =====================================================
# 📐 COSINE SIMILARITY ENGINE
# =====================================================
def cosine_similarity(a, b):

    if not a or not b:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# =====================================================
# 🔍 SMART VECTOR SEARCH (RANKED RAG ENGINE)
# =====================================================
def search_vectors(institution_id: str, query: str, top_k: int = 5):

    query_embedding = get_embedding(query)

    if not query_embedding:
        return []

    data = select("embeddings", {
        "institution_id": institution_id
    }) or []

    scored_results = []

    for row in data:

        content = row.get("content", "")
        embedding = row.get("embedding")

        if not content or not embedding:
            continue

        score = cosine_similarity(query_embedding, embedding)

        scored_results.append({
            "content": content,
            "video_url": row.get("video_url"),
            "start_time": row.get("start_time"),
            "score": round(score, 4)
        })

    # sort by relevance
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    return scored_results[:top_k]