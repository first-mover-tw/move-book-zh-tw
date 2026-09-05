---
description: Move (Move) 中的包裝器 (Wrapper) 型別模式：透過將現有型別包裝於新結構中，建立受限制或擴充版本。
title: 模式 (Pattern)：包裝器型別 (Wrapper Type)
keywords:
  - Move
  - Sui
  - Move tutorial
  - pattern
  - wrapper
  - type
  - design patterns
  - type system
questions:
  - 'What is Pattern: Wrapper Type in Move?'
  - 'How do I use Pattern: Wrapper Type in Move?'
  - What is Definition in Move?
  - What is Common Practices in Move?
answer: 'The Wrapper type pattern in Move: create restricted or extended versions of existing types by wrapping them in new structs.'
goal:
  description: 'Reader understands the Wrapper type pattern in Move: create restricted or extended versions of existing types by wrapping them in new structs'
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

# 模式：包裝型別 (Pattern: Wrapper Type) {#pattern-wrapper-type}

有時候，需要建立一個行為類似既有型別、但具有特定修改或限制的新型別。例如，你可能想建立一個行為如同向量、但不允許在插入元素後修改元素的[集合型別](./collections)。包裝型別模式是實現此目標的有效方式。

## 定義 (Definition) {#definition}

包裝型別模式是一種設計模式，其中你建立一個包裝既有型別的新型別。包裝型別與原始型別不同，但可在兩者之間互相轉換。

它通常會實作為只有一個欄位的[位置結構](./../move-basics/struct.md#positional-structs)。

```move file=packages/samples/sources/programmability/wrapper-type-pattern.move anchor=main

```

## 常見作法 (Common Practices) {#common-practices}

當目標是擴充既有型別的行為時，通常會為被包裝的型別提供存取子。這種作法可讓使用者在需要時直接存取底層型別。例如，在下列程式碼中，我們為 Stack 型別提供 `inner()`、`inner_mut()` 與 `into_inner()` 方法。

```move file=packages/samples/sources/programmability/wrapper-type-pattern.move anchor=common

```

## 優點 (Advantages) {#advantages}

包裝型別模式提供數項優點：

- 自訂函式：可讓你為既有型別定義自訂函式。
- 穩健的函式簽章：將函式簽章限制為新型別，因而讓程式碼更加穩健。
- 可讀性提升：透過提供更具描述性的型別名稱，通常可提升程式碼的可讀性。

## 缺點 (Disadvantages) {#disadvantages}

包裝型別模式在兩種情境中相當強大：當你想限制既有型別的行為，同時為相同資料結構提供自訂介面時；以及當你想擴充既有型別的行為時。然而，它仍有一些限制：

- 冗長：實作時可能相當冗長，尤其是當你想公開被包裝型別的所有方法時。
- 精簡實作：實作可能相當精簡，因為它通常只會將呼叫轉送至被包裝型別。

## 後續步驟 (Next Steps) {#next-steps}

包裝型別模式非常實用，尤其是搭配集合型別使用時，如前一節所示。下一節將介紹[動態欄位](./dynamic-fields)——這是一項重要的基本元素，可啟用[動態集合](./dynamic-collections)，讓你能以更具彈性但成本更高的方式儲存大量資料。
