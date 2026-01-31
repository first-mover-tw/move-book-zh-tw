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

    # Optimized Approach: Try a sequence of fast models.
    # Update models based on 2026 availability (User checked screenshot: 2.5 Flash, 3.0 Flash Preview)
    models_to_try = ["gemini-2.5-flash", "gemini-3.0-flash-preview", "gemini-2.0-flash-exp"]
    
    max_retries = 3
    base_wait = 60 # Aggressive backoff: wait 1 minute if hit rate limit to clear the bucket

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                # print(f"Trying {model_name} (attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name, 
                    contents=msg
                )
                return response.text
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"Rate limit for {model_name} (Attempt {attempt+1}/{max_retries}). Waiting {base_wait}s...")
                    # Print details to debug if it's daily limit vs minute limit
                    # print(f"DEBUG: {error_str}") 
                    time.sleep(base_wait)
                elif "404" in error_str:
                     print(f"Model {model_name} not found. Skipping.")
                     break # Try next model immediately
                else:
                    print(f"Error with {model_name}: {e}")
                    time.sleep(5)
    
    raise RuntimeError(f"All models failed after retries.")


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
            # Google Free Tier (Flash) has ~15 RPM limit. 
            # Sleeping 10s + processing time ensures we stay well below this.
            # Slow and steady wins the race.
            print("Sleeping for 10s to respect rate limits...")
            time.sleep(10)
            
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
