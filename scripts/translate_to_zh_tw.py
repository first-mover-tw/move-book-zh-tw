import os
import sys
from pathlib import Path
from openai import OpenAI

def translate_markdown(input_path: Path, client: OpenAI):
    text = input_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are a professional technical translator.\n"
        "Translate the following Markdown content into Traditional Chinese (Taiwan).\n"
        "Preserve all Markdown structure, links, images, and code blocks.\n"
        "Do NOT translate code, but DO translate comments inside code blocks.\n"
        "Keep technical terms for Move/Sui consistent and natural in zh-TW."
    )

    # 使用新版 SDK 的 responses API[web:106][web:99]
    resp = client.responses.create(
        model="gpt-4.1-mini",  # 或你有權限的其他模型
        instructions=system_prompt,
        input=text,
    )

    translated = resp.output_text
    return translated


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/translate_to_zh_tw.py <file1> [<file2> ...]")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)

    for path_str in sys.argv[1:]:
        input_path = Path(path_str)
        if not input_path.is_file():
            print(f"Skip (not a file): {input_path}")
            continue

        print(f"Translating {input_path} ...")
        translated = translate_markdown(input_path, client)

        # output_path = input_path.with_suffix(input_path.suffix + ".zh-TW")
        # 例如 input: xxx.md -> output: xxx.md.zh-TW，你也可以改成 .zh-TW.md
        # 如果你想要 .zh-TW.md，可以用：
        output_path = input_path.with_name(input_path.stem + ".zh-TW.md")

        output_path.write_text(translated, encoding="utf-8")
        print(f"Wrote translated file to {output_path}")


if __name__ == "__main__":
    main()
