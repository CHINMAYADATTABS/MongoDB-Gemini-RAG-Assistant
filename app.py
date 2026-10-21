import os
import sys
import time
import random
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DB", "rag_demo")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "documents")
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "vector_index")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHAT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SAMPLE_DOCS = [
    {
        "title": "Refund Policy",
        "text": "Customers may request a refund within 30 days of purchase. The product must be in its original condition. Refunds are usually processed within 5 to 7 business days after approval."
    },
    {
        "title": "Shipping Policy",
        "text": "Standard shipping usually takes 3 to 5 business days. Express shipping usually takes 1 to 2 business days. Customers receive a tracking number after an order ships."
    },
    {
        "title": "Customer Support",
        "text": "Customer support is available Monday through Friday, 9 AM to 5 PM Central Time. Customers can contact support by emailing help@example.com. Include the order number when asking about an order."
    },
    {
        "title": "Warranty",
        "text": "Products include a one-year limited warranty covering manufacturing defects. The warranty does not cover accidental damage, misuse, or normal wear and tear."
    },
]

def connect():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    collection = client[DB_NAME][COLLECTION_NAME]
    return client, collection

def seed_documents(collection, embedder):
    """Insert or replace the small demo knowledge base and store embeddings."""
    collection.delete_many({})
    texts = [d["text"] for d in SAMPLE_DOCS]
    vectors = embedder.encode(texts, normalize_embeddings=True).tolist()
    rows = []
    for doc, vector in zip(SAMPLE_DOCS, vectors):
        rows.append({**doc, "embedding": vector})
    if rows:
        collection.insert_many(rows)
    print(f"Loaded {len(rows)} sample documents into {DB_NAME}.{COLLECTION_NAME}.")

def retrieve(collection, embedder, question, top_k=3):
    query_vector = embedder.encode([question], normalize_embeddings=True)[0].tolist()
    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def answer_question(collection, embedder, llm, question):
    matches = retrieve(collection, embedder, question)
    if not matches:
        print("No matching documents found.")
        return

    context = "\n\n".join(
        f"Source: {item['title']}\nContent: {item['text']}"
        for item in matches
    )

    for attempt in range(5):
        try:
            response = llm.models.generate_content(
                model=CHAT_MODEL,
                contents=(
                    "Answer the user's question using only the supplied context. "
                    "If the context does not contain the answer, say you don't know "
                    "based on the available documents. Cite the source title(s) you used.\n\n"
                    f"Context:\n{context}\n\nQuestion: {question}"
                )
            )
            break

        except Exception as exc:
            if "503" not in str(exc) and "UNAVAILABLE" not in str(exc):
                raise

            if attempt == 4:
                raise

            wait_time = min(2 ** (attempt + 1), 30) + random.uniform(0, 1)
            print(f"Gemini is busy. Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)


    print("\nAnswer:")
    print(response.text)

    print("\nRetrieved sources:")
    for item in matches:
        print(f"- {item['title']} (similarity score: {item.get('score', 0):.3f})")

def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("Set GEMINI_API_KEY in your .env file before running.")
        sys.exit(1)
    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        client, collection = connect()
    except Exception as exc:
        print(f"Could not connect to MongoDB: {exc}")
        print("Check MONGODB_URI and confirm your MongoDB server/Atlas cluster is available.")
        sys.exit(1)

    try:
        if "--seed" in sys.argv:
            seed_documents(collection, embedder)
            print(
                "\nNext, create the MongoDB Atlas Vector Search index described in README.md, "
                "then run: python app.py"
            )
            return

        print(f"Connected to {DB_NAME}.{COLLECTION_NAME}")
        print("Ask a question about the sample policies. Type 'exit' to quit.")
        while True:
            question = input("\nQuestion: ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if question:
                try:
                    answer_question(collection, embedder, llm, question)
                except Exception as exc:
                    print(f"Could not answer question: {exc}")
                    print("Confirm that the Atlas Vector Search index exists and is ACTIVE.")
    finally:
        client.close()

if __name__ == "__main__":
    main()