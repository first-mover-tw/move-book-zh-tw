---
description: 官方 Move 語言參考手冊：涵蓋語法 (syntax)、型別 (types)、能力 (abilities)、函式 (functions) 及所有語言功能 (language features) 的完整文件。
title: Move 參考手冊
keywords:
  - Move
  - Sui
  - Move reference
  - move
  - reference
questions:
  - Where is the Move language reference?
  - What does the Move reference cover?
answer: The Move Reference is the comprehensive language specification covering syntax, types, abilities, functions, and all features of the Move programming language.
goal:
  description: Reader can navigate the Move language reference to find detailed documentation
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

# Move 參考文件 (The Move Reference) {#the-move-reference}

_由 Move 貢獻者撰寫，並由 Move 社群貢獻內容後調整為適用於 Sui_

歡迎使用 Move，這是一種用於安全資產程式設計的次世代語言。其主要使用案例是在
區塊鏈環境中，Move 程式用於建構狀態變更。Move 讓
開發者能夠撰寫可彈性管理及轉移資產的程式，同時提供針對這些資產之攻擊的安全性
與保護。然而，Move 的開發也考量了區塊鏈情境以外的使用案例。

Move 借鑑 [Rust](https://www.rust-lang.org/)，使用具備 move（因此得名）
語意的資源型別，作為貨幣等數位資產的明確表示方式。

<!-- TODO：我們是否有可複製到這裡的既有摘要？ -->
