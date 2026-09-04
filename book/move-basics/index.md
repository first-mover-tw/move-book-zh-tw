---
description: 學習 Sui 智慧合約的 Move 語言基礎：型別 (types)、模組 (modules)、函式 (functions)、結構 (structs)、能力 (abilities)、泛型 (generics) 與控制流程 (control flow)。
title: Move 基礎 (Move)
keywords:
  - Move
  - Sui
  - Move tutorial
  - move
  - basics
questions:
  - What are the basics of Move?
  - What Move features should I learn first?
answer: Move basics covers modules, functions, primitive types, structs, abilities, generics, control flow, constants, strings, and other foundational language features.
goal:
  description: Reader understands what Move language fundamentals this section covers
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

# Move 基礎 (Move Basics) {#move-basics}

本章介紹 Move 語言的基礎：語法、型別系統，以及每個 Move 程式所建構於其上的概念。本章聚焦於語言本身，並大致先不討論區塊鏈——此處的所有內容都適用於任何 Move 程式；儲存與 Sui 特有的功能則會在接下來的 [物件模型](./../object/) 章節中介紹。

各節內容會逐步建立於前一節之上，建議依序閱讀：

- **程式碼的組織方式：**[模組](./module)、[註解](./comments)、
  [原始型別](./primitive-types)、[地址型別](./address)、
  [運算式](./expression)與[函式](./function)。
- **定義自訂型別：**[結構](./struct)，以及控制型別值可執行哪些操作的
  [能力系統](./abilities-introduction)——從 [drop](./drop-ability) 開始。
- **重複使用既有程式碼：**[匯入](./importing-modules)，以及具備核心型別的
  [標準函式庫](./standard-library)——[vector](./vector)、
  [Option](./option) 與 [String](./string)。
- **撰寫邏輯：**[控制流程](./control-flow)、具備模式比對的
  [列舉](./enum-and-match)、[結構方法](./struct-methods)，以及
  [可見性修飾詞](./visibility)。
- **Move 安全性核心：**[所有權與範圍](./ownership-and-scope)、
  [copy 能力](./copy-ability)、[常數](./constants)與
  [中止執行](./assert-and-abort)，以及[參考](./references)。
- **抽象化工具：**[泛型](./generics)、[巨集函式](./macros)、
  [內部許可](./internal-permit)、[型別反射](./type-reflection)，最後是
  [測試](./testing)。

本章中的每個程式碼範例都來自可編譯且已測試的套件。大多數範例都是放置於測試函式內的摘錄，因此你可以將任何範例複製到 [Hello World](./../your-first-move/hello-world) 章節建立的套件中，並以 `sui move test` 執行它們。
