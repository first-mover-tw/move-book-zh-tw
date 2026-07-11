---
description:
  在 Sui 中轉移到物件 (Transfer to Object, TTO)：在 Move 中將物件傳送給其他物件，並使用 Receiving
  型別接收它們。
---

# 以物件形式接收 (Receiving as Object) {#receiving-as-object}

[address 擁有](./storage-functions.md#transfer) 的物件狀態支援兩種擁有者型別：一個帳戶，或另一個物件。如果某物件被轉移到另一個物件，Sui 提供了一種方式，可以透過其擁有者的 [`UID`][uid] _接收_（receive）這個物件。

> 這項功能也被稱為 _"Transfer to Object"_，即 TTO。

## 定義 (Definition) {#definition}

接收功能是在 [`sui::transfer`][transfer] 模組中實作的。它包含一個特殊型別 `Receiving`，透過特殊的交易參數來實例化，以及 `receive` 函式，該函式接收父物件的 [`UID`][uid]。

> `transfer::receive` 中的 `T` 受 [Internal Constraint][internal] 約束。公開版本的 `receive` 稱為 `public_receive`，和其他[儲存函式][storage-funs]一樣，它要求 `T` 具有 [`store`][store]。

```move
module sui::transfer;

// 一個圍繞 `Receiving` 參數的暫時性包裝。作為交易區塊中的特殊輸入提供。
// 注意：這個型別必須明確 import 才能使用！
public struct Receiving<phantom T: key> has drop {
    id: ID,
    version: u64,
}

/// 透過特殊型別 `Receiving`，從父物件的 `UID` 接收 `T`。
public fun receive<T: key>(parent: &mut UID, to_receive: Receiving<T>): T;
```

因為 `receive` 需要父物件 `UID` 的可變參考，接收操作只能透過定義該父物件的模組來進行——或是透過該模組選擇公開的存取方式。如果一個物件的模組沒有提供接收的實作，它就無法釋放被送到它身上的物件，因此這項功能應該謹慎使用，並在受控的情境下使用。

## 範例 (Example) {#example}

作為 _轉移_ 與 _接收_ 的示範，來看一個 `PostOffice`（郵局），它會註冊郵箱，並讓任何人都能將物件寄送到這些郵箱：

```move file=packages/samples/sources/storage/transfer-to-object.move anchor=main

```

## 使用情境 (Use Cases) {#use-cases}

轉移到物件是一項強大的功能，它讓物件能夠作為其他物件的擁有者，並且能夠實現純粹的 address 擁有權無法表達的設計：

- **受控的接收。** 因為接收會經過父物件的模組，可以附加額外的邏輯——例如上述的 `PostOffice`，可以對每一件收到的物品收取費用。
- **物件作為容器。** 父物件收集寄送給它的資產，且自身也能被轉移，並隨身攜帶其整個「庫存」——完全不需要在交易中列出內容物。
- **延遲交付。** 資產可以在擁有者尚未準備好領取之前，就先寄送到某個物件——例如一個郵箱，能持續累積物品，直到使用者啟用其帳戶。
- **類帳戶物件。** 一個具有 ID、能夠接收與釋放資產的物件，其行為就非常類似於一個帳戶，這使得 TTO 成為帳戶抽象（account-abstraction）設計的一個建構區塊。

寄送 _到某個物件_ 本質上也是平行的：對某個物件 ID 的轉移就是單純的轉移——它們在交易中不會參考到父物件，因此不會與父物件產生競爭。

## 下一步 (Next Steps) {#next-steps}

本章節結束了「使用物件」這一章：你現在已經能夠定義物件、將它們置於任何擁有權狀態、管理它們的身分，甚至讓物件擁有其他物件。[進階程式設計](./../programmability) 這一章會在此基礎上繼續深入——從執行環境開始，並回頭探討物件組合，介紹父子物件關係背後的第二種機制：[動態欄位](./../programmability/dynamic-fields)。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的 [Transfer to Object](https://docs.sui.io/guides/developer/objects/transfers/transfer-to-object)
- [`sui::transfer`][transfer] 模組文件

[transfer]: https://docs.sui.io/references/framework/sui/transfer
[key]: ./key-ability.md
[store]: ./store-ability.md
[uid]: ./uid-and-id.md
[internal]: ./internal-constraint.md
[storage-funs]: ./storage-functions.md
