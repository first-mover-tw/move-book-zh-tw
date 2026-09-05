---
title: Sui 物件 (Object) | 參考手冊
description: Sui 物件參考 (Sui Object reference)：key 能力 (key ability) 如何定義物件、UID 要求，以及 Sui 區塊鏈上的物件儲存
keywords:
  - Move
  - Sui
  - Move reference
  - sui
  - object
  - reference
  - object model
questions:
  - How does Sui Object work in Move?
  - What is the syntax for Sui Object in Move?
  - What is Object Rules in Move?
  - What is Transfer Rules in Move?
answer: 'Sui Object reference: how the key ability defines objects, UID requirements, and object storage on the Sui blockchain.'
goal:
  description: 'Reader understands sui Object reference: how the key ability defines objects, UID requirements, and object storage on the Sui blockchain'
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

# Sui 物件 (Sui Objects) {#sui-objects}

在 Sui 中，`key` 用於表示一個*物件*。物件是在 Sui 中儲存資料的唯一方式，讓資料能在交易之間持續存在。

如需更多詳細資料，請參閱 Sui 文件中的：

- [物件模型](https://docs.sui.io/guides/developer/objects)
- [物件的 Move 規則](https://docs.sui.io/concepts/sui-move-concepts#global-unique)
- [轉移物件](https://docs.sui.io/guides/developer/objects/transfers)

## 物件規則 (Object Rules) {#object-rules}

物件是具有 [`key`](../abilities.md#key) 能力的 [`struct`](../structs.md)。結構的第一個欄位必須是 `id: sui::object::UID`。此 32 位元組欄位（[`address`](../primitive-types/address.md) 的強型別包裝）會用於唯一識別該物件。

請注意，由於 `sui::object::UID` 僅具有 `store` 能力（不具有 `copy` 或 `drop`），因此沒有任何物件具有 `copy` 或 `drop`。

## 轉移規則 (Transfer Rules) {#transfer-rules}

物件可以在 `sui::transfer` 模組中變更其擁有權並進行轉移。模組中的許多函式都有「公開」與「私有」變體，其中「私有」變體只能在定義物件型別的模組內呼叫。「公開」變體則只有在物件具有 `store` 時才能呼叫。

例如，假設我們在模組 `my_module` 中定義了兩個物件 `A` 與 `B`：

```move
module a::my_module;

public struct A has key {
    id: sui::object::UID,
}

public struct B has key, store {
    id: sui::object::UID,
}
```

`A` 只能在 `a::my_module` 內使用 `sui::transfer::transfer` 進行轉移，而 `B` 可在任何位置使用 `sui::transfer::public_transfer` 進行轉移。這些規則由 Sui 中的自訂型別系統（位元碼驗證器）規則強制執行。
