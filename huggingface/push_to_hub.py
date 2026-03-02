#!/usr/bin/env python3
"""
NRC Protein Folding — Hub Push Script
======================================
Pushes model card and source to HuggingFace Hub.
Requires:  pip install huggingface_hub
           huggingface-cli login   (or set HF_TOKEN env var)
"""
import argparse, os, sys
from pathlib import Path

def push(repo_id: str, card: str) -> None:
    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[error] pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token)

    print(f"[1/2] Creating / accessing repo: {repo_id} ...")
    create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False, token=token)

    print(f"[2/2] Uploading model card ...")
    api.upload_file(
        path_or_fileobj=card,
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
        commit_message="feat: Add NRC Protein Folding model card",
    )
    print(f"\n✓ View at: https://huggingface.co/{repo_id}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="Nexus-Resonance-Codex/nrc-Protein-Folding")
    parser.add_argument("--card", default=str(Path(__file__).parent / "MODEL_CARD.md"))
    args = parser.parse_args()
    push(args.repo_id, args.card)

if __name__ == "__main__":
    main()
