# Sugar-AI: RAG Pipeline for Sugar Labs

A Retrieval-Augmented Generation (RAG) system that answers questions about Sugar Labs using documentation as a knowledge base.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the test script (no API key needed!)
python3 test_rag.py

# Run with an LLM for full answer generation
OPENAI_API_KEY=sk-... python3 test_rag.py --llm openai
ANTHROPIC_API_KEY=sk-... python3 test_rag.py --llm anthropic
python3 test_rag.py --llm ollama  # requires local Ollama server
```

## Project Structure

```
sugar-ai/
├── rag_pipeline.py          # Core RAG pipeline (chunking, embedding, retrieval)
├── test_rag.py              # Test script with 10 ground-truth queries
├── requirements.txt         # Python dependencies
├── README.md
└── data/
    └── docs/                # Sugar Labs documentation (knowledge base)
        ├── sugar_overview.md
        ├── activities_guide.md
        ├── contributing.md
        ├── music_blocks.md
        └── troubleshooting.md
```

## How It Works

1. **Load**: Reads `.md` files from `data/docs/`
2. **Chunk**: Splits documents into ~500 char overlapping chunks
3. **Embed**: Converts chunks to vectors using `all-MiniLM-L6-v2` (via ChromaDB)
4. **Store**: Indexes vectors in ChromaDB (in-memory)
5. **Retrieve**: For each query, finds top-k most similar chunks via cosine similarity
6. **Generate**: (Optional) Passes retrieved chunks + query to an LLM for answer generation

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--llm` | none | LLM backend: `openai`, `anthropic`, `ollama` |
| `--top-k` | 3 | Number of chunks to retrieve |
| `--chunk-size` | 500 | Chunk size in characters |
| `--chunk-overlap` | 100 | Overlap between chunks |
| `--docs-dir` | data/docs | Path to documentation |
| `--quiet` | false | Hide chunk text previews |
| `--json` | false | Output results as JSON |

## Test Queries

The test suite includes 10 curated queries covering:
- Installation (Raspberry Pi, Linux)
- Activities (Turtle Blocks, Pippy, Music Blocks)
- Development (creating Activities, contributing)
- Core concepts (Journal, collaboration)
- Troubleshooting (startup issues, platform compatibility)

Each query has expected source documents for measuring retrieval accuracy.

## License

GPLv3+ (consistent with Sugar Labs)
