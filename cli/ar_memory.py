#!/usr/bin/env python3
"""
AdvancedRules Memory CLI Module
Minimal CLI for memory operations with feature flag protection

Usage:
    python -m cli.ar_memory [command] [options]
    arx memory [command] [options]
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory.bridge import MemoryBridge, get_memory_bridge


def rag_enabled() -> bool:
    """Check if RAG memory is enabled via feature flag or env override"""
    # Check feature flag in config
    try:
        import yaml
        config_path = Path("config/advanced_rules.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f)
            flag = bool(cfg.get("features", {}).get("rag_memory", False))
        else:
            flag = False
    except Exception:
        flag = False

    # Check environment override
    env_override = os.getenv("AR_ENABLE_RAG") == "1"

    return flag or env_override


def require_rag():
    """Require RAG to be enabled, exit if not"""
    if not rag_enabled():
        print("❌ Memory/RAG disabled. Set AR_ENABLE_RAG=1 or enable features.rag_memory in config.")
        sys.exit(1)


def cmd_index(args):
    """Index content into memory"""
    require_rag()

    print(f"🔍 Indexing: {args.src}")
    print(f"   Namespaces: {args.namespaces}")
    print(f"   Persona: {args.persona}")
    print(f"   Reindex: {args.reindex}")
    print("-" * 50)

    # Parse namespaces
    namespaces = [ns.strip() for ns in args.namespaces.split(",")] if args.namespaces else []

    # Get memory bridge
    bridge = get_memory_bridge()

    # Initialize if needed
    if not bridge._initialized:
        config_path = Path("config/advanced_rules.yaml")
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f)
                    rag_config = full_config.get("rag", {})
                    bridge.initialize(rag_config)
            except Exception as e:
                print(f"❌ Failed to initialize memory bridge: {e}")
                sys.exit(1)

    # Index the path
    success = index_path_wrapper(
        bridge=bridge,
        src_path=args.src,
        namespaces=namespaces,
        persona=args.persona or "GENERAL_AI",
        reindex=args.reindex
    )

    print(f"✅ Indexed successfully" if success else "⚠️ Index completed with warnings")


def cmd_query(args):
    """Query memory for context"""
    require_rag()

    print(f"🔍 Querying for {args.persona}: {args.query}")
    print(f"   Max results: {args.k}")
    print("-" * 40)

    # Get memory bridge
    bridge = get_memory_bridge()

    # Initialize if needed
    if not bridge._initialized:
        config_path = Path("config/advanced_rules.yaml")
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f)
                    rag_config = full_config.get("rag", {})
                    bridge.initialize(rag_config)
            except Exception as e:
                print(f"❌ Failed to initialize memory bridge: {e}")
                sys.exit(1)

    # Perform query
    try:
        hits = bridge.persona_context(
            persona=args.persona,
            query=args.query,
            k=args.k
        )

        if not hits:
            print("ℹ️ No results found")
            return

        for i, hit in enumerate(hits, 1):
            score = hit.get('score', 0.0)
            source = hit.get('source', 'unknown')
            content = hit.get('content', '')[:120]  # Preview first 120 chars
            print(f"{i}. score={score:.3f} src={source} :: {content}")

        print(f"\n📊 Found {len(hits)} relevant documents")

    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)


def cmd_stats(_args):
    """Show memory statistics"""
    enabled = rag_enabled()
    status = "active" if enabled else "disabled"

    print(f"Status: {status}")

    if enabled:
        require_rag()  # Enforce RAG flag for stats access
        try:
            bridge = get_memory_bridge()

            # Initialize if needed
            if not bridge._initialized:
                config_path = Path("config/advanced_rules.yaml")
                if config_path.exists():
                    try:
                        import yaml
                        with open(config_path, 'r') as f:
                            full_config = yaml.safe_load(f)
                            rag_config = full_config.get("rag", {})
                            bridge.initialize(rag_config)
                    except Exception as e:
                        print(f"❌ Failed to initialize memory bridge: {e}")
                        return

            # Get stats
            stats = bridge.get_memory_stats()

            if "vector_store" in stats:
                vs_stats = stats["vector_store"]
                print(f"Backend: {stats.get('backend', 'unknown')}")
                print(f"Embedding Model: {stats.get('embedding_model', 'unknown')}")
                print(f"Total Documents: {vs_stats.get('total_documents', 0)}")
                print(f"Persist Directory: {vs_stats.get('persist_dir', 'unknown')}")

            if "namespaces" in stats:
                print(f"Namespaces: {', '.join(stats['namespaces'])}")

        except Exception as e:
            print(f"Error getting stats: {e}")
    else:
        print("Memory system is disabled. Enable with AR_ENABLE_RAG=1 or features.rag_memory=true")


def cmd_purge(args):
    """Purge memory content"""
    require_rag()

    print(f"🗑️ Purging memory for persona: {args.persona}")

    # Get memory bridge
    bridge = get_memory_bridge()

    # Initialize if needed
    if not bridge._initialized:
        config_path = Path("config/advanced_rules.yaml")
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f)
                    rag_config = full_config.get("rag", {})
                    bridge.initialize(rag_config)
            except Exception as e:
                print(f"❌ Failed to initialize memory bridge: {e}")
                sys.exit(1)

    # Perform purge
    try:
        success = bridge.purge_persona_memory(args.persona)
        print("✅ Purged successfully" if success else "⚠️ Nothing to purge or purge failed")
    except Exception as e:
        print(f"❌ Purge failed: {e}")
        sys.exit(1)


def index_path_wrapper(bridge: MemoryBridge, src_path: str, namespaces: List[str],
                      persona: str, reindex: bool = False) -> bool:
    """Wrapper for indexing that handles different source types"""
    src = Path(src_path)

    if not src.exists():
        print(f"❌ Source path does not exist: {src_path}")
        return False

    total_docs = 0

    try:
        if src.is_file():
            # Index single file
            total_docs = index_single_file(bridge, src, namespaces, persona)
        elif src.is_dir():
            # Index directory
            total_docs = index_directory(bridge, src, namespaces, persona, reindex)
        else:
            print(f"❌ Unsupported source type: {src_path}")
            return False

        print(f"📊 Processed {total_docs} documents")
        return total_docs > 0

    except Exception as e:
        print(f"❌ Indexing failed: {e}")
        return False


def index_single_file(bridge: MemoryBridge, file_path: Path, namespaces: List[str],
                     persona: str) -> int:
    """Index a single file"""
    try:
        # Import appropriate indexer based on file type
        if file_path.suffix in ['.py', '.ts', '.js', '.java', '.cpp', '.c', '.h']:
            from memory.indexers.code_indexer import CodeIndexer
            indexer = CodeIndexer()
        elif file_path.suffix in ['.md', '.rst', '.txt']:
            from memory.indexers.md_indexer import MarkdownIndexer
            indexer = MarkdownIndexer()
        else:
            print(f"⚠️ Unsupported file type: {file_path}")
            return 0

        # Index the file
        docs = indexer.index_file(file_path)

        if not docs:
            print(f"⚠️ No content extracted from: {file_path}")
            return 0

        # Add persona metadata
        for doc in docs:
            doc["persona"] = persona
            if namespaces:
                doc["namespace"] = namespaces[0]  # Use first namespace as default

        # Store in vector database
        success = bridge.vector_store.store_documents(docs)

        if success:
            print(f"✅ Indexed: {file_path} ({len(docs)} chunks)")
            return len(docs)
        else:
            print(f"❌ Failed to store: {file_path}")
            return 0

    except Exception as e:
        print(f"❌ Failed to index {file_path}: {e}")
        return 0


def index_directory(bridge: MemoryBridge, dir_path: Path, namespaces: List[str],
                   persona: str, reindex: bool = False) -> int:
    """Index all files in a directory"""
    total_docs = 0

    # Supported file patterns
    patterns = []
    if "coder" in namespaces or not namespaces:
        patterns.extend(['**/*.py', '**/*.ts', '**/*.js', '**/*.java', '**/*.cpp', '**/*.c', '**/*.h'])
    if "docs" in namespaces or not namespaces:
        patterns.extend(['**/*.md', '**/*.rst', '**/*.txt'])
    if "tests" in namespaces or not namespaces:
        patterns.extend(['**/test*.py', '**/spec*.py', '**/*test*.py'])

    for pattern in patterns:
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                docs_count = index_single_file(bridge, file_path, namespaces, persona)
                total_docs += docs_count

    return total_docs


def cmd_doctor(args):
    """Run diagnostics on the memory system"""
    import os, importlib, sys
    mids = os.getenv("AR_EMBED_MODEL", "")
    print("model:", mids or "(default)")

    try:
        torch = importlib.import_module("torch")
        print("cuda?", getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception as e:
        print("torch check failed:", e)

    try:
        importlib.import_module("chromadb")
        print("chroma: ok")
    except Exception as e:
        print("chroma missing:", e)

    print("persist_dir:", os.getenv("AR_PERSIST_DIR", ".cache/chroma"))


def main(argv: Optional[List[str]] = None):
    """Main entry point for memory commands"""
    parser = argparse.ArgumentParser(
        prog="arx memory",
        description="AdvancedRules Memory CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arx memory index --src tools/ --namespaces coder,tests --persona CODER_AI
  arx memory query --persona CODER_AI --query "authentication patterns" --k 5
  arx memory stats
  arx memory purge --persona CODER_AI
  arx memory doctor
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Memory command to execute")

    # Index command
    index_parser = subparsers.add_parser("index", help="Index content into memory")
    index_parser.add_argument("--src", required=True, help="Source path to index")
    index_parser.add_argument("--namespaces", default="coder,tests,docs",
                            help="Comma-separated namespaces")
    index_parser.add_argument("--persona", default="GENERAL_AI",
                            help="Persona to associate with content")
    index_parser.add_argument("--reindex", action="store_true",
                            help="Reindex existing content")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query memory for context")
    query_parser.add_argument("--persona", required=True, help="Persona to query for")
    query_parser.add_argument("--query", required=True, help="Query string")
    query_parser.add_argument("--k", type=int, default=8, help="Number of results")

    # Stats command
    subparsers.add_parser("stats", help="Show memory statistics")

    # Purge command
    purge_parser = subparsers.add_parser("purge", help="Purge memory content")
    purge_parser.add_argument("--persona", required=True, help="Persona memory to purge")

    # Doctor command
    subparsers.add_parser("doctor", help="Run memory system diagnostics")

    # Parse arguments
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return

    args = parser.parse_args(argv)

    # Execute command
    if args.command == "index":
        cmd_index(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "purge":
        cmd_purge(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()