import os
import re
import sys
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────
# CONSTANTS — All thresholds and config live here, not buried in code.
# Changing behavior means editing ONE place, not hunting across functions.
# ─────────────────────────────────────────────────────────────────

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims — fast and cheap
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "agricultural_assistant"

CHUNK_SIZE = 120   # ~120 words ≈ ~160 tokens, well under model limits
CHUNK_OVERLAP = 20    # words shared between consecutive chunks
SCORE_THRESHOLD = 0.55  # below this: result is irrelevant, we reject it
N_RESULTS = 3     # how many chunks to return per query


# ─────────────────────────────────────────────────────────────────
# LAYER 1 — EMBEDDING
# Everything that talks to the OpenAI API lives here.
# If we switch to a different embedding provider, we only edit this layer.
# ─────────────────────────────────────────────────────────────────

def create_openai_client() -> OpenAI:
    """
    Instantiates the OpenAI client with API key validation.

    """
    if not OPENAI_API_KEY:
        raise EnvironmentError(
            "OPENAI_API_KEY is missing.\n"
            "Create a .env file with: OPENAI_API_KEY=sk-..."
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_embeddings(texts: list[str], client: OpenAI) -> list[list[float]]:
    """
    Converts a list of texts into vectors via the OpenAI API.

    WHY batch instead of one by one?
    A single HTTP request for N texts = less network latency and lower API cost.
    The OpenAI API accepts up to 2048 texts per batch call.

    WHY return list[list[float]] and not a numpy array?
    ChromaDB accepts plain Python lists natively — no extra dependency needed.
    """
    if not texts:
        return []

    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    # The API guarantees the same order as the inputs → safe to zip directly
    return [item.embedding for item in response.data]


# ─────────────────────────────────────────────────────────────────
# LAYER 2 — CHUNKING
# Splitting long documents into indexable pieces.
# ─────────────────────────────────────────────────────────────────

def split_into_chunks(text: str) -> list[str]:
    """
    Splits a long text into fixed-size chunks with overlap.

    WHY overlap?
    An idea may fall exactly on the boundary between two chunks.
    With overlap, each chunk repeats the last few words of the previous one,
    ensuring no idea gets silently cut in half.

    WHY ~120 words per chunk?
    Too short (< 50 words): loses context, embeddings become vague.
    Too long (> 500 words): dilutes meaning, one chunk covers too many topics.
    120 words ≈ one well-formed paragraph — the sweet spot for semantic search.
    """
    # Normalize excessive blank lines before splitting
    clean_text = re.sub(r'\n{3,}', '\n\n', text.strip())
    words = clean_text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ─────────────────────────────────────────────────────────────────
# LAYER 3 — STORAGE
# Everything that reads from or writes to ChromaDB lives here.
# ─────────────────────────────────────────────────────────────────

def init_collection() -> chromadb.Collection:
    """
    Opens or creates the persistent ChromaDB collection.

    WHY get_or_create?
    Idempotent: safe to run multiple times without creating duplicates.
    In production, the collection persists between sessions — we never
    start from zero on each launch.

    WHY hnsw:space = cosine?
    ChromaDB defaults to L2 (euclidean) distance.
    Forcing cosine space ensures results are ranked by semantic direction,
    not by vector magnitude — which is what we want for text similarity.
    """
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def index_document(text: str, source: str, collection: chromadb.Collection, client: OpenAI) -> int:
    """
    Full pipeline: long text → chunks → embeddings → stored in Chroma.

    Returns the number of chunks added (0 if already indexed).

    WHY check for duplicates?
    Running this script multiple times should be safe.
    We check if the first chunk ID already exists before indexing.
    This is a simple but effective guard for single-document indexing.

    In production with thousands of documents, you'd maintain a separate
    index of processed file hashes to avoid re-embedding.
    """
    first_chunk_id = f"{source}_chunk_000"
    existing = collection.get(ids=[first_chunk_id])

    if existing["ids"]:
        return 0  # Already indexed — skip silently

    chunks = split_into_chunks(text)
    embeddings = generate_embeddings(chunks, client)

    collection.add(
        ids=[f"{source}_chunk_{i:03d}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": source, "chunk_index": i} for i in range(len(chunks))]
    )
    return len(chunks)


# ─────────────────────────────────────────────────────────────────
# LAYER 4 — SEARCH
# The heart of the RAG system: find relevant chunks for a query.
# ─────────────────────────────────────────────────────────────────

def search(query: str, collection: chromadb.Collection, client: OpenAI) -> list[dict]:
    """
    Finds the most relevant chunks for a user query.

    FLOW:
    1. The query is converted into a vector (same space as stored documents)
    2. Chroma calculates cosine similarity against all stored vectors
    3. The top N are returned, then filtered by the relevance threshold

    WHY a rejection threshold?
    Chroma ALWAYS returns N results, even if nothing is relevant.
    Without a threshold, we'd pass off-topic chunks to the LLM → hallucinations.
    The threshold of 0.55 is empirical — adjust based on your data.

    DISTANCE → SCORE CONVERSION:
    With cosine space, Chroma returns distances in [0, 2].
    score = 1 - distance / 2 maps this to [0, 1] (more intuitive).
    """
    if collection.count() == 0:
        return []

    query_embedding = generate_embeddings([query], client)[0]

    raw_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(N_RESULTS, collection.count()),
        include=["documents", "distances", "metadatas"]
    )

    filtered = []
    for text, distance, meta in zip(
        raw_results["documents"][0],
        raw_results["distances"][0],
        raw_results["metadatas"][0]
    ):
        score = round(1 - distance / 2, 4)
        if score >= SCORE_THRESHOLD:
            filtered.append({
                "text": text,
                "score": score,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", -1)
            })

    return filtered


def build_context(results: list[dict]) -> str:
    """
    Formats retrieved chunks into a readable context block for a LLM.

    This function is the bridge between vector retrieval and answer generation.
    It's the 'R' in RAG (Retrieval-Augmented Generation).
    The LLM uses this context to answer factually instead of hallucinating.

    WHY include scores in the context?
    Useful for debugging. In production, you'd strip them before sending
    to the LLM to keep the prompt clean.
    """
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[Source {i} — {r['source']} — score {r['score']}]\n{r['text']}")
    return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────────
# LAYER 5 — INTERFACE
# Display and user interaction. Kept separate from business logic.
# ─────────────────────────────────────────────────────────────────

def display_results(query: str, results: list[dict]) -> None:
    """Prints search results in a clear, readable format."""
    print(f"\n  ❓ {query}")

    if not results:
        print(f"  ⚠️  No relevant results found (score < {SCORE_THRESHOLD})")
        print("     → In a real RAG system: respond with 'I don't have that information'")
        return

    for i, r in enumerate(results, 1):
        bar = "█" * int(r["score"] * 20) + "░" * (20 - int(r["score"] * 20))
        print(f"\n  #{i} [{bar}] {r['score']:.4f} | chunk #{r['chunk_index']:02d}")
        short_text = r["text"][:120] + "..." if len(r["text"]) > 120 else r["text"]
        print(f"     {short_text}")


def interactive_mode(collection: chromadb.Collection, client: OpenAI) -> None:
    """Lets the user type their own questions in a loop."""
    print("\n  💬 Interactive mode — type 'quit' to exit\n")
    while True:
        query = input("  Your question: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            print("\n  Goodbye!")
            break
        if not query:
            continue
        results = search(query, collection, client)
        display_results(query, results)


# ─────────────────────────────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────────────────────────────

OLIVE_TREE_TEXT = """
The olive tree (Olea europaea) is the most widespread fruit tree in Tunisia,
with over 100 million trees covering approximately 1.8 million hectares.
Tunisia is one of the world's leading exporters of olive oil.

The olive fly (Bactrocera oleae) is the main pest of the olive tree in the Mediterranean.
The female pierces the olive to lay her eggs inside. The larvae develop within the fruit,
causing losses of 10 to 80% depending on the year. The recommended treatment is spinosad,
which is approved for organic farming. Pheromone traps help monitor the population preventively.

Verticillium wilt is a fungal disease caused by Verticillium dahliae.
It causes sudden wilting of branches, then progressive death of the tree.
There is no curative treatment. Prevention relies on using healthy plants
and avoiding contaminated soil. Crop rotation is essential.

Cercosporiosis (Spilocea oleagina) appears as circular brown spots on leaves,
causing significant defoliation. It develops in autumn and winter in humid conditions.
Copper-based fungicides are effective as a preventive measure.

Pruning is best done in February–March, after the hard frosts but before bud break.
Dead, crossing, and inward-facing branches are removed to maintain an open crown.

Drip irrigation reduces water use by 40% compared to surface irrigation.
The critical periods for water are flowering (May–June) and fruit sizing (July–August).
Water stress during these stages can cut yield in half.

Harvest takes place between October and January depending on the variety and region.
For extra virgin olive oil, harvest at veraison — when olives start changing color (green to purple).
Early harvest gives oil richer in polyphenols (antioxidants) and more bitter in taste.
"""

DEMO_QUESTIONS = [
    "How do I treat olive flies on my trees?",
    "When is the best time to prune an olive tree?",
    "How can I reduce water usage when irrigating olives?",
    "What is verticillium wilt?",
    "When should I harvest olives for the best oil quality?",
    "How do I make a chocolate cake?",  # ← off-topic: should be rejected
]


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    demo_mode = "--demo" in sys.argv

    print("\n" + "═" * 62)
    print("  TUNISIAN AGRICULTURAL ASSISTANT — RAG Pipeline")
    print("  Week 3 Embeddings — Day 5: Clean Code ✅")
    print("═" * 62)

    # Initialize
    client = create_openai_client()
    collection = init_collection()

    # Index document (skipped automatically if already done)
    print("\n📌 Indexing olive tree document...")
    n_added = index_document(OLIVE_TREE_TEXT, "olive_tree_guide", collection, client)

    if n_added > 0:
        print(f"  ✅ {n_added} chunks indexed")
    else:
        print(f"  ✅ Already indexed ({collection.count()} chunks in the database)")

    # Demo or interactive
    if demo_mode:
        print("\n📌 Demo mode — 6 questions (including 1 off-topic)\n")
        for question in DEMO_QUESTIONS:
            results = search(question, collection, client)
            display_results(question, results)
    else:
        interactive_mode(collection, client)

    # Week summary
    print("\n" + "═" * 62)
    print("🎯 WEEK 3 SUMMARY — What You've Learned\n")
    print("  ✅ Day 1: Embedding = text → vector, cosine similarity")
    print("  ✅ Day 2: ChromaDB = persistent local vector database")
    print("  ✅ Day 3: Semantic search + importance of rejection threshold")
    print("  ✅ Day 4: Chunking with overlap on real long documents")
    print("  ✅ Day 5: Clean layered pipeline, pushed to GitHub")
    print("\n  🚀 Week 4: Connect a LLM → full RAG assistant end-to-end")
    print("═" * 62 + "\n")


if __name__ == "__main__":
    main()
