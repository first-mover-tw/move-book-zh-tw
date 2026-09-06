---
title: 布林 (Bool) | 參考手冊
description: Move 布林 (bool) 型別參考：`true` 與 `false` 常值、邏輯運算子（and、or、not），以及布林運算式語意。
keywords:
  - Move
  - Sui
  - Move reference
  - bool
  - reference
questions:
  - How does Bool work in Move?
  - What is the syntax for Bool in Move?
  - What is Literals in Move?
  - What is Operations in Move?
answer: 'Move bool type reference: true and false literals, logical operators (and, or, not), and boolean expression semantics.'
goal:
  description: 'Reader understands move bool type reference: true and false literals, logical operators (and, or, not), and boolean expression semantics'
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

# 真偽值 (Bool) {#bool}

`bool` 是 Move 用於布林 `true` 與 `false` 值的基本型別。

## 常值 (Literals) {#literals}

`bool` 的常值為 `true` 或 `false`。

## 運算 (Operations) {#operations}

### 邏輯運算 (Logical) {#logical}

`bool` 支援三種邏輯運算：

| 語法                      | 說明         | 等價運算式                                                |
| ------------------------- | ------------ | --------------------------------------------------------- |
| `&&`                      | 短路邏輯 AND | `p && q` 等價於 `if (p) q else false`                     |
| <code>&vert;&vert;</code> | 短路邏輯 OR  | <code>p &vert;&vert; q</code> 等價於 `if (p) true else q` |
| `!`                       | 邏輯否定     | `!p` 等價於 `if (p) false else true`                      |

### 控制流程 (Control Flow) {#control-flow}

`bool` 值可用於數種 Move 的控制流程建構：

- [`if (bool) { ... }`](./../control-flow/conditionals)
- [`while (bool) { .. }`](./../control-flow/loops)
- [`assert!(bool, u64)`](./../abort-and-assert)

## 所有權 (Ownership) {#ownership}

與語言內建的其他純量值相同，真偽值可隱含複製，
也就是可以在不使用明確指令（例如
[`copy`](.././variables#move-and-copy)）的情況下複製。
