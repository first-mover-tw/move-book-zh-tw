---
description: key 能力 (key ability) 讓結構體 (struct) 成為可在 Sui 區塊鏈上儲存、擁有和轉移的物件 (object)。
---

# 能力：key (Ability: Key) {#ability-key}

在 [Move 基礎][basic-syntax] 章節中，我們介紹了四種能力中的兩種——[Drop][drop-ability] 與 [Copy][copy-ability]。它們影響一個值在作用域內的行為，與儲存無關。現在該來談談 `key` 能力了——這是讓一個結構體能夠成為儲存單位的能力。

從歷史上看，`key` 能力最初是用來標記一個型別為_全域儲存中的鍵值_。擁有 `key` 能力的型別可以被儲存在頂層，並可以被某個帳戶或地址_擁有_。隨著 [物件模型][object-model] 的引入，`key` 能力成為定義_物件_的關鍵能力。

> 在本書中，我們將任何擁有 `key` 能力的結構體稱為_物件_。

## 物件定義 (Object Definition) {#object-definition}

擁有 `key` 能力的結構體即為物件，可用於[儲存函式](./storage-functions)。其定義受兩層規則約束：

- Move 語言要求 `key` 結構體的每個欄位都必須具備 [`store`][store-ability] 能力——我們會在下一頁探討 `store`；
- Sui 驗證器另外要求該結構體的第一個欄位必須命名為 `id`，且型別為 `UID`。

```move file=packages/samples/sources/storage/key-ability.move anchor=user

```

`new` 函式會建立該物件。全新的 `UID` 只能由 `object::new` 產生，此函式需要傳入 [交易上下文](./../programmability/transaction-context) 的可變參考——因此每個新建立的物件都會取得一個網路上前所未有的識別碼。我們會在 [UID 與 ID](./uid-and-id) 小節中更深入探討 `UID` 型別及其保證。

## 與 `copy` 及 `drop` 的關係 (Relation to `copy` and `drop`) {#relation-to-copy-and-drop}

`UID` 是一個既沒有 [`drop`][drop-ability] 也沒有 [`copy`][copy-ability] 的型別。由於每個物件都必須具備 `UID` 欄位，而結構體只能擁有其欄位所支援的能力，這意味著物件永遠不能擁有 `drop` 或 `copy`。每個物件在結構上都是不可捨棄且不可複製的——這正是[數位資產屬性](./../object/digital-assets)所要求的。

這項特性可以在[能力約束][generics]中被善加利用：要求 `drop` 或 `copy` 會自動排除物件，反過來說，要求 `key` 則會排除擁有 `drop` 或 `copy` 的型別。

## 擁有 key 能力的型別 (Types with the `key` Ability) {#types-with-the-key-ability}

由於 `UID` 的要求，Move 中沒有任何原生型別能擁有 `key` 能力，[標準函式庫][standard-library]中的型別也不例外。`key` 能力只存在於部分 [Sui 框架][sui-framework]型別以及自訂型別之中。

## 總結 (Summary) {#summary}

- `key` 能力定義了一個物件。
- Sui 驗證器要求物件的第一個欄位必須是型別為 `UID` 的 `id`。
- Move 語言要求 `key` 結構體的所有欄位都必須具備 [`store`][store-ability]。
- 物件永遠不能擁有 [`drop`][drop-ability] 或 [`copy`][copy-ability]。

## 下一步 (Next Steps) {#next-steps}

`key` 能力定義了物件，並強制所有欄位都必須具備 `store`。在下一節中，我們將探討 `store` 能力本身——以及它對物件而言所扮演的第二種、較不明顯的角色。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[型別能力](./../../reference/abilities)。

[drop-ability]: ./../move-basics/drop-ability
[copy-ability]: ./../move-basics/copy-ability
[store-ability]: ./store-ability
[generics]: ./../move-basics/generics#constraints-on-type-parameters
[sui-framework]: ./../programmability/sui-framework
[standard-library]: ./../move-basics/standard-library
[object-model]: ./../object
[basic-syntax]: ./../move-basics
