# Windows Setup Guide

## Prerequisites
- Python 3.10 or newer
- MongoDB Atlas cluster with Vector Search support
- MongoDB database user with appropriate access
- Gemini API key

## Install
```cmd
cd /d "C:\path\to\MongoDB-Gemini-RAG-Assistant"
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit your local `.env` to supply your **own current credentials**. The template is safe to commit, but the populated `.env` is not. Never paste secrets in issues or screenshots.

## Create Atlas Vector Search index
Navigate to your Atlas cluster, database `rag_demo`, collection `documents`, and create a Vector Search index named `vector_index` with this definition:

```json
{
  "fields": [
    {"type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine"}
  ]
}
```

Wait for the index to become active. Ensure Atlas Network Access permits your current client IP.

## Load documents
For **new demo collections only**, run:
```cmd
python app.py --seed
```
**Caution:** Seeding deletes all documents in the configured collection, including previously ingested PDF records.

For additional permitted PDFs, place them in a local `pdfs` folder and run:
```cmd
python ingest_pdf.py
```
The PDF ingestion tool may not extract scanned pages without text layers.

## Ask questions
```cmd
python app.py
```
At `Question:` type `When is customer support available?`. Type `exit` to stop.

## Troubleshooting
- **TLS/SSL handshake error:** Check MongoDB Atlas cluster status, IP allowlist, DNS/network connectivity, and certificate/network interception; retry after connectivity stabilizes.
- **Search index missing:** Verify the correct database, collection, `vector_index` name, and 384 dimensions.
- **Gemini 503/UNAVAILABLE:** The application retries up to five times with exponential backoff.
- **Model unavailable:** Change `GEMINI_MODEL` in your `.env` to a Gemini model available to your API key.
- **Incorrect response:** Check retrieved source text and whether the required document was ingested.

## Safety
Do not commit credentials, user data, university admissions PDFs containing personal details, database exports, or screenshots with secrets.