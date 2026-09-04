---
description: Sui Move 中的交易內容 (TxContext)：在智慧合約中存取傳送者地址、交易摘要、時期、gas 價格，並產生唯一 ID。
title: 交易情境 (Transaction Context)
keywords:
  - Move
  - Sui
  - Move tutorial
  - transaction
  - context
questions:
  - What is Transaction Context in Move?
  - How do I use Transaction Context in Move?
  - What is Reading the Transaction Context in Move?
  - What is Mutability in Move?
answer: 'TxContext in Sui Move: access sender address, transaction digest, epoch, gas price, and generate unique IDs in your smart contracts.'
goal:
  description: 'Reader understands txContext in Sui Move: access sender address, transaction digest, epoch, gas price, and generate unique IDs in your smart contracts'
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

# 交易情境 (Transaction Context) {#transaction-context}

每筆交易都會在一個 _交易情境_ 中執行。此情境是一組在執行期間可供程式使用的預先定義值，例如傳送者地址、目前的 epoch，或交易摘要。

程式可透過 `TxContext` 結構存取交易情境。此結構定義於 [`sui::tx_context`][tx-context-framework] 模組中，並包含下列欄位：

[tx-context-framework]: https://docs.sui.io/references/framework/sui/tx_context

```move
module sui::tx_context;

/// 目前正在執行之交易的資訊。
/// 此結構無法由交易建立——它是由
/// VM 建立的特權物件，並以 `&mut TxContext` 傳入交易的入口函式。
public struct TxContext has drop {
    /// 簽署目前交易之使用者的地址
    sender: address,
    /// 目前交易的雜湊值
    tx_hash: vector<u8>,
    /// 目前的 epoch 編號
    epoch: u64,
    /// epoch 開始時的時間戳記
    epoch_timestamp_ms: u64,
    /// 記錄執行期間新建立 ID 數量的計數器
    /// 在交易開始時一律為 0
    ids_created: u64
}
```

> 雖然此結構仍宣告其原始欄位，目前版本的 framework 已不再直接讀取其中大部分欄位——getter 函式會轉送至 Sui 執行環境中實作的原生函式。這些欄位是為了相容性而保留，並且最好將 `TxContext` 視為執行環境的不透明控制代碼。

交易情境無法手動建立或直接修改。它由系統建立，並在交易中以參考形式傳入函式。在 [交易](./../concepts/what-is-a-transaction)中呼叫的任何函式都可存取此情境，並可將其傳入巢狀呼叫。

> `TxContext` 必須是函式簽章中的最後一個引數。

## 讀取交易情境 (Reading the Transaction Context) {#reading-the-transaction-context}

`sui::tx_context` 模組為情境中可用的每個值提供 getter 函式。所有 getter 都不需要可變參考，因為讀取情境不會修改它：

- `sender()` - 簽署交易的地址；
- `digest()` - 目前交易的 32 位元組摘要（雜湊）的參考，每筆交易皆不相同；
- `epoch()` - 目前的 [epoch](./epoch-and-time) 編號；
- `epoch_timestamp_ms()` - epoch 開始當下的時間戳記，以毫秒為單位；
- `sponsor()` - 交易贊助者的地址；若交易未受贊助則為 `None`；
- `gas_price()` - 與目前交易一併提交的 gas 價格；
- `reference_gas_price()` - 目前 epoch 的參考 gas 價格。

```move file=packages/samples/sources/programmability/transaction-context.move anchor=reading

```

> 交易摘要是交易輸入內容的雜湊值；雖然每筆交易皆不相同，但絕不可將其作為隨機性的來源——它在交易執行前就已知，且可由傳送者操控。

`sponsor()` getter 與 _受贊助交易_ 有關——此類交易由第三方贊助者代表使用者支付 gas。在受贊助交易中，`sender()` 仍會回傳使用者地址，因此無論交易是否受贊助，以傳送者為基礎的邏輯都具有相同行為。

這些 getter 是讀取情境的完整公開介面。其他值，例如交易的 gas 預算，刻意不向程式公開。

## 可變性 (Mutability) {#mutability}

有些操作要求以可變參考 `&mut TxContext` 傳入情境。其中最重要的是建立新物件：Sui 上的每個物件都必須有全域唯一的 `UID`。新的 UID 是從交易摘要及目前此交易中已建立 ID 的計數器——`ids_created` 欄位——推導而來。每次要求新的 UID 時，計數器都會遞增，確保每個推導出的地址皆為唯一。由於計數器必須變更，此操作需要情境的可變參考。

我們會在 [UID 與 ID](./../storage/uid-and-id)章節中詳細說明物件建立。

## 產生唯一地址 (Generating Unique Addresses) {#generating-unique-addresses}

相同的推導機制可直接用於你的程式，以產生唯一地址。`sui::tx_context` 模組為此公開 `fresh_object_address` 函式；若應用程式需要唯一識別碼，例如作為[動態欄位](./dynamic-fields)或鏈下索引中的鍵，這個函式可能很有用。

```move
module sui::tx_context;

/// 建立尚未使用過的 `address`。由於它是物件地址，
/// 因此絕不會作為使用者的地址出現。
/// 換句話說，產生的地址是全域唯一的物件 ID。
public fun fresh_object_address(ctx: &mut TxContext): address;
```

## 測試中的交易情境 (Transaction Context in Tests) {#transaction-context-in-tests}

由於 `TxContext` 無法在一般程式碼中建立，[測試](./../move-basics/testing)將無法呼叫任何預期接收它的函式。針對此情境，framework 提供僅限測試使用的建構函式：最簡單的是 `tx_context::dummy()`，它會回傳具有預留位置值的情境。你會在本書各處的程式碼範例中看到它：

```move
#[test]
fun test_some_action() {
    let ctx = &mut tx_context::dummy();
    // 將 `ctx` 傳入預期接收 `&mut TxContext` 的函式
}
```

對於需要特定值（例如特定傳送者、epoch 或 gas 價格）的測試，此模組提供更多僅限測試使用的建構函式，以及用於模擬 epoch 變更的輔助函式。這些內容會在[模擬交易情境](./../testing/transaction-context)章節中說明。對於多筆交易情境及存取儲存空間中的物件，請使用 `sui::test_scenario` 模組，該模組在[測試情境](./../testing/test-scenario)章節中說明。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::tx_context][tx-context-framework] 模組文件。
- [暫存區](./scratchpad) - 可透過 `TxContext` 存取的每筆交易鍵值儲存區。
