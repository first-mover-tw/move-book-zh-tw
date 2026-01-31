import os
import sys
from pathlib import Path

import google.generativeai as genai  # pip install google-generativeai


def translate_markdown(input_path: Path):
    text = input_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are a professional technical translator.\n"
        "Translate the following Markdown content into Traditional Chinese (Taiwan).\n"
        "Preserve all Markdown structure, links, images, and code blocks.\n"
        "Do NOT translate code, but DO translate comments inside code blocks.\n"
        "Keep Move/Sui related technical terms accurate and natural in zh-TW."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")  # 有免費額度且價格便宜[web:128][web:140]

    prompt = (
        system_prompt
        + "\n\nMarkdown to translate:\n\n"
        + text
        + "\n\nReturn only the translated Markdown, no explanation."
    )

    resp = model.generate_content(prompt)
    return resp.text


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_to_zh_tw.py <file1> [<file2> ...]")
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)

    for path_str in sys.argv[1:]:
        input_path = Path(path_str)
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"Translating {input_path} ...")
        translated = translate_markdown(input_path)

        # 輸出檔名：xxx.zh-TW.md
        output_path = input_path.with_name(input_path.stem + ".zh-TW.md")
        output_path.write_text(translated, encoding="utf-8")
        print(f"Wrote translated file to {output_path}")


if __name__ == "__main__":
    main()
