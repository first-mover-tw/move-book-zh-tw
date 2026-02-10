---
draft: true
---

<!-- 此頁面已廢棄。暫時保存內容，但應重定向至 storage-functions -->

# 受限轉移與公開轉移 (Restricted and Public Transfer)

我們在 [前述章節](./storage-functions) 中介紹的存儲操作預設是受限的 —— 它們只能在定義物件的模組中被呼叫。換句話說，類型對於該模組必須是「內部的 (internal)」才能用於存儲操作。此限制在 Sui 校驗器中實作，並在位元組碼層級強制執行。

然而，為了允許物件在其他模組中被轉移和存儲，這些限制可以被放寬。`sui::transfer` 模組提供了一組 `public_*` 函式，允許在其他模組中呼叫存儲操作。這些函式以 `public_` 為前綴，對所有模組和交易都可用。

## 公開存儲操作

`sui::transfer` 模組提供了以下公開函式。它們與我們之前介紹的函式幾乎完全相同，但可以從任何模組中呼叫。

```move
module sui::transfer;

/// `transfer` 函式的公開版本。
public fun public_transfer<T: key + store>(object: T, to: address) {}

/// `share_object` 函式的公開版本。
public fun public_share_object<T: key + store>(object: T) {}

/// `freeze_object` 函式的公開版本。
public fun public_freeze_object<T: key + store>(object: T) {}
```

為了說明這些函式的用法，考慮以下範例：模組 A 定義了具有 `key` 的 `ObjectK` 以及具有 `key + store` 能力的 `ObjectKS`，而模組 B 嘗試為這些物件實作一個 `transfer` 函式。

> 在此範例中，我們使用 `transfer::transfer`，但對於 `share_object` 和 `freeze_object` 函式，其行為是完全相同的。

```move
/// 分別定義具有 `key` 和 `key + store` 能力的 `ObjectK` 和 `ObjectKS`
module book::transfer_a;

public struct ObjectK has key { id: UID }
public struct ObjectKS has key, store { id: UID }
```

```move
/// 從 `transfer_a` 匯入 `ObjectK` 和 `ObjectKS` 類型，並嘗試為它們實作不同的轉移函式
module book::transfer_b;

// 類型對此模組來說不是內部的
use book::transfer_a::{ObjectK, ObjectKS};

// 失敗！ObjectK 不具備 `store`，且對此模組來說不是內部的
public fun transfer_k(k: ObjectK, to: address) {
    transfer::transfer(k, to);
}

// 失敗！ObjectKS 具備 `store` 但函式並非公開版本
public fun transfer_ks(ks: ObjectKS, to: address) {
    transfer::transfer(ks, to);
}

// 失敗！ObjectK 不具備 `store`，`public_transfer` 要求具備 `store`
public fun public_transfer_k(k: ObjectK, to: address) {
    transfer::public_transfer(k, to);
}

// 成功！ObjectKS 具備 `store` 且使用的是公開函式
public fun public_transfer_ks(ks: ObjectKS, to: address) {
    transfer::public_transfer(ks, to);
}
```

對上述範例的進一步說明：

- ❌ `transfer_k` 失敗，因為 `ObjectK` 對模組 `transfer_b` 來說不是內部的。
- ❌ `transfer_ks` 失敗，因為 `ObjectKS` 對模組 `transfer_b` 來說不是內部的。
- ❌ `public_transfer_k` 失敗，因為 `ObjectK` 不具備 `store` 能力。
- ✅ `public_transfer_ks` 成功，因為 `ObjectKS` 具備 `store` 能力且使用的是公開轉移。

## `store` 的影響

決定是否為某種類型添加 `store` 能力應該非常謹慎。一方面，它是該類型被其他應用程式「使用」的事實上的要求。另一方面，它允許「包裝 (wrapping)」並改變預期的存儲模型。例如，一個角色 (Character) 可能被設定為由帳戶擁有，但若具備 `store` 能力，它就可以被凍結（不能被共享 —— 這種轉換是受限的）。
