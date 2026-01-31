import os
import sys
from pathlib import Path

from google import genai  # pip install google-genai

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
    try:
        # Paging through models to find ones that match 'gemini'
        print("Checking available models...")
        # Note: client.models.list returns an iterator
        for m in client.models.list():
            if "gemini" in m.name:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Warning: Could not list models: {e}")

    model_id = "gemini-1.5-pro"
    
    try:
        response = client.models.generate_content(
            model=model_id, 
            contents=msg
        )
    except Exception as e:
        print(f"Model {model_id} failed: {e}")
        print("Falling back to gemini-1.5-flash...")
        model_id = "gemini-1.5-flash"
        try:
            response = client.models.generate_content(
                model=model_id, 
                contents=msg
            )
        except Exception as e2:
             print(f"Model {model_id} also failed: {e2}")
             raise e2
        
    return response.text


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_to_zh_tw.py <file1> [<file2> ...]")
        sys.exit(1)

    # API key check moved to inside translate_markdown or init here, 
    # but strictly checking env var existence here is good too.
    if not os.environ.get("GEMINI_API_KEY"):
         raise RuntimeError("GEMINI_API_KEY is not set")

    for path_str in sys.argv[1:]:
        input_path = Path(path_str)
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"Translating {input_path} ...")
        try:
            translated = translate_markdown(input_path)
            
            # 輸出成 xxx.zh-TW.md
            output_path = input_path.with_name(input_path.stem + ".zh-TW.md")
            output_path.write_text(translated, encoding="utf-8")
            print(f"Wrote translated file to {output_path}")
        except Exception as e:
            print(f"Error translating {input_path}: {e}")
            sys.exit(1) # Fail the action if translation fails


if __name__ == "__main__":
    main()
