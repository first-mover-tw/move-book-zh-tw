---
description: 在 Move (Move) 測試中模擬交易情境 (TxContext)：建立虛擬情境 (dummy contexts)、設定傳送者地址 (sender addresses)，並產生新的唯一識別碼 (fresh UIDs) 以進行單元測試 (unit testing)。
title: 模擬交易情境 (Simulating Transaction Context)
keywords:
  - Move
  - Sui
  - Move tutorial
  - simulating
  - transaction
  - context
questions:
  - What is Simulating Transaction Context in Move?
  - How do I use Simulating Transaction Context in Move?
  - What is Creating a Dummy Context in Move?
  - What is Custom Context with new in Move?
answer: 'Simulate TxContext in Move tests: create dummy contexts, set sender addresses, and generate fresh UIDs for unit testing.'
goal:
  description: 'Reader understands simulate TxContext in Move tests: create dummy contexts, set sender addresses, and generate fresh UIDs for unit testing'
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

# 模擬交易情境 (Simulating Transaction Context) {#simulating-transaction-context}

大多數會建立物件或與使用者互動的 Move 函式都具有 `TxContext` 引數。執行交易時，其值由執行階段提供；但在測試中，你需要自行建立並傳入它。`sui::tx_context` 模組為此用途提供了數個實用函式。

> **注意：** 本章的實用工具僅適用於簡單的單元測試。它們不提供從儲存空間存取共享或已轉移物件的能力。若測試需要從儲存空間取得物件，或模擬多筆交易的情境，請使用 [測試情境](./test-scenario.md)。

## 建立虛擬情境 (Creating a Dummy Context) {#creating-a-dummy-context}

取得 `TxContext` 最簡單的方法是 `tx_context::dummy()`。它會建立具有預設值的情境：零地址傳送者、epoch 0，以及固定的交易雜湊：

```move
use std::unit_test::assert_eq;

#[test]
fun test_create_object() {
    let ctx = &mut tx_context::dummy();
    let obj = my_module::new(ctx);

    assert_eq!(ctx.sender(), @0); // 傳送者預設為 0x0
    // ...
}
```

這足以應付大多數不在意特定情境值，且需要測試建立物件而非與儲存空間互動的測試。

## 使用 `new` 自訂情境 (Custom Context with `new`) {#custom-context-with-new}

當你需要傳送者、epoch 或時間戳記的特定值時，請使用 `tx_context::new`：

```move
use std::unit_test::assert_eq;

#[test]
fun test_with_specific_sender() {
    let sender = @0xA;
    let tx_hash = x"3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532";
    let epoch = 5;
    let epoch_timestamp_ms = 1234567890000;
    let ids_created = 0;

    let ctx = &mut tx_context::new(
        sender,
        tx_hash,
        epoch,
        epoch_timestamp_ms,
        ids_created,
    );

    assert_eq!(ctx.sender(), @0xA);
    assert_eq!(ctx.epoch(), 5);
}
```

`tx_hash` 必須剛好是 32 個位元組。為了方便起見，請使用 `new_from_hint`，從簡單整數產生唯一的雜湊：

```move
#[test]
fun test_with_hint() {
    let ctx = &mut tx_context::new_from_hint(
        @0xA,    // 傳送者
        42,      // 提示值（用於產生唯一的 tx_hash）
        5,       // epoch
        1000,    // epoch_timestamp_ms
        0,       // ids_created
    );
    // ...
}
```

## 追蹤已建立的物件 (Tracking Created Objects) {#tracking-created-objects}

測試物件建立時，你可能想驗證建立了多少物件，或取得最後建立之物件的地址：

```move
use std::unit_test::{assert_eq, destroy};

#[test]
fun test_object_creation_count() {
    let ctx = &mut tx_context::dummy();

    assert_eq!(ctx.ids_created(), 0);

    let obj1 = my_module::new(ctx);
    assert_eq!(ctx.ids_created(), 1);

    let obj2 = my_module::new(ctx);
    assert_eq!(ctx.ids_created(), 2);

    // 取得最近建立物件的地址（由其 ID 推導而來）
    let last_id = ctx.last_created_object_id();
    assert_eq!(last_id, object::id(&obj2).to_address());

    // 物件沒有 `drop`，因此需要清理
    destroy(obj1);
    destroy(obj2);
}
```

## 模擬時間與 Epoch (Simulating Time and Epochs) {#simulating-time-and-epochs}

若測試依賴時間或 epoch 變更，請使用遞增函式：

```move
use std::unit_test::assert_eq;

#[test]
fun test_time_dependent_logic() {
    let ctx = &mut tx_context::dummy();

    // 初始狀態
    assert_eq!(ctx.epoch(), 0);
    assert_eq!(ctx.epoch_timestamp_ms(), 0);

    // 模擬 epoch 變更
    ctx.increment_epoch_number();
    assert_eq!(ctx.epoch(), 1);

    // 模擬時間流逝（增加 1 天的毫秒數）
    ctx.increment_epoch_timestamp(24 * 60 * 60 * 1000);
    assert_eq!(ctx.epoch_timestamp_ms(), 86_400_000);
}
```

## 使用 `create` 完整控制 (Full Control with `create`) {#full-control-with-create}

若要完整控制所有情境欄位，包括與 gas 相關的值，請使用 `tx_context::create`：

```move
use std::unit_test::assert_eq;

#[test]
fun test_with_full_context() {
    let ctx = &tx_context::create(
        @0xA,                    // 傳送者
        tx_context::dummy_tx_hash_with_hint(1), // tx_hash
        10,                      // epoch
        1700000000000,           // epoch_timestamp_ms
        0,                       // ids_created
        1000,                    // reference_gas_price
        1500,                    // gas_price
        10_000_000,              // gas_budget
        option::none(),          // 贊助者（None = 無贊助者）
    );

    assert_eq!(ctx.gas_budget(), 10_000_000);
}
```

## 總結 (Summary) {#summary}

| 函式                          | 使用情境                           |
| ----------------------------- | ---------------------------------- |
| `dummy()`                     | 用於簡單測試的快速情境             |
| `new()`                       | 自訂傳送者、epoch 或時間戳記       |
| `new_from_hint()`             | 類似 `new`，但會從整數產生 tx_hash |
| `create()`                    | 完整控制，包括 gas 參數            |
| `ids_created()`               | 檢查已建立的物件數量               |
| `last_created_object_id()`    | 取得最近建立物件的地址             |
| `increment_epoch_number()`    | 模擬 epoch 推進                    |
| `increment_epoch_timestamp()` | 模擬時間流逝                       |

## 延伸閱讀 (Further Reading) {#further-reading}

- [交易情境](./../programmability/transaction-context.md) - `TxContext` 及其在交易中角色的詳細概覽
