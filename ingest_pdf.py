
import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

load_dotenv()

PDF_FOLDER = Path(__file__).parent / "pdfs"
DB_NAME = os.getenv("MONGODB_DB", "rag_demo")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "documents")

def main():
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the pdfs folder.")
        return

    print("Loading embedding model...")
    embedder = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    client = MongoClient(
        os.environ["MONGODB_URI"],
        serverSelectionTimeoutMS=5000
    )
    collection = client[DB_NAME][COLLECTION_NAME]

    try:
        client.admin.command("ping")

        total = 0

        for pdf_path in pdf_files:
            print(f"Reading {pdf_path.name}...")
            reader = PdfReader(str(pdf_path))

            chunks = []

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                text = " ".join(text.split())

                for start in range(0, len(text), 800):
                    chunk = text[start:start + 800]

                    if chunk.strip():
                        chunks.append({
                            "title": pdf_path.stem,
                            "text": chunk,
                            "source": pdf_path.name,
                            "page": page_number
                        })

            if not chunks:
                print(f"No readable text found in {pdf_path.name}")
                continue

            embeddings = embedder.encode(
                [chunk["text"] for chunk in chunks],
                normalize_embeddings=True
            ).tolist()

            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding

            # Replace previous chunks from this PDF only.
            # Keep all other MongoDB documents.
            collection.delete_many({"source": pdf_path.name})
            collection.insert_many(chunks)

            total += len(chunks)
            print(f"Stored {len(chunks)} chunks from {pdf_path.name}")

        print(f"\nDone! Stored {total} PDF chunks in MongoDB.")

    finally:
        client.close()

if __name__ == "__main__":
    main()