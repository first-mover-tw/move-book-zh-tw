---
description: Move 函式庫 (Move libraries) 開放原始碼指南：Sui 可重複使用套件的命名慣例、文件、測試與發布。
title: 程式庫 (Libraries) 開放原始碼
keywords:
  - Move
  - Sui
  - Move tutorial
  - open
  - sourcing
  - libraries
questions:
  - What is Open Sourcing Libraries in Move?
  - How do I use Open Sourcing Libraries in Move?
  - What is README in Move?
  - What is Named Addresses in Move?
answer: 'Guide to open sourcing Move libraries: naming conventions, documentation, testing, and publishing reusable packages for Sui.'
goal:
  description: 'Reader understands guide to open sourcing Move libraries: naming conventions, documentation, testing, and publishing reusable packages for Sui'
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 50
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 將函式庫開放原始碼 (Open Sourcing Libraries) {#open-sourcing-libraries}

將函式庫開放原始碼是為 Move 生態系做出貢獻的絕佳方式。本指南將協助你
了解如何將函式庫開放原始碼、如何撰寫測試，以及如何為函式庫編寫文件。

## README {#readme}

TODO：readme

## 命名地址 (Named Addresses) {#named-addresses}

TODO：命名地址

## 產生文件 (Generating Documentation) {#generating-documentation}

TODO：docgen

## 新增範例 (Adding Examples) {#adding-examples}

發布預定供他人使用的套件（NFT 協定或函式庫）時，
展示此套件的使用方式相當重要。這正是範例派上用場的地方。Move 沒有
針對範例的特殊功能，但有一些用於標記範例的慣例。首先，只有原始碼會納入套件位元碼，
因此放在不同目錄中的任何程式碼都不會被納入，但仍會接受測試！

因此，將範例放在獨立的 `examples/` 目錄是個好主意。

```bash
sources/
    protocol.move
    library.move
tests/
    protocol_test.move
examples/
    my_example.move
Move.toml
```

## 標籤與發行版本 (Git) (Tags and Releases (Git)) {#tags-and-releases-git}

TODO：標籤與發行版本

## 實現與封閉原始碼相容的技巧 (Tricks to allow compatibility with closed source) {#tricks-to-allow-compatibility-with-closed-source}

TODO：透過具有簽章的空函式實現相容性
