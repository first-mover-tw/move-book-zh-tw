---
description: Move 中的 key 能力使結構 (struct) 成為可在 Sui 區塊鏈上儲存、擁有及轉移的物件 (object)。
title: 能力 (Ability)：金鑰 (Key)
keywords:
  - Move
  - Sui
  - Move tutorial
  - ability
  - key
  - abilities
questions:
  - 'What is Ability: Key in Move?'
  - 'How do I use Ability: Key in Move?'
  - What is Object Definition in Move?
  - What is Relation to copy and drop in Move?
answer: The key ability in Move makes a struct an object that can be stored, owned, and transferred on the Sui blockchain.
goal:
  description: Reader understands the key ability in Move makes a struct an object that can be stored, owned, and transferred on the Sui blockchain
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

# 能力：鍵 (Ability: Key) {#ability-key}

在 [Move 基礎][basic-syntax]章節中，我們介紹了四種能力中的兩種：
[Drop][drop-ability] 與 [Copy][copy-ability]。它們會影響值在作用域內的行為，
且與儲存無關。現在該介紹 `key` 能力了——它讓結構成為一個儲存單位。

在過去，建立 `key` 能力是為了將型別標示為*全域儲存中的鍵*。具有 `key`
能力的型別可以儲存在頂層，並可由帳戶或地址*擁有*。隨著
[物件模型][object-model]的導入，`key` 能力成為定義*物件*的能力。

> 在本書中，我們將任何具有 `key` 能力的結構稱為*物件*。

## 物件定義 (Object Definition) {#object-definition}

具有 `key` 能力的結構就是物件，並且可用於
[儲存函式](./storage-functions)。其定義須遵守兩層規則：

- Move 語言要求 `key` 結構的每個欄位都必須具有 [`store`][store-ability]
  能力——我們會在下一頁介紹 `store`；
- Sui 驗證器還要求結構的第一個欄位必須命名為 `id`，且型別必須為 `UID`。

```move file=packages/samples/sources/storage/key-ability.move anchor=user

```

`new` 函式會建立物件。新的 `UID` 只能由 `object::new` 產生；此函式會
接受一個對[交易內容](./../programmability/transaction-context)的可變參考，
因此每個新建立的物件都會取得一個先前從未在網路上存在過的識別碼。我們會在
[UID 與 ID](./uid-and-id)章節中更深入探討 `UID` 型別及其保證。

## 與 `copy` 和 `drop` 的關係 (Relation to `copy` and `drop`) {#relation-to-copy-and-drop}

`UID` 是一種既沒有 [`drop`][drop-ability]，也沒有 [`copy`][copy-ability]
的型別。由於每個物件都必須具有 `UID` 欄位，而結構只能具有其欄位所支援的能力，
這表示物件永遠不可能具有 `drop` 或 `copy`。依其設計，每個物件都不可捨棄且
不可複製——這正是[資產屬性](./../object/digital-assets)所要求的特性。

此特性可用於[能力限制][generics]：要求 `drop` 或 `copy` 會自動排除物件；
反過來說，要求 `key` 會排除具有 `drop` 或 `copy` 的型別。

## 具有 `key` 能力的型別 (Types with the `key` Ability) {#types-with-the-key-ability}

由於 `UID` 的要求，Move 中的任何原生型別都不能具有 `key` 能力，
[標準函式庫][standard-library]中的任何型別也不能。`key` 能力只存在於部分
[Sui 框架][sui-framework]型別與自訂型別中。

## 總結 (Summary) {#summary}

- `key` 能力定義物件。
- Sui 驗證器要求物件的第一個欄位為型別 `UID` 的 `id`。
- Move 語言要求 `key` 結構的所有欄位都具有 [`store`][store-ability]。
- 物件永遠無法具有 [`drop`][drop-ability] 或 [`copy`][copy-ability]。

## 後續步驟 (Next Steps) {#next-steps}

`key` 能力定義物件，並強制所有欄位具有 `store`。在下一節中，我們將介紹
`store` 能力本身，以及它對物件所扮演的第二個、較不明顯的角色。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力](./../../reference/abilities)。

[drop-ability]: ./../move-basics/drop-ability
[copy-ability]: ./../move-basics/copy-ability
[store-ability]: ./store-ability
[generics]: ./../move-basics/generics#constraints-on-type-parameters
[sui-framework]: ./../programmability/sui-framework
[standard-library]: ./../move-basics/standard-library
[object-model]: ./../object
[basic-syntax]: ./../move-basics
