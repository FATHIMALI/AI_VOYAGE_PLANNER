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
# LOAD RAG DATABASE
# ============================================================

print("Loading tourism knowledge base...")

index = faiss.read_index(
    str(INDEX_PATH)
)

with open(
    METADATA_PATH,
    "rb"
) as file:
    metadata = pickle.load(file)


# ============================================================
# EMBEDDING
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

    embedding = embedding.reshape(1, -1)

    faiss.normalize_L2(embedding)

    return embedding


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_information(query, top_k=8):

    query_embedding = create_embedding(query)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    seen_sources = set()

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        source = metadata[index_id]["source"]

        # Remove duplicate sources
        if source in seen_sources:
            continue

        # Ignore weak matches
        if float(score) < 0.55:
            continue

        seen_sources.add(source)

        results.append({
            "source": source,
            "text": metadata[index_id]["text"],
            "score": float(score)
        })

    return results[:5]


# ============================================================
# CREATE ITINERARY
# ============================================================

def generate_itinerary(
    destination,
    days,
    budget,
    interests,
    travel_preference
):

    query = f"""
    Create tourism information for a trip to {destination}.
    Number of days: {days}
    Budget: {budget}
    Interests: {interests}
    Travel preference: {travel_preference}

    Find relevant destinations, attractions,
    heritage information and sustainable tourism
    recommendations.
    """

    # --------------------------------------------------------
    # Retrieve relevant information
    # --------------------------------------------------------

    documents = retrieve_information(
        query,
        top_k=6
    )

    context = ""

    for document in documents:

        context += f"""
SOURCE: {document['source']}

{document['text']}

-----------------------------------
"""


    # --------------------------------------------------------
    # Llama 3 prompt
    # --------------------------------------------------------

    prompt = f"""
You are an AI Sustainable Tourism Planner.

Create a personalized {days}-day travel itinerary.

USER REQUIREMENTS
=================
Destination: {destination}
Number of days: {days}
Budget: {budget}
Interests: {interests}
Travel preference: {travel_preference}


RETRIEVED TOURISM KNOWLEDGE
===========================

{context}


IMPORTANT RULES
===============

1. Use the retrieved knowledge as the primary source.
2. Do not invent specific facts that are not supported.
3. If information is unavailable, clearly mention it.
4. Create a realistic day-by-day itinerary.
5. Prioritize the user's interests.
6. Consider the user's budget.
7. Include sustainable transportation suggestions.
8. Include sustainable tourism practices.
9. Encourage local businesses where appropriate.
10. Avoid claiming real-time availability.
11. Do not provide fake hotel or ticket prices.
12. Clearly separate known information from estimates.


OUTPUT FORMAT
=============

# {destination} Sustainable Travel Plan

## Trip Summary

Destination:
Duration:
Budget:
Interests:
Travel Preference:


## Day 1

Morning:
Afternoon:
Evening:

Transportation:
Sustainability Tip:


## Day 2

Morning:
Afternoon:
Evening:

Transportation:
Sustainability Tip:


Continue for all requested days.


## Budget Guidance

Explain how the user can manage the available budget.


## Sustainable Travel Recommendations

Provide practical eco-friendly recommendations.


## Important Notes

Mention information that should be verified before travelling.
"""


    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt
    )

    return response["response"], documents


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("AI SUSTAINABLE TOURISM PLANNER")
    print("========================================")

    destination = input(
        "\nEnter destination: "
    )

    days = int(
        input("Number of days: ")
    )

    budget = input(
        "Budget: "
    )

    interests = input(
        "Interests: "
    )

    travel_preference = input(
        "Travel preference: "
    )


    print(
        "\nSearching tourism knowledge..."
    )

    itinerary, sources = generate_itinerary(
        destination,
        days,
        budget,
        interests,
        travel_preference
    )


    print(
        "\n========================================"
    )

    print("GENERATED ITINERARY")

    print(
        "========================================\n"
    )

    print(itinerary)


    print(
        "\n========================================"
    )

    print("RAG SOURCES USED")

    print(
        "========================================"
    )

    for source in sources:

        print(
            f"- {source['source']} "
            f"(score: {source['score']:.4f})"
        )