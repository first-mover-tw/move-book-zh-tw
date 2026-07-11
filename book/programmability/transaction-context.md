---
description: 'TxContext in Sui Move: access sender address, transaction digest, epoch, and generate unique IDs in your smart contracts.'
---

# 交易上下文 (Transaction Context)

每個交易都有一個執行上下文。上下文是一組預定義的變數，在程式執行期間可供使用。例如，每個交易都有一個發送者地址，而交易上下文包含一個保存該發送者地址的變數。

交易上下文透過 `TxContext` 結構提供給程式使用。該結構定義在 [`sui::tx_context`][tx-context-framework] 模組中，並包含以下欄位：

[tx-context-framework]: https://docs.sui.io/references/framework/sui/tx_context

```move
module sui::tx_context;

/// 有關目前正在執行的交易資訊。
/// 這不能由交易建構——它是由 VM 建立的特權物件，
/// 並作為 `&mut TxContext` 傳遞給交易的入口點。
public struct TxContext has drop {
    /// 簽署目前交易的使用者地址
    sender: address,
    /// 目前交易的雜湊值
    tx_hash: vector<u8>,
    /// 目前的 epoch 編號
    epoch: u64,
    /// epoch 開始時的時間戳（毫秒）
    epoch_timestamp_ms: u64,
    /// 紀錄執行此交易期間建立的新 ID 數量。
    /// 在交易開始時始終為 0。
    ids_created: u64
}
```

交易上下文不能手動建構或直接修改。它由系統建立，並在交易中作為參考傳遞給函式。任何在 [交易](./../concepts/what-is-a-transaction) 中被呼叫的函式都可以存取上下文，並將其傳遞給巢狀呼叫。

> `TxContext` 必須是函式簽名中的最後一個參數。

## 讀取交易上下文 (Reading the Transaction Context)

除了 `ids_created` 之外，`TxContext` 中的所有欄位都有對應的 getter 函式。這些 getter 定義在 `sui::tx_context` 模組中，可供程式使用。Getter 不需要 `&mut`，因為它們不會修改上下文。

```move file=packages/samples/sources/programmability/transaction-context.move anchor=reading

```

## 可變性 (Mutability)

在系統中建立新物件（或僅僅是 `UID`）需要 `TxContext`。新的 UID 是從交易摘要 (transaction digest) 衍生而來的，為了使摘要唯一，需要一個變化的參數。Sui 使用 `ids_created` 欄位來實現這一點。每當建立一個新的 UID 時，`ids_created` 欄位就會加一。這樣，摘要就始終是唯一的。

在內部，這表示為 `derive_id` 函式：

```move
native fun derive_id(tx_hash: vector<u8>, ids_created: u64): address;
```

## 產生唯一地址 (Generating Unique Addresses)

底層的 `derive_id` 函式也可以在您的程式中用來產生唯一地址。該函式本身並未公開，但 `sui::tx_context` 模組中提供了一個封裝函式 `fresh_object_address`。如果您需要在程式中產生唯一識別碼，這可能會很有用。

```move
module sui::tx_context;

/// 建立一個尚未被使用的 `address`。
/// 由於它是一個物件地址，因此絕不會作為使用者的地址出現。
/// 換句話說，產生的地址是一個全域唯一的物件 ID。
public fun fresh_object_address(ctx: &mut TxContext): address {
    let ids_created = ctx.ids_created;
    let id = derive_id(*&ctx.tx_hash, ids_created);
    ctx.ids_created = ids_created + 1;
    id
}
```
