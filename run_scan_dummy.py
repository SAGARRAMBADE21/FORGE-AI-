#!/usr/bin/env python3
"""Run scanner non-interactively against `examples/dummy_frontend`.

This uses local embeddings (if available) and will not call OpenAI.
"""
from pathlib import Path
from rich.console import Console

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

console = Console()


def main():
    project_path = Path("examples/dummy_frontend").resolve()
    output_dir = Path("scan-output-dummy").resolve()

    console.print(f"Using project: {project_path}")
    console.print(f"Output dir: {output_dir}")

    config = ScannerConfig(project_root=project_path, output_dir=output_dir)
    config.embedding.provider = "local"

    # Prevent automatic download/initialization of HuggingFace models during this run.
    # This forces the embedder to be unavailable and the workflow to continue
    # without remote downloads (useful when network or large downloads are undesired).
    try:
        import frontend_scanner.agents.embedder as _embedder_module
        _embedder_module.HUGGINGFACE_AVAILABLE = False
    except Exception:
        pass

    config.ensure_directories()

    workflow = create_scanner_workflow(config)

    console.print("\nStarting non-interactive scan on dummy frontend...\n")

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
