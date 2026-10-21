# MongoDB Atlas + Gemini RAG Assistant

A Python retrieval-augmented generation (RAG) application combining local Sentence Transformers embeddings, MongoDB Atlas Vector Search, and Google Gemini. It retrieves relevant document passages and generates answers with source-title citations and similarity scores.

## Features
- `all-MiniLM-L6-v2` sentence embeddings (384 dimensions)
- MongoDB Atlas `$vectorSearch` retrieval (top 3)
- Google Gemini answer generation, grounded in retrieved documents
- Retries for Gemini 503/UNAVAILABLE responses
- Four sample policy documents and optional PDF ingestion

## Setup
1. Install Python 3.10+ and clone this repository.
2. Create a virtual environment: `python -m venv .venv`; on Windows activate with `.venv\Scripts\activate`.
3. Install packages: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and replace placeholders with **new** credentials. Never commit `.env`.
5. In MongoDB Atlas, make a Vector Search index named `vector_index` on `rag_demo.documents`, field `embedding`, `numDimensions: 384`, similarity `cosine`.
6. To seed only the demo collection, run `python app.py --seed`. **Warning:** this deletes the collection's existing documents; do not seed after ingesting PDFs you need to retain.
7. Start `python app.py`, then ask a question such as `When is customer support available?`.

## PDF ingestion
Put permitted, non-sensitive PDFs in a local `pdfs/` folder and run `python ingest_pdf.py`. The script extracts text, chunks it, embeds each chunk, and upserts PDF content by replacing previous chunks for each filename. Do not upload private PDFs or dataset exports to this public repo.

## Documentation
- [Workflow](docs/Workflow.md)
- [Setup Guide](docs/Setup_Guide.md)
- [Technical Report](docs/Technical_Report.md)

## Demonstrated result
**Question:** When is customer support available?

**Answer:** Monday–Friday, 9 AM to 5 PM Central Time. The `Customer Support` source was the highest retrieved match (similarity score approximately 0.900 in the recorded demonstration).

## Security
Credentials are read from environment variables. `.env`, virtual environments, local PDFs, and binary database files must not be committed. Rotate any previously exposed database passwords and API keys before deployment.

## Limitations
A high similarity score does not prove an answer is factually correct. Verify cited source passages, restrict access to sensitive documents, and evaluate the retrieval quality before production usage.
