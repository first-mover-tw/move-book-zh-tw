import os
import sys
from pathlib import Path

from google import genai  # pip install google-genai

import argparse
import time

def translate_markdown(input_path: Path):
    text = input_path.read_text(encoding="utf-8")

    # Prompt optimization for Gemini
    system_prompt = (
        "You are a professional technical translator.\n"
        "Translate the following Markdown content into Traditional Chinese (Taiwan).\n"
        "Preserve all Markdown structure, links, images, and code blocks.\n"
        "Do NOT translate code, but DO translate comments inside code blocks.\n"
        "Keep Move/Sui related technical terms accurate and natural in zh-TW."
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
        
    client = genai.Client(api_key=api_key)

    msg = (
        system_prompt
        + "\n\nMarkdown to translate:\n\n"
        + text
        + "\n\nReturn only the translated Markdown, no explanation."
    )

    # Updated to use the new SDK method and explicitly target gemini-2.0-flash or gemini-1.5-pro
    # Try Pro first, then Flash as fallback
    # DEBUG: List models to confirm availability
    # (Skipped re-listing to reduce noise, assuming user fixed model per previous step)

    # Optimized Approach: Use Flash specific model for higher key limits and speed.
    # Pro model usage on free tier is very limited (2 RPM / 32k TPM), whereas Flash is higher (15 RPM / 1M TPM).
    # To be "efficient", we must use Flash for batch processing.
    model_id = "gemini-2.5-flash" 
    
    max_retries = 5
    base_wait = 20 # seconds

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_id, 
                contents=msg
            )
            return response.text
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = base_wait * (attempt + 1)
                print(f"Rate limit hit for {model_id}. Waiting {wait_time}s before retry ({attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            elif "404" in error_str and model_id == "gemini-2.5-flash":
                 print("Gemini 2.5 Flash not found, trying 1.5 Flash...")
                 model_id = "gemini-1.5-flash"
                 continue
            else:
                print(f"Error: {e}")
                # For non-retriable errors or max retries, we might want to stop or raise
                if attempt == max_retries - 1:
                    raise e
                # General error, maybe temporary? wait briefly
                time.sleep(5)
    
    raise RuntimeError(f"Failed to translate after {max_retries} attempts.")


def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files to Traditional Chinese.")
    parser.add_argument("files", nargs="*", type=Path, help="Specific files to translate")
    parser.add_argument("--all", action="store_true", help="Scan and translate all untranslated .md files in book/ and reference/")
    args = parser.parse_args()

    # API key check
    if not os.environ.get("GEMINI_API_KEY"):
         raise RuntimeError("GEMINI_API_KEY is not set")

    files_to_translate = []
    
    if args.all:
        for root in ["book", "reference"]:
            if not os.path.isdir(root):
                continue
            for path in Path(root).rglob("*.md"):
                # Skip already translated files
                if path.name.endswith(".zh-TW.md"):
                    continue
                # Check if translation already exists to avoid re-translating (optional, but good for saving quota)
                target_path = path.with_name(path.stem + ".zh-TW.md")
                if target_path.exists():
                    print(f"Skipping {path} (already translated)")
                    continue
                    
                files_to_translate.append(path)
    else:
        files_to_translate = args.files

    if not files_to_translate:
        print("No files to translate.")
        return

    print(f"Found {len(files_to_translate)} files to translate.")

    for i, input_path in enumerate(files_to_translate):
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"[{i+1}/{len(files_to_translate)}] Translating {input_path} ...")
        
        try:
            translated = translate_markdown(input_path)
            
            output_path = input_path.with_name(input_path.stem + ".zh-TW.md")
            output_path.write_text(translated, encoding="utf-8")
            print(f"Wrote translated file to {output_path}")
            
            # Rate limit mitigation: 
            # With Flash model, limits are higher. A small buffer is still good.
            time.sleep(2)
            
        except Exception as e:
            print(f"Error translating {input_path}: {e}")
            # Do not exit immediately, try next file? 
            # Or exit to fail the workflow? 
            # For automation, maybe fail so we know. But let's try to continue for partial success.
            # actually better to fail so we don't commit partial state as 'success'
            # But with --all, maybe we want to get as much done as possible.
            print("Skipping file due to error.")
            continue

if __name__ == "__main__":
    main()
