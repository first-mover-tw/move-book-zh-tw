---
title: 原始型別 (Primitive Types) | 參考手冊
description: Move 基本型別 (primitive types) 參考手冊：整數、布林值、地址、向量、參考、元組及單位型別概覽。
keywords:
  - Move
  - Sui
  - Move reference
  - primitive
  - types
  - reference
  - type system
questions:
  - How does Primitive Types work in Move?
  - What is the syntax for Primitive Types in Move?
answer: 'Move primitive types reference: integers, booleans, addresses, vectors, references, tuples, and unit type overview.'
goal:
  description: 'Reader understands move primitive types reference: integers, booleans, addresses, vectors, references, tuples, and unit type overview'
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

# 基本型別 (Primitive Types) {#primitive-types}

基本型別是此語言的基本建構元素。

這些基本型別可單獨使用，也可用來建立更複雜的使用者自訂型別，
例如 [`struct`](./structs)。

- [整數 (Integers)](./primitive-types/integers)
- [布林值 (Bool)](./primitive-types/bool)
- [地址 (Address)](./primitive-types/address)
- [向量 (Vector)](./primitive-types/vector)

這些基本型別會與其他型別搭配使用

- [參考 (References)](./primitive-types/references)
- [元組與單位型別 (Tuples and Unit)](./primitive-types/tuples)
