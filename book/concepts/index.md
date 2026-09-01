---
description: Sui 和 Move 的核心概念：套件 (package)、帳戶 (account)、交易 (transaction)、地址 (address)，以及資料
  (data) 如何儲存在 Sui 區塊鏈 (blockchain) 上。
title: 概念 (Concepts)
keywords:
- Move
- Sui
- Move tutorial
- concepts
questions:
- What are the core concepts in Move?
- How are Move packages structured?
- What is Move.toml?
answer: Core Move concepts include packages (units of code organization), the Move.toml
  manifest, named addresses, and the account/address model on Sui.
goal:
  description: Reader understands packages, manifests, addresses, and accounts in
    Move
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

# 概念 (Concepts) {#concepts}

在本章中，您將學習 Sui 和 Move 的基本概念：什麼是 package 以及如何與其互動，什麼是 account 和 transaction，以及資料如何在 Sui 上儲存。儘管本章不是一份完整的參考文件——關於這點請參閱 [Sui Documentation](https://docs.sui.io)——但它將讓您對在 Sui 上撰寫 Move 程式所需的概念有充分的理解。
