import ollama


MODEL_NAME = "llama3"


def generate_answer(query, context):

    prompt = f"""
You are an AI Sustainable Tourism Planner.

Answer the user's tourism question using ONLY the
provided tourism context.

If the answer is not available in the context,
clearly say that the information is not available
in the current knowledge base.

Do not invent facts.

Tourism Context:
----------------
{context}
----------------

User Question:
{query}

Provide a clear and useful answer.
"""


    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt
    )

    return response["response"]


if __name__ == "__main__":

    context = """
Destination: Taj Mahal
Location: Agra, Uttar Pradesh
Category: Historical Monument / Cultural Tourism

The Taj Mahal is a major heritage attraction
located in Agra, Uttar Pradesh.
"""

    question = "Tell me about the Taj Mahal."

    answer = generate_answer(
        question,
        context
    )

    print("\n========== LLAMA 3 RESPONSE ==========\n")
    print(answer)