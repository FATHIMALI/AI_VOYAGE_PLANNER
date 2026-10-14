from pathlib import Path
import pickle

import faiss
import numpy as np
import ollama


VECTOR_DIR = Path("vector_db")

INDEX_PATH = VECTOR_DIR / "tourism.index"
METADATA_PATH = VECTOR_DIR / "metadata.pkl"

EMBEDDING_MODEL = "nomic-embed-text"


print("Loading RAG system...")

# Load FAISS index
index = faiss.read_index(str(INDEX_PATH))

# Load metadata
with open(METADATA_PATH, "rb") as file:
    metadata = pickle.load(file)

print(f"Loaded {index.ntotal} vectors")


def create_query_embedding(query):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=query
    )

    embedding = np.array(
        response["embeddings"][0],
        dtype="float32"
    )

    embedding = embedding.reshape(1, -1)

    faiss.normalize_L2(embedding)

    return embedding


def search(query, top_k=5):

    query_embedding = create_query_embedding(query)

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


if __name__ == "__main__":

    query = input(
        "\nEnter your tourism question: "
    )

    results = search(query)

    print(
        "\n========== RAG RESULTS ==========\n"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"Result {i}")
        print(f"Source: {result['source']}")
        print(
            f"Similarity: {result['score']:.4f}"
        )
        print(
            f"Text:\n{result['text']}"
        )
        print(
            "\n" + "-" * 60
        )