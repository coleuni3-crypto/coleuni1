from rag.vector_store import search_vectors


# =====================================================
# 🧠 RAG CONTEXT RETRIEVAL ENGINE
# =====================================================
def retrieve_context(institution_id, query, max_length: int = 3000):

    results = search_vectors(institution_id, query, top_k=5) or []

    if not results:
        return {
            "context": "",
            "sources": []
        }

    context_chunks = []
    sources = []

    total_length = 0

    for r in results:

        content = r.get("content", "")

        if not content:
            continue

        # avoid overflowing GPT context window
        if total_length + len(content) > max_length:
            break

        context_chunks.append(content)
        total_length += len(content)

        sources.append({
            "content": content,
            "score": r.get("score", 0),
            "video_url": r.get("video_url"),
            "timestamp": r.get("start_time")
        })

    context = "\n\n".join(context_chunks)

    return {
        "context": context,
        "sources": sources
    }