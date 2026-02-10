# 能力：Key (Ability: Key)

在 [基礎語法][basic-syntax] 章節中，我們已經介紹了四種能力中的兩種：[Drop][drop-ability] 和 [Copy][copy-ability]。它們影響數值在作用域中的行為，與存儲沒有直接關係。現在是時候介紹 `key` 能力了，它允許結構 (struct) 被「存儲」。

歷史上，`key` 能力是為了將一種類型標記為一個「存儲中的鍵 (key in storage)」。具有 `key` 能力的類型可以存儲在全域存儲的頂層，並且可以由帳戶或地址「擁有」。隨著 [物件模型][object-model] 的引入，`key` 能力成為了「物件 (Objects)」的定義性能力。

> 在本書隨後的內容中，我們將把任何具有 `key` 能力的結構稱為一個「物件」。

## 物件定義

具有 `key` 能力的結構被視為「一個物件」，並可以用於存儲函式。Sui 校驗器要求結構的第一個欄位必須命名為 `id` 且類型為 `UID`。此外，它要求所有欄位都必須具有 `store` 能力 —— 我們將在 [下一頁][store-ability] 詳細探討。

```move
/// `User` 物件定義。
public struct User has key {
    id: UID, // Sui 位元組碼校驗器要求
    name: String, // 欄位類型必須具有 `store`
}

/// 建立一個新的 `User` 類型實體。
/// 使用特殊的結構 `TxContext` 來衍生唯一 ID (UID)。
public fun new(name: String, ctx: &mut TxContext): User {
    User {
        id: object::new(ctx), // 建立一個新的 UID
        name,
    }
}
```

## 與 `copy` 和 `drop` 的關係

`UID` 是一種不具有 [`drop`][drop-ability] 或 [`copy`][copy-ability] 能力的類型。由於它是任何具有 `key` 能力類型的必需欄位，這意味著具有 `key` 的類型永遠不能具有 `drop` 或 `copy`。

此屬性可用於 [能力限制 (ability constraints)][generics]：要求 `drop` 或 `copy` 會自動排除 `key`；反之，要求 `key` 則會排除具有 `drop` 或 `copy` 的類型。

## 具有 `key` 能力的類型

由於對具有 `key` 的類型有 `UID` 要求，Move 中的任何原生類型都不能具有 `key` 能力，[標準函式庫][standard-library] 中的任何類型也不能。`key` 能力僅存在於某些 [Sui 框架][sui-framework] 類型以及自定義類型中。

## 總結

- `key` 能力定義了一個物件
- 物件的第一個欄位必須是 `id`，類型為 `UID`
- `key` 類型的欄位必須具有 [`store`][store-ability] 能力
- 物件不能具有 [`drop`][drop-ability] 或 [`copy`][copy-ability] 能力

## 下一步

`key` 能力在 Move 中定義了物件，並強制欄位具有 `store`。在下一節中，我們將介紹 `store` 能力，以便稍後解釋 [存儲操作 (storage operations)](./storage-functions.md) 是如何運作的。

## 延伸閱讀

- Move 參考手冊中的 [類型能力 (Type Abilities)](./../../reference/abilities)。

[drop-ability]: ./../move-basics/drop-ability
[copy-ability]: ./../move-basics/copy-ability
[store-ability]: ./store-ability.md
[generics]: ./../move-basics/generics#constraints-on-type-parameters
[sui-framework]: ./../programmability/sui-framework
[standard-library]: ./../move-basics/standard-library
[object-model]: ./../object
[basic-syntax]: ./../move-basics
