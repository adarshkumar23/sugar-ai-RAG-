"""
Sugar-AI RAG Pipeline
=====================
Retrieval-Augmented Generation pipeline for Sugar Labs documentation.
Uses ChromaDB for vector storage and all-MiniLM-L6-v2 for embeddings.
"""

import os
import glob
import hashlib
import chromadb
from typing import Optional


# ---------------------------------------------------------------------------
# Text chunking (lightweight, no langchain dependency needed)
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks by character count.

    Uses a simple sentence-aware splitter:
    1. Split on double newlines (paragraphs) first
    2. If a paragraph exceeds chunk_size, split on sentences
    3. Merge small paragraphs into chunks up to chunk_size
    """
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph stays within limit, accumulate
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = (current_chunk + "\n\n" + para).strip()
        else:
            # Save current chunk if non-empty
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself is too long, split by sentences
            if len(para) > chunk_size:
                sentences = _split_sentences(para)
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 <= chunk_size:
                        sub_chunk = (sub_chunk + " " + sent).strip()
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    # Add overlap: prepend last N chars of previous chunk
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            overlap_text = chunks[i - 1][-chunk_overlap:]
            overlapped.append(overlap_text + " " + chunks[i])
        return overlapped

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Naive sentence splitter on '.', '!', '?'."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# Document loader
# ---------------------------------------------------------------------------

def load_documents(docs_dir: str) -> list[dict]:
    """Load all .md and .txt files from a directory.

    Returns list of dicts: { "source": filename, "content": text }
    """
    documents = []
    patterns = ["*.md", "*.txt"]
    for pattern in patterns:
        for filepath in sorted(glob.glob(os.path.join(docs_dir, pattern))):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                documents.append({
                    "source": os.path.basename(filepath),
                    "content": content,
                })
    return documents


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

class SugarRAG:
    """RAG pipeline for Sugar Labs documentation."""

    def __init__(
        self,
        docs_dir: str = "data/docs",
        collection_name: str = "sugar_docs",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.docs_dir = docs_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # In-memory ChromaDB (use PersistentClient for production)
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._indexed = False

    # ---- Indexing ---------------------------------------------------------

    def index_documents(self) -> dict:
        """Load docs, chunk them, and add to ChromaDB. Returns stats."""
        documents = load_documents(self.docs_dir)
        if not documents:
            raise FileNotFoundError(f"No documents found in {self.docs_dir}")

        all_chunks: list[str] = []
        all_ids: list[str] = []
        all_metadata: list[dict] = []

        for doc in documents:
            chunks = chunk_text(
                doc["content"],
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{doc['source']}_{i}".encode()
                ).hexdigest()
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    "source": doc["source"],
                    "chunk_index": i,
                })

        # Upsert to ChromaDB (handles duplicates via ID)
        self.collection.upsert(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadata,
        )
        self._indexed = True

        return {
            "documents_loaded": len(documents),
            "total_chunks": len(all_chunks),
            "sources": [d["source"] for d in documents],
        }

    # ---- Retrieval --------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve top-k most relevant chunks for a query.

        Returns list of dicts:
        {
            "text": chunk text,
            "source": source filename,
            "score": cosine similarity (higher = better),
            "chunk_index": position in original doc,
        }
        """
        if not self._indexed:
            self.index_documents()

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for i in range(len(results["documents"][0])):
            # ChromaDB returns cosine *distance*, convert to similarity
            distance = results["distances"][0][i]
            similarity = 1 - distance  # cosine similarity

            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "score": round(similarity, 4),
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
            })

        # Sort by score descending
        retrieved.sort(key=lambda x: x["score"], reverse=True)
        return retrieved

    # ---- Generation (mock / pluggable) ------------------------------------

    def generate_answer(
        self,
        query: str,
        context_chunks: list[dict],
        llm_fn: Optional[callable] = None,
    ) -> str:
        """Generate an answer given query + retrieved context.

        If llm_fn is provided, calls llm_fn(prompt) -> str.
        Otherwise returns a formatted context-only response (no LLM needed).
        """
        context_text = "\n\n---\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in context_chunks
        )

        prompt = (
            "You are Sugar-AI, a helpful assistant for Sugar Labs. "
            "Answer the user's question using ONLY the context provided below. "
            "If the context doesn't contain enough information, say so honestly.\n\n"
            f"## Context\n\n{context_text}\n\n"
            f"## Question\n\n{query}\n\n"
            "## Answer\n\n"
        )

        if llm_fn is not None:
            return llm_fn(prompt)

        # Fallback: return the prompt + context (useful for testing pipeline)
        return (
            f"[No LLM configured — showing retrieved context for inspection]\n\n"
            f"Prompt that would be sent to LLM:\n"
            f"{'=' * 60}\n{prompt}\n{'=' * 60}"
        )

    # ---- End-to-end -------------------------------------------------------

    def query(self, question: str, top_k: int = 3, llm_fn=None) -> dict:
        """Full RAG pipeline: retrieve + generate.

        Returns {
            "question": str,
            "retrieved_chunks": list[dict],
            "answer": str,
        }
        """
        chunks = self.retrieve(question, top_k=top_k)
        answer = self.generate_answer(question, chunks, llm_fn=llm_fn)
        return {
            "question": question,
            "retrieved_chunks": chunks,
            "answer": answer,
        }
