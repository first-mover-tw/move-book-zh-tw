---
description: "在 Move 測試中模擬 TxContext：建立虛擬上下文 (dummy context)、設定發送者地址，並生成用於單元測試的新 UID。"
---

# 模擬交易上下文 (Simulating Transaction Context)

大多數建立物件或與使用者互動的 Move 函式都有一個 `TxContext` 參數。當交易執行時，其值由運行時 (runtime) 提供，但在測試中你需要自行建立並傳遞它。`sui::tx_context` 模組為此目的提供了幾個實用函式。

> **注意：** 本章中的工具僅適用於簡單的單元測試。它們不提供對存儲中共享物件或已轉移物件的存取。對於需要從存儲中獲取物件或模擬多交易場景的測試，請使用 [測試場景 (Test Scenario)](./test-scenario.md)。

## 建立虛擬上下文

獲取 `TxContext` 最簡單的方法是 `tx_context::dummy()`。它建立一個具有預設值的上下文 —— 零地址發送者、Epoch 0 和固定的交易雜湊值：

```move
use std::unit_test::assert_eq;

#[test]
fun test_create_object() {
    let ctx = &mut tx_context::dummy();
    let obj = my_module::new(ctx);

    assert_eq!(ctx.sender(), @0); // 預設發送者為 0x0
    // ...
}
```

這對於大多數不關心具體上下文數值，且需要測試物件建立而非與存儲互動的測試來說已經足夠了。

## 使用 `new` 自定義上下文

當你需要特定的發送者、Epoch 或時間戳記時，使用 `tx_context::new`：

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

`tx_hash` 必須剛好是 32 位元組。為了方便起見，可以使用 `new_from_hint` 從一個簡單的整數生成唯一的雜湊值：

```move
#[test]
fun test_with_hint() {
    let ctx = &mut tx_context::new_from_hint(
        @0xA,    // sender
        42,      // hint (提示值，用於生成唯一的 tx_hash)
        5,       // epoch
        1000,    // epoch_timestamp_ms
        0,       // ids_created
    );
    // ...
}
```

## 追蹤已建立的物件

測試物件建立時，你可能想要驗證建立了多少個物件，或獲取最後建立物件的 ID：

```move
use std::unit_test::assert_eq;

#[test]
fun test_object_creation_count() {
    let ctx = &mut tx_context::dummy();

    assert_eq!(ctx.ids_created(), 0);

    let obj1 = my_module::new(ctx);
    assert_eq!(ctx.ids_created(), 1);

    let obj2 = my_module::new(ctx);
    assert_eq!(ctx.ids_created(), 2);

    // 獲取最近建立物件的 ID
    let last_id = ctx.last_created_object_id();

    // ...
}
```

## 模擬時間和 Epoch

對於依賴時間或 Epoch 變更的測試，使用遞增函式：

```move
use std::unit_test::assert_eq;

#[test]
fun test_time_dependent_logic() {
    let ctx = &mut tx_context::dummy();

    // 初始狀態
    assert_eq!(ctx.epoch(), 0);
    assert_eq!(ctx.epoch_timestamp_ms(), 0);

    // 模擬 Epoch變更
    ctx.increment_epoch_number();
    assert_eq!(ctx.epoch(), 1);

    // 模擬時間流逝 (增加 1 天的毫秒數)
    ctx.increment_epoch_timestamp(24 * 60 * 60 * 1000);
    assert_eq!(ctx.epoch_timestamp_ms(), 86_400_000);
}
```

## 使用 `create` 進行完全控制

如果需要完全控制所有上下文欄位，包括與 Gas 相關的數值，請使用 `tx_context::create`：

```move
use std::unit_test::assert_eq;

#[test]
fun test_with_full_context() {
    let ctx = &tx_context::create(
        @0xA,                    // sender
        tx_context::dummy_tx_hash_with_hint(1), // tx_hash
        10,                      // epoch
        1700000000000,           // epoch_timestamp_ms
        0,                       // ids_created
        1000,                    // reference_gas_price
        1500,                    // gas_price
        10_000_000,              // gas_budget
        option::none(),          // sponsor (None = 無贊助者)
    );

    assert_eq!(ctx.gas_budget(), 10_000_000);
}
```

## 總結

| 函式 | 使用場景 |
| ----------------------------- | --------------------------------------------- |
| `dummy()` | 用於簡單測試的快速上下文 |
| `new()` | 自定義發送者、Epoch 或時間戳記 |
| `new_from_hint()` | 類似 `new`，但從整數生成 tx_hash |
| `create()` | 完全控制，包括 Gas 參數 |
| `ids_created()` | 檢查建立的物件數量 |
| `last_created_object_id()` | 獲取最近建立物件的 ID |
| `increment_epoch_number()` | 模擬 Epoch 進展 |
| `increment_epoch_timestamp()` | 模擬時間流逝 |

## 延伸閱讀

- [交易上下文 (Transaction Context)](./../programmability/transaction-context.md) - 詳細介紹 `TxContext` 及其在交易中的角色
