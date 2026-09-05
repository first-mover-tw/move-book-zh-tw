---
description: Sui 中的物件轉移 (Transfer to Object, TTO)：將物件傳送至其他物件，並使用 Move 中的接收型別 (Receiving type) 來接收它們。
title: 以物件 (Object) 接收
keywords:
  - Move
  - Sui
  - Move tutorial
  - receiving
  - object
  - object model
questions:
  - What is Receiving as Object in Move?
  - How do I use Receiving as Object in Move?
  - What is Definition in Move?
  - What is Use Cases in Move?
answer: 'Transfer to Object (TTO) in Sui: send objects to other objects and receive them using the Receiving type in Move.'
goal:
  description: 'Reader understands transfer to Object (TTO) in Sui: send objects to other objects and receive them using the Receiving type in Move'
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

# 以物件身分接收 (Receiving as Object) {#receiving-as-object}

[地址擁有](./storage-functions.md#transfer)的物件狀態支援兩種擁有者：帳戶與另一個物件。若物件已轉移給另一個物件，Sui 提供透過其擁有者的 [`UID`][uid] 來*接收*此物件的方法。

> 此功能也稱為 _「轉移至物件」_（"Transfer to Object"）或 TTO。

## 定義 (Definition) {#definition}

接收功能實作於 [`sui::transfer`][transfer] 模組中。它由特殊型別 `Receiving` 組成，此型別會透過特殊交易引數具現化；另有 `receive` 函式，該函式接受父物件的 [`UID`][uid]。

> `transfer::receive` 中的 `T` 受限於[內部約束][internal]。`receive` 的公開版本稱為 `public_receive`；和其他[儲存函式][storage-funs]一樣，它要求 `T` 具有 [`store`][store]。

```move
module sui::transfer;

// `Receiving` 引數的暫時性包裝器。作為特殊輸入提供
// 於交易區塊中。
// 注意：必須明確匯入此型別才能使用！
public struct Receiving<phantom T: key> has drop {
    id: ID,
    version: u64,
}

/// 透過特殊型別 `Receiving`，從父層 `UID` 接收 `T`。
public fun receive<T: key>(parent: &mut UID, to_receive: Receiving<T>): T;
```

由於 `receive` 需要父物件 `UID` 的可變參考，因此只能透過定義父物件的模組，或該模組選擇公開的存取方式來接收。模組未提供接收實作的物件無法釋放轉移給它的物件，因此應謹慎並在受控環境中使用此功能。

## 範例 (Example) {#example}

為說明*轉移*與*接收*，請考慮一個 `PostOffice`，它會註冊郵箱，並讓任何人都能將物件傳送給這些郵箱：

```move file=packages/samples/sources/storage/transfer-to-object.move anchor=main

```

## 使用案例 (Use Cases) {#use-cases}

轉移至物件是一項強大的功能，可讓物件成為其他物件的擁有者，並支援單純地址擁有權無法表達的設計：

- **受控接收。** 由於接收會經過父物件的模組，因此可以附加額外邏輯；例如，上述 `PostOffice` 可對每個接收的項目收取費用。
- **作為容器的物件。** 父物件會收集傳送給它的資產，且其本身可被轉移，並攜帶整個「庫存」——無須在交易中列出內容。
- **延後交付。** 資產可在擁有者準備好領取前先傳送給物件，例如郵箱會累積項目，直到使用者啟用其帳戶。
- **類帳戶物件。** 具有可接收及釋放資產之 ID 的物件，其行為很像帳戶，使 TTO 成為帳戶抽象化設計的建構基礎。

*轉移至物件*也自然地支援平行處理：轉移至物件 ID 屬於一般轉移——它們不會在交易中參考父物件，因此不會與其產生競爭。

## 後續步驟 (Next Steps) {#next-steps}

本節結束「使用物件」章節：你現在可以定義物件、將其置於任何擁有權狀態、管理其身分，甚至讓物件擁有其他物件。[進階可程式化](./../programmability)章節會建立於這些概念之上——從執行環境開始，並透過[動態欄位](./../programmability/dynamic-fields)回到物件組合；動態欄位是父子物件關係背後的第二種機制。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的[轉移至物件](https://docs.sui.io/guides/developer/objects/transfers/transfer-to-object)
- [`sui::transfer`][transfer] 模組文件

[transfer]: https://docs.sui.io/references/framework/sui/transfer
[key]: ./key-ability.md
[store]: ./store-ability.md
[uid]: ./uid-and-id.md
[internal]: ./internal-constraint.md
[storage-funs]: ./storage-functions.md
