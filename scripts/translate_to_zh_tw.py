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

    model_id = "gemini-2.5-pro"
    
    try:
        response = client.models.generate_content(
            model=model_id, 
            contents=msg
        )
    except Exception as e:
        print(f"Model {model_id} failed: {e}")
        # Add a small delay before fallback to let quota cool down slightly if it was a rate limit
        time.sleep(5)
        print("Falling back to gemini-2.5-flash...")
        model_id = "gemini-2.5-flash"
        try:
            response = client.models.generate_content(
                model=model_id, 
                contents=msg
            )
        except Exception as e2:
             print(f"Model {model_id} also failed: {e2}")
             print("Falling back to gemini-3.0-flash-preview...")
             model_id = "gemini-3.0-flash-preview"
             response = client.models.generate_content(
                model=model_id, 
                contents=msg
             )
        
    return response.text


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
            
            # Rate limit mitigation: Sleep 15 seconds between files
            # Google Free Tier often has 15 RPM (Requests Per Minute) limits
            print("Sleeping for 15s to respect rate limits...")
            time.sleep(15)
            
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
