---
description: 'The drop ability in Move allows struct instances to be discarded. Learn how it works and when to use it in Sui smart contracts.'
---

# 能力：丟棄 (Abilities: Drop)

`drop` 能力 — 最簡單的一種 — 允許結構實例被 **忽略** 或 **丟棄**。在許多程式語言中，這種行為被認為是預設的。然而，在 Move 中，不允許忽略沒有 `drop` 能力的結構。這是 Move 語言的一項安全功能，確保所有資產都得到正確處理。嘗試忽略沒有 `drop` 能力的結構將導致編譯錯誤。

```move file=packages/samples/sources/move-basics/drop-ability.move anchor=main

```

`drop` 能力常用於自定義集合類型，以消除在不再需要集合時對其進行特殊處理的需求。例如，`vector` 類型具有 `drop` 能力，這允許在不再需要時忽略向量。然而，Move 類型系統最大的特色在於可以 **不具備** `drop`。這確保了資產被正確處理，而不是被忽略。

僅具有 `drop` 能力的結構被稱為 **見證者 (Witness)**。我們在 [見證者與抽象實作](./../programmability/witness-pattern) 章節中解釋了 **見證者 (Witness)** 的概念。

## 具有 `drop` 能力的類型

Move 中的所有原生類型都具有 `drop` 能力。這包括：

- [`bool`](./../move-basics/primitive-types#booleans)
- [無號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 具有 `drop` 時的 [`vector<T>`](./../move-basics/vector)
- [`address`](./../move-basics/address)

標準庫中定義的所有類型同樣也具有 `drop` 能力。這包括：

- 當 `T` 具有 `drop` 時的 [`Option<T>`](./../move-basics/option)
- [`String`](./../move-basics/string)
- [`TypeName`](./../move-basics/type-reflection)

## 延伸閱讀

- Move 參考手冊中的 [類型能力](./../../reference/abilities)。
