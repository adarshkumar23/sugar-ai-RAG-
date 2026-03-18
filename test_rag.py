#!/usr/bin/env python3
"""
test_rag.py — Sugar-AI RAG Pipeline Test Script
================================================

Demonstrates the full RAG pipeline:
  1. Load Sugar Labs documentation
  2. Chunk & embed into ChromaDB
  3. Run test queries and show retrieval results
  4. (Optional) Generate answers via LLM

Usage:
    python3 test_rag.py                    # Run with mock LLM (no API key needed)
    OPENAI_API_KEY=sk-... python3 test_rag.py --llm openai
    python3 test_rag.py --llm ollama       # Requires local Ollama server
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_pipeline import SugarRAG


# ──────────────────────────────────────────────────────────────────────────────
#  ANSI colors for terminal output
# ──────────────────────────────────────────────────────────────────────────────

class C:
    HEADER  = "\033[95m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


def print_banner():
    print(f"""
{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════════╗
║           🍬  Sugar-AI RAG Pipeline Test Suite  🍬           ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
""")


def print_section(title: str):
    print(f"\n{C.BOLD}{C.BLUE}{'─' * 64}")
    print(f"  {title}")
    print(f"{'─' * 64}{C.RESET}\n")


def print_result(label: str, value, color=C.GREEN):
    print(f"  {C.BOLD}{label}:{C.RESET} {color}{value}{C.RESET}")


# ──────────────────────────────────────────────────────────────────────────────
#  LLM backends (pluggable)
# ──────────────────────────────────────────────────────────────────────────────

def get_llm_fn(backend: Optional[str] = None):
    """Return an LLM function based on the chosen backend."""

    if backend == "openai":
        try:
            import openai
        except ImportError:
            print(f"{C.RED}✗ openai package not installed. Run: pip install openai{C.RESET}")
            sys.exit(1)

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print(f"{C.RED}✗ OPENAI_API_KEY not set{C.RESET}")
            sys.exit(1)

        client = openai.OpenAI(api_key=api_key)

        def openai_fn(prompt: str) -> str:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        return openai_fn

    elif backend == "ollama":
        import urllib.request
        import json as _json

        def ollama_fn(prompt: str) -> str:
            url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
            model = os.environ.get("OLLAMA_MODEL", "llama3.2")
            data = _json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                f"{url}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = _json.loads(resp.read().decode())
            return result.get("response", "").strip()

        return ollama_fn

    elif backend == "anthropic":
        try:
            import anthropic
        except ImportError:
            print(f"{C.RED}✗ anthropic package not installed. Run: pip install anthropic{C.RESET}")
            sys.exit(1)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print(f"{C.RED}✗ ANTHROPIC_API_KEY not set{C.RESET}")
            sys.exit(1)

        client = anthropic.Anthropic(api_key=api_key)

        def anthropic_fn(prompt: str) -> str:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

        return anthropic_fn

    # Default: no LLM (pipeline-only test)
    return None


# ──────────────────────────────────────────────────────────────────────────────
#  Test queries with expected source documents (ground truth)
# ──────────────────────────────────────────────────────────────────────────────

TEST_QUERIES = [
    {
        "query": "How do I install Sugar on a Raspberry Pi?",
        "expected_sources": ["sugar_overview.md"],
        "description": "Installation question — should retrieve platform docs",
    },
    {
        "query": "What programming language does Turtle Blocks use?",
        "expected_sources": ["activities_guide.md"],
        "description": "Activity-specific question — should retrieve activities guide",
    },
    {
        "query": "How do I create a new Sugar Activity?",
        "expected_sources": ["activities_guide.md"],
        "description": "Developer question — should retrieve activity creation docs",
    },
    {
        "query": "What is the Journal in Sugar?",
        "expected_sources": ["sugar_overview.md"],
        "description": "Core concept question — should retrieve overview docs",
    },
    {
        "query": "How can I contribute to Sugar Labs?",
        "expected_sources": ["contributing.md"],
        "description": "Community question — should retrieve contributing guide",
    },
    {
        "query": "What is Music Blocks and how does it work?",
        "expected_sources": ["music_blocks.md"],
        "description": "Music Blocks question — should retrieve Music Blocks docs",
    },
    {
        "query": "Sugar won't start after installation, what should I do?",
        "expected_sources": ["troubleshooting.md"],
        "description": "Troubleshooting — should retrieve FAQ/troubleshooting docs",
    },
    {
        "query": "How does collaboration work in Sugar Activities?",
        "expected_sources": ["activities_guide.md"],
        "description": "Collaboration feature question — should retrieve activities guide",
    },
    {
        "query": "Can I run Sugar on Windows?",
        "expected_sources": ["troubleshooting.md"],
        "description": "Platform compatibility — should retrieve troubleshooting FAQ",
    },
    {
        "query": "What is Pippy and how do I use it to learn Python?",
        "expected_sources": ["activities_guide.md"],
        "description": "Pippy Activity — should retrieve activities guide",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
#  Test runner
# ──────────────────────────────────────────────────────────────────────────────

def run_tests(rag: SugarRAG, llm_fn=None, top_k: int = 3, verbose: bool = True):
    """Run all test queries and compute retrieval accuracy."""

    results = []
    total_hits = 0
    total_queries = len(TEST_QUERIES)

    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        expected = set(test["expected_sources"])

        print(f"\n{C.BOLD}{C.YELLOW}┌─ Query {i}/{total_queries}{C.RESET}")
        print(f"{C.BOLD}│  Q: {query}{C.RESET}")
        print(f"{C.DIM}│  ({test['description']}){C.RESET}")
        print(f"│")

        # Time the retrieval
        t0 = time.time()
        retrieved = rag.retrieve(query, top_k=top_k)
        retrieval_time = time.time() - t0

        # Check if expected source is in top-k results
        retrieved_sources = set(r["source"] for r in retrieved)
        hit = bool(expected & retrieved_sources)
        total_hits += int(hit)

        # Print retrieved chunks
        for j, chunk in enumerate(retrieved, 1):
            score_color = C.GREEN if chunk["score"] > 0.4 else C.YELLOW if chunk["score"] > 0.2 else C.RED
            source_marker = " ✓ EXPECTED" if chunk["source"] in expected else ""
            print(f"│  {C.CYAN}[{j}]{C.RESET} {score_color}score={chunk['score']:.4f}{C.RESET}  "
                  f"source={C.BOLD}{chunk['source']}{C.RESET}{C.GREEN}{source_marker}{C.RESET}")
            if verbose:
                preview = chunk["text"][:150].replace("\n", " ")
                print(f"│      {C.DIM}\"{preview}...\"{C.RESET}")

        # Retrieval verdict
        status = f"{C.GREEN}✓ HIT{C.RESET}" if hit else f"{C.RED}✗ MISS{C.RESET}"
        print(f"│")
        print(f"│  Retrieval: {status}  │  Time: {retrieval_time*1000:.1f}ms")

        # Generate answer if LLM is available
        if llm_fn is not None:
            print(f"│")
            print(f"│  {C.CYAN}Generating answer via LLM...{C.RESET}")
            t0 = time.time()
            answer = rag.generate_answer(query, retrieved, llm_fn=llm_fn)
            gen_time = time.time() - t0
            print(f"│  {C.GREEN}Answer ({gen_time:.1f}s):{C.RESET}")
            for line in answer.split("\n"):
                print(f"│  {C.DIM}  {line}{C.RESET}")

        print(f"{C.BOLD}{C.YELLOW}└{'─' * 63}{C.RESET}")

        results.append({
            "query": query,
            "hit": hit,
            "retrieved_sources": list(retrieved_sources),
            "expected_sources": list(expected),
            "top_score": retrieved[0]["score"] if retrieved else 0,
            "retrieval_time_ms": round(retrieval_time * 1000, 1),
        })

    return results, total_hits, total_queries


# ──────────────────────────────────────────────────────────────────────────────
#  Summary report
# ──────────────────────────────────────────────────────────────────────────────

def print_summary(results: list[dict], total_hits: int, total_queries: int):
    """Print a summary of test results."""
    accuracy = (total_hits / total_queries * 100) if total_queries > 0 else 0
    avg_score = sum(r["top_score"] for r in results) / len(results)
    avg_time = sum(r["retrieval_time_ms"] for r in results) / len(results)

    print_section("📊  TEST RESULTS SUMMARY")

    # Accuracy bar
    bar_len = 30
    filled = int(bar_len * accuracy / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    acc_color = C.GREEN if accuracy >= 80 else C.YELLOW if accuracy >= 60 else C.RED

    print(f"  Retrieval Accuracy:  {acc_color}{bar} {accuracy:.0f}%{C.RESET}  ({total_hits}/{total_queries})")
    print(f"  Avg Top-1 Score:     {avg_score:.4f}")
    print(f"  Avg Retrieval Time:  {avg_time:.1f}ms")
    print()

    # Per-query results table
    print(f"  {'Query':<55} {'Hit':>5}  {'Score':>6}  {'Time':>7}")
    print(f"  {'─' * 55} {'─' * 5}  {'─' * 6}  {'─' * 7}")
    for r in results:
        q = r["query"][:52] + "..." if len(r["query"]) > 55 else r["query"]
        hit_str = f"{C.GREEN}  ✓  {C.RESET}" if r["hit"] else f"{C.RED}  ✗  {C.RESET}"
        print(f"  {q:<55} {hit_str}  {r['top_score']:>6.4f}  {r['retrieval_time_ms']:>5.1f}ms")

    print()

    if accuracy == 100:
        print(f"  {C.GREEN}{C.BOLD}🎉 All queries retrieved the expected source documents!{C.RESET}")
    elif accuracy >= 80:
        print(f"  {C.YELLOW}{C.BOLD}⚡ Good retrieval accuracy. Some queries may need doc improvements.{C.RESET}")
    else:
        print(f"  {C.RED}{C.BOLD}⚠  Low accuracy — consider tuning chunk_size, overlap, or adding more docs.{C.RESET}")

    print()


# ──────────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sugar-AI RAG Pipeline Test")
    parser.add_argument("--llm", choices=["openai", "ollama", "anthropic"],
                        default=None, help="LLM backend for answer generation")
    parser.add_argument("--top-k", type=int, default=3,
                        help="Number of chunks to retrieve (default: 3)")
    parser.add_argument("--chunk-size", type=int, default=500,
                        help="Chunk size in characters (default: 500)")
    parser.add_argument("--chunk-overlap", type=int, default=100,
                        help="Chunk overlap in characters (default: 100)")
    parser.add_argument("--docs-dir", default="data/docs",
                        help="Path to documentation directory")
    parser.add_argument("--quiet", action="store_true",
                        help="Hide chunk previews")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    print_banner()

    # ── Step 1: Initialize RAG pipeline ──────────────────────────────────
    print_section("Step 1: Initialize RAG Pipeline")

    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.docs_dir)
    print_result("Docs directory", docs_dir)
    print_result("Chunk size", f"{args.chunk_size} chars")
    print_result("Chunk overlap", f"{args.chunk_overlap} chars")
    print_result("Top-K retrieval", args.top_k)
    print_result("LLM backend", args.llm or "none (retrieval-only test)")

    rag = SugarRAG(
        docs_dir=docs_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    # ── Step 2: Index documents ──────────────────────────────────────────
    print_section("Step 2: Index Documents into Vector Store")

    t0 = time.time()
    stats = rag.index_documents()
    index_time = time.time() - t0

    print_result("Documents loaded", stats["documents_loaded"])
    print_result("Total chunks", stats["total_chunks"])
    print_result("Sources", ", ".join(stats["sources"]))
    print_result("Indexing time", f"{index_time*1000:.0f}ms")
    print_result("Embedding model", "all-MiniLM-L6-v2 (ChromaDB built-in)")
    print_result("Vector store", "ChromaDB (in-memory)")

    # ── Step 3: Run test queries ─────────────────────────────────────────
    print_section("Step 3: Run Test Queries")

    llm_fn = get_llm_fn(args.llm)
    results, hits, total = run_tests(
        rag,
        llm_fn=llm_fn,
        top_k=args.top_k,
        verbose=not args.quiet,
    )

    # ── Step 4: Summary ──────────────────────────────────────────────────
    print_summary(results, hits, total)

    # ── Optional JSON output ─────────────────────────────────────────────
    if args.json:
        output = {
            "config": {
                "chunk_size": args.chunk_size,
                "chunk_overlap": args.chunk_overlap,
                "top_k": args.top_k,
                "llm": args.llm,
                "embedding_model": "all-MiniLM-L6-v2",
            },
            "indexing": stats,
            "results": results,
            "summary": {
                "accuracy": hits / total * 100,
                "total_hits": hits,
                "total_queries": total,
            },
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
