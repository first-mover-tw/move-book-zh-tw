---
description: TxContext（交易上下文）in Sui Move：在你的智慧合約中存取傳送者地址 (sender address)、交易摘要 (transaction digest)、epoch、燃料價格 (gas price)，並產生唯一 ID (unique IDs)。
---

# 交易上下文 (Transaction Context) {#transaction-context}

每筆交易都在一個 _transaction context_ 中執行。此 context 是一組預先定義好的值,在程式執行期間可供使用,例如寄件者地址、當前 epoch,或交易摘要 (digest)。

交易 context 透過 `TxContext` struct 提供給程式。此 struct 定義於 [`sui::tx_context`][tx-context-framework] 模組中,包含以下欄位:

[tx-context-framework]: https://docs.sui.io/references/framework/sui/tx_context

```move
module sui::tx_context;

/// 目前正在執行的交易的相關資訊。
/// 這無法由交易自行建構——它是一個特殊權限物件，由
/// VM 建立並以 `&mut TxContext` 的形式傳入交易的進入點。
public struct TxContext has drop {
    /// 簽署目前交易的使用者地址
    sender: address,
    /// 目前交易的雜湊值
    tx_hash: vector<u8>,
    /// 目前的 epoch 編號
    epoch: u64,
    /// 該 epoch 開始的時間戳記
    epoch_timestamp_ms: u64,
    /// 記錄此交易執行期間所建立的新 id 數量的計數器
    /// 交易開始時一律為 0
    ids_created: u64
}
```

> 雖然此 struct 仍然宣告了原本的欄位,但目前版本的 framework 已不再直接讀取大部分欄位——getter 函式會轉發呼叫到 Sui 執行環境中實作的 native 函式。這些欄位是為了相容性而保留,`TxContext` 最好被理解為對執行環境的一個不透明控制代碼 (opaque handle)。

交易 context 無法手動建構或直接修改。它由系統建立,並以參考形式傳入交易中的函式。在 [Transaction](./../concepts/what-is-a-transaction) 中被呼叫的任何函式都能存取此 context,並可將其傳入巢狀呼叫中。

> `TxContext` 必須是函式簽章中的最後一個參數。

## 讀取交易上下文 (Reading the Transaction Context) {#reading-the-transaction-context}

`sui::tx_context` 模組為 context 中每個可用的值提供了一個 getter。所有 getter 都不需要可變參考,因為讀取 context 不會修改它:

- `sender()` - 簽署此交易的地址;
- `digest()` - 對當前交易 32 位元組摘要 (hash) 的參考,每筆交易皆唯一;
- `epoch()` - 當前 [epoch](./epoch-and-time) 編號;
- `epoch_timestamp_ms()` - epoch 開始時刻的時間戳記,單位為毫秒;
- `sponsor()` - 交易贊助者的地址,若交易並非由他人贊助則為 `None`;
- `gas_price()` - 隨當前交易一併提交的 gas 價格;
- `reference_gas_price()` - 當前 epoch 的參考 gas 價格。

```move file=packages/samples/sources/programmability/transaction-context.move anchor=reading

```

> 交易摘要是交易輸入的雜湊值,雖然每筆交易皆唯一,但絕不應被用作隨機性的來源——它在交易執行前就已知,且可被寄件者操縱。

`sponsor()` getter 與 _sponsored transactions_(贊助交易)有關——這類交易由第三方(即贊助者)代替使用者支付 gas 費用。在贊助交易中,`sender()` 仍會回傳使用者的地址,因此無論交易是否被贊助,基於 sender 的邏輯行為都相同。

這些 getter 是讀取 context 的完整公開介面。其他的值,例如交易的 gas 預算,則刻意未對程式公開。

## 可變性 (Mutability) {#mutability}

某些操作需要以可變參考傳入 context——`&mut TxContext`。其中最重要的是建立新物件:Sui 上的每個物件都必須有一個全域唯一的 `UID`。新產生的 UID 是由交易摘要以及此交易中目前已建立的 ID 計數器(即 `ids_created` 欄位)推導而來。每次請求新的 UID 時,計數器都會遞增,以確保每個推導出的地址都是唯一的。由於計數器必須改變,此操作需要 context 的可變參考。

我們會在 [UID and ID](./../storage/uid-and-id) 章節詳細說明物件的建立。

## 產生唯一地址 (Generating Unique Addresses) {#generating-unique-addresses}

同樣的推導機制也可以直接在你的程式中用來產生唯一地址。`sui::tx_context` 模組為此公開了 `fresh_object_address` 函式,若應用程式需要一個唯一識別碼——例如作為 [dynamic field](./dynamic-fields) 的 key 或鏈下索引使用——此函式會很有用。

```move
module sui::tx_context;

/// 建立一個尚未被使用過的 `address`。由於它是物件地址，所以
/// 永遠不會作為使用者的地址出現。
/// 換句話說，產生的地址是一個全域唯一的物件 ID。
public fun fresh_object_address(ctx: &mut TxContext): address;
```

## 測試中的交易上下文 (Transaction Context in Tests) {#transaction-context-in-tests}

由於 `TxContext` 無法在一般程式碼中建構,[測試](./../move-basics/testing) 將無法呼叫任何需要它的函式。針對這種情況,framework 提供了僅用於測試的建構函式:其中最簡單的是 `tx_context::dummy()`,它會回傳一個具有預留位置值 (placeholder values) 的 context。你會在本書各處的程式碼範例中看到它:

```move
#[test]
fun test_some_action() {
    let ctx = &mut tx_context::dummy();
    // 將 `ctx` 傳入需要 `&mut TxContext` 的函式中
}
```

對於需要特定值(特定 sender、epoch 或 gas price)的測試,該模組還提供了更多僅用於測試的建構函式,以及用來模擬 epoch 變化的輔助函式。這些內容涵蓋於 [Simulating Transaction Context](./../testing/transaction-context) 章節。對於多筆交易情境以及對儲存中物件的存取,請使用 `sui::test_scenario` 模組,詳見 [Test Scenario](./../testing/test-scenario) 章節。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::tx_context][tx-context-framework] 模組文件。
