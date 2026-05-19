from rag.vector_store import search_vectors


# =====================================================
# 🧠 RAG CONTEXT RETRIEVAL ENGINE (V4.1)
# =====================================================
def retrieve_context(institution_id, query, max_length: int = 3000):

    if not query or len(query.strip()) < 2:
        return {
            "context": "",
            "sources": []
        }

    results = search_vectors(institution_id, query, top_k=8) or []

    if not results:
        return {
            "context": "",
            "sources": []
        }

    # ==============================
    # 📊 SORT BY RELEVANCE SCORE
    # ==============================
    results = sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    context_chunks = []
    sources = []
    total_length = 0

    for r in results:

        content = r.get("content", "")
        score = r.get("score", 0)

        if not content or len(content.strip()) < 5:
            continue

        # skip very low relevance noise
        if score < 0.15:
            continue

        # prevent context overflow
        if total_length + len(content) > max_length:
            break

        context_chunks.append(content.strip())
        total_length += len(content)

        sources.append({
            "content": content.strip(),
            "score": round(score, 4),
            "video_url": r.get("video_url"),
            "timestamp": r.get("start_time")
        })

    # ==============================
    # 🧠 FINAL CONTEXT BUILD
    # ==============================
    context = "\n\n".join(context_chunks)

    return {
        "context": context,
        "sources": sources,
        "chunks_used": len(context_chunks),
        "engine": "rag-context-v4.1"
    }