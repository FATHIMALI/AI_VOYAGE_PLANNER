from pathlib import Path
import pickle

import faiss
import numpy as np
import ollama


# ============================================================
# PATHS
# ============================================================

KNOWLEDGE_DIR = Path("documents/tourism_knowledge")
VECTOR_DIR = Path("vector_db")

VECTOR_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = VECTOR_DIR / "tourism.index"
METADATA_PATH = VECTOR_DIR / "metadata.pkl"


# ============================================================
# OLLAMA EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL = "nomic-embed-text"


# ============================================================
# LOAD DOCUMENTS
# ============================================================

def load_documents():

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


# ============================================================
# TEXT CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================
# CREATE EMBEDDING
# ============================================================

def create_embedding(text):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return np.array(
        response["embeddings"][0],
        dtype="float32"
    )


# ============================================================
# BUILD FAISS DATABASE
# ============================================================

def build_vector_database():

    print("Loading tourism documents...")

    documents = load_documents()

    print(
        f"Loaded {len(documents)} documents"
    )

    if not documents:

        print(
            "ERROR: No tourism documents found."
        )

        return


    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    all_chunks = []

    metadata = []

    for document in documents:

        chunks = chunk_text(
            document["text"]
        )

        for chunk in chunks:

            all_chunks.append(chunk)

            metadata.append({
                "source": document["source"],
                "text": chunk
            })


    print(
        f"Created {len(all_chunks)} text chunks"
    )


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print(
        "\nGenerating embeddings using Ollama..."
    )

    embeddings = []

    for i, chunk in enumerate(all_chunks):

        print(
            f"Embedding {i + 1}/{len(all_chunks)}"
        )

        embedding = create_embedding(chunk)

        embeddings.append(embedding)


    embeddings = np.array(
        embeddings,
        dtype="float32"
    )


    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    faiss.normalize_L2(
        embeddings
    )


    # --------------------------------------------------------
    # Create FAISS index
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    print(
        f"\nEmbedding dimension: {dimension}"
    )

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )


    # --------------------------------------------------------
    # Save FAISS index
    # --------------------------------------------------------

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )


    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    with open(
        METADATA_PATH,
        "wb"
    ) as file:

        pickle.dump(
            metadata,
            file
        )


    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print(
        "\n===================================="
    )

    print(
        "VECTOR DATABASE CREATED SUCCESSFULLY"
    )

    print(
        "===================================="
    )

    print(
        f"Documents : {len(documents)}"
    )

    print(
        f"Chunks    : {len(all_chunks)}"
    )

    print(
        f"Dimension : {dimension}"
    )

    print(
        f"Vectors   : {index.ntotal}"
    )

    print(
        f"FAISS     : {INDEX_PATH}"
    )

    print(
        f"Metadata  : {METADATA_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_vector_database()