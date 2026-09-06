---
title: 控制流程 (Control Flow) | 參考手冊
description: Move 控制流程 (control flow) 參考手冊：if 運算式 (if expressions)、while 與 for 迴圈 (loops)、標籤區塊 (labeled blocks)、模式比對 (pattern matching)，以及提早回傳 (early returns)。
keywords:
  - Move
  - Sui
  - Move reference
  - control
  - flow
  - reference
questions:
  - How does Control Flow work in Move?
  - What is the syntax for Control Flow in Move?
answer: 'Move control flow reference: if expressions, while and for loops, labeled blocks, pattern matching, and early returns.'
goal:
  description: 'Reader understands move control flow reference: if expressions, while and for loops, labeled blocks, pattern matching, and early returns'
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

# 控制流程 (Control Flow) {#control-flow}

Move 提供多種以[布林運算式](./primitive-types/bool)為基礎的控制流程建構，包括常見的程式設計建構，例如 `if` 運算式以及 `while` 與 `for` 迴圈，也包含進階控制流程結構，例如迴圈標籤與可跳離的具名區塊。它也支援以結構化模式比對為基礎的更複雜建構。

- [條件運算式](./control-flow/conditionals)
- [模式比對](./control-flow/pattern-matching)
- [迴圈](./control-flow/loops)
- [標籤式控制流程](./control-flow/labeled-control-flow)
