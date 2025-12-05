#!/usr/bin/env python3
"""Non-interactive runner for Frontend Scanner (safe, no OpenAI calls).

This script creates a ScannerConfig pointed at the test fixture
`tests/fixtures/sample_react`, switches the embedding provider to
`local` (so external OpenAI calls are avoided), runs the LangGraph workflow,
and prints a short summary. Intended for CI-like runs.
"""
from pathlib import Path
from rich.console import Console

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

console = Console()


def main():
    project_path = Path("tests/fixtures/sample_react").resolve()
    output_dir = Path("scan-output-noninteractive").resolve()

    console.print(f"Using project: {project_path}")
    console.print(f"Output dir: {output_dir}")

    config = ScannerConfig(project_root=project_path, output_dir=output_dir)

    # Use local embeddings (if available). If not available, embedder will return empty embeddings
    # and the workflow will continue without calling external APIs.
    config.embedding.provider = "local"

    # Ensure directories exist
    config.ensure_directories()

    # Create workflow
    workflow = create_scanner_workflow(config)

    console.print("\nStarting non-interactive scan...\n")

    result = workflow.invoke({
        "config": config,
        "file_inventory": None,
        "parsed_files": [],
        "chunks": [],
        "embeddings": [],
        "summaries": [],
        "manifest": None,
        "vector_index": None,
        "logs": []
    })

    console.print("\nScan finished. Summary:\n")

    if result.get("manifest"):
        manifest = result["manifest"]
        console.print(f"  Files scanned: {manifest.file_inventory.get('total_files', 0)}")
        console.print(f"  Framework: {manifest.framework or 'Unknown'}")
        console.print(f"  Components: {len(manifest.components)}")
        console.print(f"  Routes: {len(manifest.routes)}")
        console.print(f"  API Calls: {len(manifest.api_calls)}")

    console.print(f"Logs: {len(result.get('logs', []))}")
    console.print("Done.")


if __name__ == '__main__':
    main()
