from pathlib import Path
import pickle

import faiss
import numpy as np
import ollama


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_DIR = Path("vector_db")

INDEX_PATH = VECTOR_DIR / "tourism.index"
METADATA_PATH = VECTOR_DIR / "metadata.pkl"

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

print("Loading FAISS database...")

index = faiss.read_index(
    str(INDEX_PATH)
)

with open(
    METADATA_PATH,
    "rb"
) as file:

    metadata = pickle.load(file)


print(
    f"Loaded {index.ntotal} vectors"
)


# ============================================================
# CREATE QUERY EMBEDDING
# ============================================================

def create_embedding(text):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    embedding = np.array(
        response["embeddings"][0],
        dtype="float32"
    )

    embedding = embedding.reshape(
        1, -1
    )

    faiss.normalize_L2(
        embedding
    )

    return embedding


# ============================================================
# RETRIEVE DOCUMENTS
# ============================================================

def retrieve_context(
    query,
    top_k=5
):

    query_embedding = create_embedding(
        query
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        results.append({
            "score": float(score),
            "source": metadata[index_id]["source"],
            "text": metadata[index_id]["text"]
        })

    return results


# ============================================================
# GENERATE ANSWER USING LLAMA 3
# ============================================================

def generate_answer(
    query,
    retrieved_documents
):

    context_parts = []

    for document in retrieved_documents:

        context_parts.append(
            f"""
Source: {document['source']}

{document['text']}
"""
        )

    context = "\n".join(
        context_parts
    )


    prompt = f"""
You are an AI Sustainable Tourism Planner.

Use the retrieved tourism information below
to answer the user's question.

IMPORTANT RULES:

1. Use the retrieved context as your primary source.
2. Do not invent tourism facts.
3. If information is unavailable, say so.
4. Give practical and clear recommendations.
5. Consider sustainable tourism whenever relevant.
6. Mention the relevant source names when appropriate.

Retrieved Tourism Information:
================================

{context}

================================

User Question:
{query}

Answer:
"""


    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt
    )

    return response["response"]


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "AI SUSTAINABLE TOURISM RAG SYSTEM"
    )

    print(
        "========================================"
    )


    query = input(
        "\nEnter your tourism question: "
    )


    # Retrieve
    print(
        "\nSearching tourism knowledge..."
    )

    retrieved_documents = retrieve_context(
        query,
        top_k=5
    )


    # Show retrieved sources
    print(
        "\nRetrieved sources:"
    )

    for document in retrieved_documents:

        print(
            f"- {document['source']} "
            f"(score: {document['score']:.4f})"
        )


    # Generate
    print(
        "\nGenerating answer with Llama 3..."
    )

    answer = generate_answer(
        query,
        retrieved_documents
    )


    print(
        "\n========================================"
    )

    print(
        "AI RESPONSE"
    )

    print(
        "========================================\n"
    )

    print(answer)