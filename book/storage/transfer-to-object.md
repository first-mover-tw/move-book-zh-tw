# 接收物件 (Receiving as Object)

[地址擁有的](./storage-functions.md#transfer) 物件狀態支援兩種類型的擁有者：帳戶和另一個物件。如果一個物件被轉移到另一個物件，Sui 提供了一種透過其擁有者的 [`UID`][uid] 來「接收 (receive)」此物件的方法。

> 此功能也被稱為「轉移至物件 (Transfer to Object)」或 TTO。

## 定義

接收功能在 [`sui::transfer`][transfer] 模組中實作。它包含一個特殊的類型 `Receiving`（透過特殊的交易參數實例化），以及接收函式 `receive`（接收父物件的 [`UID`][uid]）。

> 目前，`transfer::receive` 中的 `T` 受限於 [內部約束 (Internal Constraint)][internal]。`receive` 的公開版本稱為 `public_receive`，與其他 [存儲函式 (storage functions)][storage-funs] 一樣，它要求 `T` 具有 [`store`][store]。

```move
module sui::transfer;

// 基於 `Receiving` 參數的臨時封裝器。在交易區塊中作為特殊輸入提供。
// 注意：此類型必須明確匯入才能使用！
public struct Receiving<phantom T: key> has drop {
    id: ID,
    version: u64,
}

/// 從父物件 `UID` 透過特殊類型 `Receiving` 接收 `T`。
public fun receive<T: key>(parent: &mut UID, to_receive: Receiving<T>): T;
```

由於對 `UID` 類型的要求，接收操作無法在不提供存取權限或特殊接收實作的任意物件上執行。此功能應謹慎使用，並在受控環境下進行。

## 範例

作為「轉移」與「接收」的說明，考慮一個範例：`PostOffice` 允許註冊郵政信箱 (Post Box) 並向帳戶的郵政信箱發送物件。

```move file=packages/samples/sources/storage/transfer-to-object.move anchor=main

```

## 使用場景

轉移至物件是一項強大的功能，它允許物件充當其他物件的擁有者。使用它的原因之一是可以在接收時執行額外的授權，例如上述範例中的 `PostOffice` 可以收取接收費用。

- 允許並行執行對多個物件的轉移，而無需在交易中引用它們；
- 父物件也可以被轉移，充當容器；
- 分類似於郵政信箱的應用程式，使用者只有在啟動帳戶後才能獲得資產；
- 帳戶抽象 (Account Abstraction) 類的應用程式，其中一個物件在模擬一個帳戶。

## 相關連結

- Sui 文件中的 [轉移至物件 (Transfer to Object)](https://docs.sui.io/concepts/transfers/transfer-to-object)
- [`sui::transfer`][transfer] 模組文件

[transfer]: https://docs.sui.io/references/framework/sui_sui/transfer
[key]: ./key-ability.md
[store]: ./store-ability.md
[uid]: ./uid-and-id.md
[internal]: ./internal-constraint.md
