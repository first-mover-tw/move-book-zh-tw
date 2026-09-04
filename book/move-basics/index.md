---
description: 學習 Move 語言基礎（Learn Move language fundamentals）：型別、模組、函式、結構體、能力、泛型與流程控制，用於 Sui 智慧合約。
---

# Move 基礎 (Move Basics) {#move-basics}

本章涵蓋 Move 語言的基礎：語法、型別系統，以及每個 Move 程式所建立的基礎概念。本章聚焦於語言本身，大致上先擱置區塊鏈的部分——這裡的內容適用於任何 Move 程式,而 storage 與 Sui 特有的功能，將緊接在後從[物件模型 (Object Model)](./../object/) 章節開始介紹。

各小節彼此建立在前一節之上，建議依序閱讀：

- **程式碼如何組織：**[模組 (modules)](./module)、[註解 (comments)](./comments)、
  [基本型別 (primitive types)](./primitive-types)、[address 型別](./address)、
  [運算式 (expressions)](./expression)，以及[函式 (functions)](./function)。
- **定義自訂型別：**[結構 (structs)](./struct)，以及控制型別的值能做什麼的
  [能力系統 (ability system)](./abilities-introduction)——從
  [drop 能力](./drop-ability)開始。
- **重用既有程式碼：**[匯入 (imports)](./importing-modules)，以及
  [標準函式庫 (Standard Library)](./standard-library) 及其核心型別——[vector](./vector)、
  [Option](./option)，以及 [String](./string)。
- **撰寫邏輯：**[控制流程 (control flow)](./control-flow)、[列舉與模式比對 (enums with pattern
  matching)](./enum-and-match)、[結構方法 (struct methods)](./struct-methods)，以及
  [可見性修飾詞 (visibility modifiers)](./visibility)。
- **Move 安全機制的核心：**[所有權與作用域 (ownership and scope)](./ownership-and-scope)、
  [copy 能力](./copy-ability)、[常數 (constants)](./constants) 與
  [中止執行 (aborting execution)](./assert-and-abort)，以及[參考 (references)](./references)。
- **抽象化工具：**[泛型 (generics)](./generics)、[巨集函式 (macro functions)](./macros)、
  [內部許可 (internal permit)](./internal-permit)、[型別反射 (type reflection)](./type-reflection)，最後是
  [測試 (testing)](./testing)。

本章的每個程式碼範例都來自可編譯、經過測試的套件。大部分範例是放在測試函式內的節錄，因此你可以將其中任何一個複製到
[Hello World](./../your-first-move/hello-world) 章節建立的套件中，並用 `sui move test` 執行它們。
