---
description: 進階 Move 語言功能：適用於 Sui 開發者的模式、延伸建置設定與進階程式設計技巧。
title: 進階 Move (Move) 用法
keywords:
  - Move
  - Sui
  - Move tutorial
  - advanced
  - move
  - usage
questions:
  - What are advanced Move features?
  - What is beyond Move basics?
answer: Advanced Move covers entry functions, visibility modes, macro functions, and other features beyond the language fundamentals.
goal:
  description: Reader understands advanced Move features like entry functions, visibility, and macros
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 30
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# Move 進階用法 (Advanced Move Usage) {#advanced-move-usage}

本章涵蓋 Move 語言的進階功能，包括用於進階程式設計的各種擴充行為。這包含語言本身的進階用法，以及套件與建置系統。

- [編譯模式](./modes) - 包含具名建置模式中不可發佈的原始碼。
- [入口函式](./entry-functions) - `entry` 修飾詞，以及使其成為安全交易邊界的靜態 hot-potato 保證。
