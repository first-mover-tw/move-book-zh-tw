import json
import os
import subprocess
import sys
import argparse
import time
from pathlib import Path

from google import genai  # pip install google-genai


SYSTEM_PROMPT = (
    "You are a professional technical translator.\n"
    "Translate the following Markdown content into Traditional Chinese (Taiwan).\n"
    "Preserve all Markdown structure, links, images, and code blocks.\n"
    "Do NOT translate code, but DO translate comments inside code blocks.\n"
    "Keep Move/Sui related technical terms accurate and natural in zh-TW."
)

MODELS = ["gemini-2.5-flash", "gemini-3.0-flash-preview", "gemini-2.0-flash-exp"]
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 60
BETWEEN_FILES_WAIT = 20

MANIFEST_PATH = Path("scripts/translation-manifest.json")


def load_manifest() -> dict[str, str]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest: dict[str, str]):
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def git_hash_object(path: str) -> str:
    """Get blob hash of a file from a git ref, or from working tree."""
    result = subprocess.run(
        ["git", "hash-object", path],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def git_hash_object_ref(ref: str, path: str) -> str | None:
    """Get blob hash of a file at a specific git ref."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"{ref}:{path}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def detect_changed_files(english_ref: str = "english-main",
                         dirs: list[str] = ("book", "reference")) -> list[Path]:
    """Compare manifest against english-main blob hashes to find files needing translation."""
    manifest = load_manifest()
    changed = []

    for root in dirs:
        # List all .md files on the english ref
        try:
            result = subprocess.run(
                ["git", "ls-tree", "-r", "--name-only", english_ref, root],
                capture_output=True, text=True, check=True,
            )
        except subprocess.CalledProcessError:
            continue

        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line.endswith(".md"):
                continue
            eng_hash = git_hash_object_ref(english_ref, line)
            if eng_hash is None:
                continue
            if manifest.get(line) != eng_hash:
                changed.append(Path(line))

    return changed


def translate_markdown(client, input_path: Path) -> str:
    text = input_path.read_text(encoding="utf-8")
    msg = (
        SYSTEM_PROMPT
        + "\n\nMarkdown to translate:\n\n"
        + text
        + "\n\nReturn only the translated Markdown, no explanation."
    )

    for model_name in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model_name, contents=msg
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"  Rate limit ({model_name}, attempt {attempt+1}/{MAX_RETRIES}). Waiting {RATE_LIMIT_WAIT}s...")
                    time.sleep(RATE_LIMIT_WAIT)
                elif "404" in error_str:
                    print(f"  Model {model_name} not found, skipping.")
                    break
                else:
                    print(f"  Error with {model_name}: {e}")
                    time.sleep(5)

    raise RuntimeError("All models failed after retries.")


def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files to zh-TW.")
    parser.add_argument("files", nargs="*", type=Path, help="Specific files to translate")
    parser.add_argument("--all", action="store_true", help="Translate all untranslated/outdated files")
    parser.add_argument("--detect", action="store_true", help="Print files needing translation (manifest vs english-main)")
    parser.add_argument("--english-ref", type=str, default="english-main", help="Git ref for english source (default: english-main)")
    parser.add_argument("--batch-size", type=int, default=5, help="Max files per run (default: 5)")
    parser.add_argument("--sleep", type=int, default=BETWEEN_FILES_WAIT, help="Seconds between files (default: 20)")
    args = parser.parse_args()

    # --detect mode: just print files and exit
    if args.detect:
        changed = detect_changed_files(args.english_ref)
        for f in changed:
            print(f)
        print(f"\n{len(changed)} file(s) need translation.", file=sys.stderr)
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    # Determine files to translate
    if args.all:
        files_to_translate = detect_changed_files(args.english_ref)
        print(f"Found {len(files_to_translate)} files needing translation")
    elif args.files:
        files_to_translate = args.files
    else:
        print("No files specified. Use --all, --detect, or pass file paths.")
        return

    # Apply batch size limit
    if len(files_to_translate) > args.batch_size:
        print(f"Limiting to {args.batch_size} files (out of {len(files_to_translate)})")
        files_to_translate = files_to_translate[:args.batch_size]

    if not files_to_translate:
        print("No files to translate.")
        return

    manifest = load_manifest()
    translated_count = 0
    failed_files = []

    for i, input_path in enumerate(files_to_translate):
        input_path = Path(input_path)
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        # Get english blob hash before translation
        try:
            eng_hash = git_hash_object(str(input_path))
        except subprocess.CalledProcessError:
            eng_hash = None

        print(f"[{i+1}/{len(files_to_translate)}] Translating {input_path} ...")

        try:
            translated = translate_markdown(client, input_path)
            # Overwrite the file in-place (no .zh-TW suffix)
            input_path.write_text(translated, encoding="utf-8")
            print(f"  -> {input_path} (overwritten)")
            translated_count += 1

            # Update manifest
            if eng_hash:
                manifest[str(input_path)] = eng_hash
                save_manifest(manifest)

            # Sleep between files (skip after last file)
            if i < len(files_to_translate) - 1:
                print(f"  Sleeping {args.sleep}s...")
                time.sleep(args.sleep)

        except Exception as e:
            print(f"  ERROR: {e}")
            failed_files.append(str(input_path))
            continue

    print(f"\nDone: {translated_count} translated, {len(failed_files)} failed.")
    if failed_files:
        print("Failed files:")
        for f in failed_files:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
