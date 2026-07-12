---
title: Sui 物件 (Object) | 參考手冊
description: Sui 物件參考手冊 (Sui Object Reference)：key 能力如何定義物件、UID 需求，以及物件在 Sui 區塊鏈上的儲存方式。
---

# Sui 物件 (Sui Objects)

在 Sui 中，`key` 被用來表示一個 _物件 (object)_。物件是 Sui 中儲存資料的唯一方式——允許資料在交易之間持久化。

欲了解更多詳情，請參閱 Sui 文件：

- [物件模型 (The Object Model)](https://docs.sui.io/concepts/object-model)
- [物件的 Move 規則 (Move Rules for Objects)](https://docs.sui.io/concepts/sui-move-concepts#global-unique)
- [轉移物件 (Transferring Objects)](https://docs.sui.io/concepts/transfers)

## 物件規則 (Object Rules)

物件是一個具備 [`key`](../abilities.md#key) 能力的 [`結構體 (struct)`](../structs.md)。結構體的第一個欄位必須是 `id: sui::object::UID`。這個 32 位元組的欄位（包裝在 [`地址 (address)`](../primitive-types/address.md) 上的強型別封裝）隨後被用於唯一標識該物件。

請注意，由於 `sui::object::UID` 僅具備 `store` 能力（它不具備 `copy` 或 `drop`），因此沒有物件具備 `copy` 或 `drop` 能力。

## 轉移規則 (Transfer Rules) {#transfer-rules}

物件可以在 `sui::transfer` 模組中更改其所有權並進行轉移。該模組中的許多函式都有「公共 (public)」和「私有 (private)」變體，其中「私有」變體只能在定義該物件型別的模組內部呼叫。「公共」變體僅在物件具備 `store` 能力時才能被呼叫。

例如，如果我們在模組 `my_module` 中定義了兩個物件 `A` 和 `B`：

```move
module a::my_module;

public struct A has key {
    id: sui::object::UID,
}

public struct B has key, store {
    id: sui::object::UID,
}
```

`A` 只能在 `a::my_module` 內部使用 `sui::transfer::transfer` 進行轉移，而 `B` 則可以使用 `sui::transfer::public_transfer` 在任何地方進行轉移。這些規則由 Sui 中的自訂型別系統（位元組碼驗證器 bytecode verifier）規則強制執行。
