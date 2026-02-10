import os
import sys
import subprocess
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


def get_changed_md_files(diff_base: str) -> list[Path]:
    """Use git diff to find added/modified .md files (excluding .zh-TW.md)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AM", diff_base, "HEAD", "--", "*.md"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e.stderr}")
        return []

    files = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line or line.endswith(".zh-TW.md"):
            continue
        p = Path(line)
        if p.is_file():
            files.append(p)
    return files


def get_all_untranslated(dirs: list[str] = ("book", "reference")) -> list[Path]:
    """Find all .md files that don't have a .zh-TW.md counterpart."""
    files = []
    for root in dirs:
        if not os.path.isdir(root):
            continue
        for path in Path(root).rglob("*.md"):
            if path.name.endswith(".zh-TW.md"):
                continue
            target = path.with_name(path.stem + ".zh-TW.md")
            if target.exists():
                continue
            files.append(path)
    return files


def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files to zh-TW.")
    parser.add_argument("files", nargs="*", type=Path, help="Specific files to translate")
    parser.add_argument("--all", action="store_true", help="Translate all untranslated .md files")
    parser.add_argument("--diff-base", type=str, help="Git ref to diff against (only translate changed files)")
    parser.add_argument("--batch-size", type=int, default=5, help="Max files per run (default: 5)")
    parser.add_argument("--sleep", type=int, default=BETWEEN_FILES_WAIT, help="Seconds between files (default: 20)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    # Determine files to translate
    if args.diff_base:
        files_to_translate = get_changed_md_files(args.diff_base)
        print(f"Found {len(files_to_translate)} changed files (diff-base: {args.diff_base})")
    elif args.all:
        files_to_translate = get_all_untranslated()
        print(f"Found {len(files_to_translate)} untranslated files")
    elif args.files:
        files_to_translate = args.files
    else:
        print("No files specified. Use --all, --diff-base, or pass file paths.")
        return

    # Apply batch size limit
    if len(files_to_translate) > args.batch_size:
        print(f"Limiting to {args.batch_size} files (out of {len(files_to_translate)})")
        files_to_translate = files_to_translate[:args.batch_size]

    if not files_to_translate:
        print("No files to translate.")
        return

    translated_count = 0
    failed_files = []

    for i, input_path in enumerate(files_to_translate):
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"[{i+1}/{len(files_to_translate)}] Translating {input_path} ...")

        try:
            translated = translate_markdown(client, input_path)
            output_path = input_path.with_name(input_path.stem + ".zh-TW.md")
            output_path.write_text(translated, encoding="utf-8")
            print(f"  -> {output_path}")
            translated_count += 1

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
