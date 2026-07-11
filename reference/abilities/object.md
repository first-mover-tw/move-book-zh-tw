---
title: Sui 物件 (Object) | 參考手冊
description: Sui 物件參考手冊 (Sui Object Reference)：key 能力如何定義物件、UID 需求，以及物件在 Sui 區塊鏈上的儲存方式。
---

# Sui 物件 (Sui Objects)

對於 Sui 而言，`key` 被用來表示一個「物件 (Object)」。物件是 Sui 中存儲資料的唯一方式 —— 允許資料在交易之間持久化。

欲瞭解更多細節，請參閱 Sui 的文件：

- [物件模型 (The Object Model)](https://docs.sui.io/concepts/object-model)
- [物件的 Move 規則 (Move Rules for Objects)](https://docs.sui.io/concepts/sui-move-concepts#global-unique)
- [物件傳輸 (Transferring Objects)](https://docs.sui.io/concepts/transfers)

## 物件規則 (Object Rules)

物件是具備 [`key`](../abilities.md#key) 能力的 [`struct`](../structs.md)。結構體的第一個欄位必須是 `id: sui::object::UID`。這個 32 位元組的欄位（包裝在 [`address`](../primitive-types/address.md) 上的強類型封裝器）用於唯一識別該物件。

請注意，由於 `sui::object::UID` 僅具備 `store` 能力（它不具備 `copy` 或 `drop`），因此沒有物件具備 `copy` 或 `drop` 能力。

## 傳輸規則 (Transfer Rules) {#transfer-rules}

物件的所有權可以在 `sui::transfer` 模組中更改和傳輸。該模組中的許多函式都有「公開 (public)」和「私有 (private)」變體，其中「私有」變體只能在定義物件類型的模組內部呼叫。只有當物件具備 `store` 能力時，才能呼叫「公開」變體。

例如，如果有兩個物件 `A` 和 `B` 定義在模組 `my_module` 中：

```move
module a::my_module;

public struct A has key {
    id: sui::object::UID,
}

public struct B has key, store {
    id: sui::object::UID,
}
```

`A` 只能在 `a::my_module` 內部使用 `sui::transfer::transfer` 進行傳輸，而 `B` 則可以在任何地方使用 `sui::transfer::public_transfer` 進行傳輸。這些規則由 Sui 中的自定義類型系統（位元組碼驗證器）規則強制執行。
