# Technical Report — MongoDB Atlas + Gemini RAG Assistant

## Abstract
This project demonstrates Retrieval-Augmented Generation (RAG) using Python, local semantic embeddings, MongoDB Atlas Vector Search, and Google Gemini. Rather than relying on model recall alone, the application retrieves relevant document passages and supplies them to a generative model to draft a sourced answer.

## Problem and objective
Generic LLMs can invent details or lack access to organizational policies. The goal is to create a question-answering interface that locates passages in a small reference corpus, generates answers using retrieved evidence, and displays citations alongside similarity scores.

## Technology
- Python for the command-line application and ingestion
- `sentence-transformers/all-MiniLM-L6-v2` for normalized 384-dimensional embeddings
- MongoDB Atlas collection `rag_demo.documents` and a `vector_index` index
- MongoDB `$vectorSearch` for semantic retrieval
- Google Gemini API for grounded response generation
- PyPDF for document text extraction

## Implementation
1. Defined four illustrative policies: refund, shipping, customer support, and warranty.
2. Encoded document text with Sentence Transformers and stored the text, titles, and vectors in MongoDB.
3. Configured an Atlas Vector Search index for 384-dimensional vectors using cosine similarity.
4. Encoded each natural-language question and retrieved the three most similar passages.
5. Supplied the retrieved context to Gemini, instructed it to cite source titles, and printed its answer.
6. Implemented exponential-backoff retries for temporary 503/UNAVAILABLE errors.
7. Added optional PDF ingestion: text extraction, page-wise 800-character chunks, embedding, and per-file replacement.

## Architecture
See [Workflow.md](Workflow.md) for the end-to-end Mermaid diagram.

## Demonstration
Test question: **When is customer support available?**

Observed answer: **Monday through Friday, 9 AM to 5 PM Central Time**, supported by the **Customer Support** policy. The top retrieved similarity score displayed in the successful terminal test was approximately **0.900**.

Other retrieved documents appeared lower in the ranking. A similarity score should not be interpreted as proof of factual accuracy; the answer must be checked against the cited text.

## Troubleshooting during development
An initial attempt encountered a MongoDB Atlas TLS/SSL handshake error. Network Access was checked and the connection succeeded on a subsequent retry. Gemini also temporarily returned a service-busy condition and the application's retry mechanism allowed generation to succeed.

## Limitations
- The included sample policy set is illustrative; answers can only be as accurate as the indexed source material.
- PDF extraction does not include OCR for image-only scans.
- The prompt encourages citations, but the displayed source titles are not independently verified citations.
- Approximate semantic matching may retrieve irrelevant passages.
- There is no user authentication, private-document access enforcement, automated retrieval evaluation, or production-grade observability.
- Re-running `--seed` removes all existing documents in the target demo collection.

## Future work
- Document-level authorization and safer handling of sensitive source material
- Retrieval evaluation set and citation verification
- Chunk overlap and metadata-based filtering
- Browser interface and structured observability
- Automated tests with mocked MongoDB/Gemini services

## Conclusion
The working demonstration shows a complete RAG cycle, from embedding and indexing to question retrieval and Gemini answer generation. It is a foundation for larger domain-specific document assistants, not a production deployment.