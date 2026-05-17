# 🌱 Week 3 — Embeddings & Vector Search
### AI Engineer Journey

A complete vector embeddings pipeline applied to **Tunisian agriculture**.
Built day by day, from scratch to a fully working semantic search engine —
the foundation of the agricultural RAG assistant project.

---

## 🧠 Core Concepts Covered

### What is an Embedding?
A piece of text → a list of ~1536 numbers (a vector).
Texts with similar meanings end up with vectors that point in similar directions.
This makes it possible to search by **meaning**, not just by keyword.

```
"How to treat olive flies?"     → [0.021, -0.045, 0.112, ...]
"Pesticide against olive pests" → [0.019, -0.041, 0.108, ...]  ← very close!
"How to bake a chocolate cake?" → [-0.312, 0.201, -0.089, ...] ← far away
```

### Why 1536 Dimensions?
OpenAI chose this size to balance **precision vs cost**.
Each dimension captures a nuance learned from billions of texts.
We don't control what each dimension means — the model decided on its own.

### Cosine Similarity
Measures the **angle** between two vectors, not the distance.

```
score = 1.0  → identical meaning
score > 0.75 → very relevant
score > 0.55 → somewhat relevant
score < 0.55 → not relevant → reject in production
```

WHY cosine and not euclidean distance?
Because we want to measure **direction (meaning)**, not magnitude.
"olive tree" and "a very large and old olive tree in Tunisia" share the same
meaning but have very different vector magnitudes — cosine handles this correctly.

### ChromaDB vs SQL

| Feature | SQL (PostgreSQL) | ChromaDB (vector DB) |
|---------|-----------------|----------------------|
| Search type | Keyword (`LIKE '%word%'`) | Semantic (by meaning) |
| Finds synonyms | ❌ No | ✅ Yes |
| Finds translations | ❌ No | ✅ Partially |
| Storage | Rows & columns | Vectors + metadata |
| Use case | Structured data | Unstructured text search |

### Chunking
Long documents can't be embedded as a whole (token limits).
We split them into overlapping chunks (~120 words each, with a 20-word overlap).

WHY overlap? An idea might span two chunks. The overlap ensures
that idea appears fully in at least one of them.

---


## 📅 Day-by-Day Breakdown

### Day 1 — Understanding Embeddings
- 📺 Watch: https://www.youtube.com/watch?v=ySus5ZS0b94
- 📖 Read: https://platform.openai.com/docs/guides/embeddings
- Make your first OpenAI embedding API call
- Compare sentence pairs with cosine similarity
- **End goal:** you can generate and compare embeddings via API

### Day 2 — ChromaDB: Your First Vector Database
- 📖 Doc: https://docs.trychroma.com/getting-started
- Install ChromaDB, create a persistent collection
- Store 10 Tunisian agriculture documents with their embeddings
- Understand why vector DBs exist alongside SQL
- **End goal:** a local vector DB with real agricultural data inside

### Day 3 — Semantic Search with Cosine Similarity
- 📖 Read: https://www.pinecone.io/learn/vector-similarity
- Query Chroma with natural language questions
- Test with both relevant and irrelevant questions — observe the scores
- Learn why a rejection threshold is essential in production
- **End goal:** you understand why semantic search beats keyword search

### Day 4 — Real Texts: Chunking + Semantic Search
- Take a long agriculture document (real content)
- Split it into overlapping chunks
- Store and search — verify the right passages come back for each question
- **End goal:** you see exactly how RAG retrieval works end-to-end

### Day 5 — Refactor + Push to GitHub
- Clean code: proper functions, clear names, zero duplication
- Comments explain **WHY**, not just what
- Full pipeline in one file with layered architecture
- **End goal:** readable, shareable code pushed to GitHub
