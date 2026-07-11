---
description: 包裝器型別模式 (The Wrapper type pattern) in Move：透過將既有型別包裝進新的結構體 (struct) 中，建立受限制或擴充版本的型別。
---

# 模式：包裝型別 (Pattern: Wrapper Type) {#pattern-wrapper-type}

有時候，我們需要建立一個新的型別，其行為類似於現有型別，但帶有特定的修改或限制。舉例來說，你可能想建立一個
[collection type](./collections)，其行為類似 vector，但不允許在元素被插入後修改它們。包裝型別模式是達成此目的的有效方法。

## 定義 (Definition) {#definition}

包裝型別模式是一種設計模式，你在其中建立一個新型別，包裝現有型別。包裝型別與原始型別不同，但可以與其互相轉換。

它通常被實作為一個帶有單一欄位的
[positional struct](./../move-basics/struct.md#positional-structs)。

```move file=packages/samples/sources/programmability/wrapper-type-pattern.move anchor=main

```

## 常見做法 (Common Practices) {#common-practices}

在目標是擴充現有型別行為的情況下，通常會提供包裝型別的存取器（accessor）。這種做法讓使用者在需要時可以直接存取底層型別。例如，在以下程式碼中，我們為 Stack 型別提供了 `inner()`、`inner_mut()` 和 `into_inner()` 方法。

```move file=packages/samples/sources/programmability/wrapper-type-pattern.move anchor=common

```

## 優點 (Advantages) {#advantages}

包裝型別模式提供了幾項好處：

- 自訂函式：它讓你能為現有型別定義自訂函式。
- 穩健的函式簽章：它將函式簽章限制在新型別上，藉此讓程式碼更加穩健。
- 提升可讀性：它通常藉由提供更具描述性的型別名稱來提升程式碼的可讀性。

## 缺點 (Disadvantages) {#disadvantages}

包裝型別模式在兩種情境下特別強大 —— 當你想限制現有型別的行為，同時為相同的資料結構提供自訂介面時，以及當你想擴充現有型別的行為時。然而，它確實有一些限制：

- 冗長：實作起來可能相當冗長，尤其是當你想公開被包裝型別的所有方法時。
- 實作稀疏：實作內容可能相當精簡，因為它通常只是將呼叫轉發給被包裝的型別。

## 下一步 (Next Steps) {#next-steps}

包裝型別模式非常實用，特別是搭配 collection type 一起使用時，如前一節所示。在下一節中，我們將介紹
[Dynamic Fields](./dynamic-fields) —— 一個重要的基本元件，它促成了
[Dynamic Collections](./dynamic-collections)，一種以更靈活（雖然成本更高）的方式儲存大型資料集合的方法。
