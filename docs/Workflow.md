# RAG Workflow

```mermaid
flowchart TD
    A[Sample policy documents / permitted PDFs] --> B[Extract text and chunk documents]
    B --> C[SentenceTransformer all-MiniLM-L6-v2]
    C --> D[384-dimensional embeddings]
    D --> E[MongoDB Atlas documents collection]
    Q[User question] --> F[Encode question using same embedding model]
    F --> G[MongoDB Atlas Vector Search]
    E --> G
    G --> H[Top three semantically similar passages]
    H --> I[Prompt: use retrieved context and cite source titles]
    Q --> I
    I --> J[Google Gemini]
    J --> K[Answer with source names]
    G --> L[Similarity scores printed in terminal]
```

## Ingestion

- `python app.py --seed` embeds and stores four synthetic policy records. **It deletes all existing records in the configured collection**, so only run it when resetting a demo dataset is safe.
- `python ingest_pdf.py` scans local PDFs, extracts text per page, splits it into character chunks, computes embeddings, and replaces prior chunks from the same filename. This preserves other documents.

## Retrieval and generation

1. Encode the question using the same embedding model used for ingestion.
2. Query MongoDB's `$vectorSearch` index on the `embedding` field with 100 candidates and three results.
3. Assemble returned text and source titles into the context.
4. Request a context-grounded answer from Gemini and instruct the model to indicate when evidence is missing.
5. Print the answer and the scores for retrieved passages.

**Note:** Vector similarity is a retrieval measure, not a measure of answer correctness.