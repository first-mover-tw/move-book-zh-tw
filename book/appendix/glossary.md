---
description: Move 與 Sui 術語 (terminology) 詞彙表：快速路徑 (fast path)、平行執行 (parallel execution)、內部型別 (internal types) 以及其他重要概念的定義。
title: '附錄 A: 詞彙表 (Glossary)'
keywords:
  - Move
  - Sui
  - Move tutorial
  - appendix
  - glossary
questions:
  - What does this Move term mean?
  - Where is the Move glossary?
answer: The glossary defines key terms in the Move language and Sui ecosystem including abilities, objects, modules, packages, and blockchain concepts.
goal:
  description: Reader can look up definitions of Move and Sui terminology
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

# 附錄 A：詞彙表 (Appendix A: Glossary) {#appendix-a-glossary}

- 快速路徑 (Fast Path) - 用於描述一種不涉及共享物件，且無需共識即可執行的交易。
- 平行執行 (Parallel Execution) - 用於描述 Sui 執行時期平行執行交易的能力，包含涉及共享物件的交易。
- 內部型別 (Internal Type) - 模組內部定義的型別。此型別的欄位無法從模組外部存取，且在只有「key」能力的情況下，無法用於 `public_*` 傳輸函式。

## 能力 (Abilities) {#abilities}

- `key` - 允許結構體在儲存中作為鍵使用的能力。在 Sui 上，`key` 能力會標記物件，並要求第一個欄位為 `id: UID`。
- `store` - 允許結構體儲存在其他物件內部的能力。此能力放寬了對內部結構體的限制，允許 `public_*` 傳輸函式接受它們作為引數。它還允許物件作為動態欄位儲存。
- `copy` - 允許結構體被複製的能力。在 Sui 上，`copy` 能力與 `key` 能力衝突，不能與之一起使用。
- `drop` - 允許結構體被忽略或捨棄的能力。在 Sui 上，`drop` 能力不能與 `key` 能力一起使用，因為物件不允許被忽略。
