import os
import sys
from pathlib import Path

import google.genai as genai  # pip install google-genai[web:137][web:140]


def translate_markdown(input_path: Path, client: genai.Client):
    text = input_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are a professional technical translator.\n"
        "Translate the following Markdown content into Traditional Chinese (Taiwan).\n"
        "Preserve all Markdown structure, links, images, and code blocks.\n"
        "Do NOT translate code, but DO translate comments inside code blocks.\n"
        "Keep Move/Sui related technical terms accurate and natural in zh-TW."
    )

    # 使用新版 client.responses.create[web:133][web:140]
    resp = client.responses.create(
        model="gemini-1.5-flash-001",  # 選一個在 v1 API 可用的模型 ID
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )

    # 將多段輸出組合成一個字串
    parts = []
    for item in resp.output_candidates[0].content.parts:
        if item.text:
            parts.append(item.text)
    return "\n".join(parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_to_zh_tw.py <file1> [<file2> ...]")
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    for path_str in sys.argv[1:]:
        input_path = Path(path_str)
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"Translating {input_path} ...")
        translated = translate_markdown(input_path, client)

        # 輸出成 xxx.zh-TW.md
        output_path = input_path.with_name(input_path.stem + ".zh-TW.md")
        output_path.write_text(translated, encoding="utf-8")
        print(f"Wrote translated file to {output_path}")


if __name__ == "__main__":
    main()
