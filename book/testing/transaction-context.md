---
description:
  在 Move 測試中模擬 TxContext (TxContext)：建立虛擬情境 (context)、設定發送者地址，並產生新的 UID
  供單元測試使用。
---

# 模擬交易情境 (Simulating Transaction Context) {#simulating-transaction-context}

大多數建立物件或與使用者互動的 Move 函式都有一個 `TxContext` 引數。當交易被執行時，其值由執行環境提供，但在測試中你需要自行建立並傳入。`sui::tx_context` 模組提供了幾個工具函式來達成這個目的。

> **注意：** 本章的工具僅適用於簡單的單元測試。它們無法存取儲存中的共享或轉移物件。若測試需要從儲存中取得物件或模擬多筆交易情境，請使用
> [Test Scenario](./test-scenario.md)。

## 建立虛擬情境 (Creating a Dummy Context) {#creating-a-dummy-context}

取得 `TxContext` 最簡單的方式是 `tx_context::dummy()`。它會建立一個具有預設值的情境——寄件者地址為零、epoch 為 0，以及固定的交易雜湊：

```move
use std::unit_test::assert_eq;

#[test]
fun test_create_object() {
    let ctx = &mut tx_context::dummy();
    let obj = my_module::new(ctx);

    assert_eq!(ctx.sender(), @0); // 預設寄件者為 0x0
    // ...
}
```

對於大多數不在意特定情境值的測試，以及需要測試物件建立（而非與儲存互動）的情況，這已經足夠了。

## 使用 `new` 自訂情境 (Custom Context with `new`) {#custom-context-with-new}

當你需要為寄件者、epoch 或時間戳記指定特定值時，請使用 `tx_context::new`：

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

`tx_hash` 必須恰好是 32 位元組。為求方便，可使用 `new_from_hint` 從一個簡單的整數產生唯一的雜湊值：

```move
#[test]
fun test_with_hint() {
    let ctx = &mut tx_context::new_from_hint(
        @0xA,    // 寄件者
        42,      // hint（用於產生唯一的 tx_hash）
        5,       // epoch
        1000,    // epoch_timestamp_ms
        0,       // ids_created
    );
    // ...
}
```

## 追蹤已建立的物件 (Tracking Created Objects) {#tracking-created-objects}

在測試物件建立時，你可能會想驗證建立了多少個物件，或取得最後建立物件的地址：

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

    // 取得最近建立物件的地址（由其 ID 衍生）
    let last_id = ctx.last_created_object_id();
    assert_eq!(last_id, object::id(&obj2).to_address());

    // 物件沒有 `drop`，所以需要清理
    destroy(obj1);
    destroy(obj2);
}
```

## 模擬時間與 Epoch (Simulating Time and Epochs) {#simulating-time-and-epochs}

對於依賴時間或 epoch 變化的測試，可使用遞增函式：

```move
use std::unit_test::assert_eq;

#[test]
fun test_time_dependent_logic() {
    let ctx = &mut tx_context::dummy();

    // 初始狀態
    assert_eq!(ctx.epoch(), 0);
    assert_eq!(ctx.epoch_timestamp_ms(), 0);

    // 模擬 epoch 變化
    ctx.increment_epoch_number();
    assert_eq!(ctx.epoch(), 1);

    // 模擬時間經過（新增以毫秒表示的 1 天）
    ctx.increment_epoch_timestamp(24 * 60 * 60 * 1000);
    assert_eq!(ctx.epoch_timestamp_ms(), 86_400_000);
}
```

## 使用 `create` 完全控制 (Full Control with `create`) {#full-control-with-create}

若要完全控制所有情境欄位（包含與 gas 相關的值），請使用 `tx_context::create`：

```move
use std::unit_test::assert_eq;

#[test]
fun test_with_full_context() {
    let ctx = &tx_context::create(
        @0xA,                    // 寄件者
        tx_context::dummy_tx_hash_with_hint(1), // tx_hash
        10,                      // epoch
        1700000000000,           // epoch_timestamp_ms
        0,                       // ids_created
        1000,                    // reference_gas_price
        1500,                    // gas_price
        10_000_000,              // gas_budget
        option::none(),          // sponsor（None = 無贊助者）
    );

    assert_eq!(ctx.gas_budget(), 10_000_000);
}
```

## 總結 (Summary) {#summary}

| 函式                          | 使用情境                         |
| ----------------------------- | -------------------------------- |
| `dummy()`                     | 適用於簡單測試的快速情境         |
| `new()`                       | 自訂寄件者、epoch 或時間戳記     |
| `new_from_hint()`             | 類似 `new`，但從整數產生 tx_hash |
| `create()`                    | 完全控制，包含 gas 參數          |
| `ids_created()`               | 檢查已建立的物件數量             |
| `last_created_object_id()`    | 取得最近建立物件的地址           |
| `increment_epoch_number()`    | 模擬 epoch 進展                  |
| `increment_epoch_timestamp()` | 模擬時間經過                     |

## 延伸閱讀 (Further Reading) {#further-reading}

- [交易情境](./../programmability/transaction-context.md)——關於 `TxContext` 及其在交易中角色的詳細概述
