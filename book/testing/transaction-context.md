---
description: "在 Move 測試中模擬 TxContext：建立虛擬上下文、設置發送者位址、為單元測試生成全新的 UID。"
---

# 模擬交易上下文 (Simulating Transaction Context)

大多數建立物件或與使用者交互的 Move 函式都有一個 `TxContext` 參數。當交易被執行時，其值由執行時期提供，但在測試中你需要自己建立並傳遞它。`sui::tx_context` 模組為此目的提供了幾個實用函式。

> **注意：** 本章中的實用函式只適用於簡單的單元測試。它們無法存取來自儲存的共享或已轉移物件。對於需要從儲存中取得物件或模擬多交易情境的測試，請使用
> [測試情境 (Test Scenario)](./test-scenario.md)。

## 建立虛擬上下文 (Creating a Dummy Context)

獲取 `TxContext` 最簡單的方式是 `tx_context::dummy()`。它建立一個預設值的上下文 - 零位址發送者、紀元 0 和一個固定的交易雜湊：

```move
use std::unit_test::assert_eq;

#[test]
fun test_create_object() {
    let ctx = &mut tx_context::dummy();
    let obj = my_module::new(ctx);

    assert_eq!(ctx.sender(), @0); // 發送者預設為 0x0
    // ...
}
```

對於大多數你不關心特定上下文值的測試，以及當你需要測試物件的建立而不是與儲存的交互時，這已經足夠了。

## 使用 `new` 的自訂上下文 (Custom Context with `new`)

當你需要發送者、紀元或時間戳記的特定值時，使用 `tx_context::new`：

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

`tx_hash` 必須恰好是 32 位元組。為了方便，使用 `new_from_hint` 從簡單整數生成唯一的雜湊：

```move
#[test]
fun test_with_hint() {
    let ctx = &mut tx_context::new_from_hint(
        @0xA,    // 發送者
        42,      // 提示（用於生成唯一的 tx_hash）
        5,       // 紀元
        1000,    // 紀元時間戳記（毫秒）
        0,       // 已建立的 ID 數
    );
    // ...
}
```

## 追蹤已建立的物件 (Tracking Created Objects)

當測試物件建立時，你可能想要驗證有多少個物件被建立或取得最後一個建立的物件的 ID：

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

    // 取得最近建立的物件的 ID
    let last_id = ctx.last_created_object_id();

    // ...
}
```

## 模擬時間和紀元 (Simulating Time and Epochs)

對於依賴時間或紀元變化的測試，使用增量函式：

```move
use std::unit_test::assert_eq;

#[test]
fun test_time_dependent_logic() {
    let ctx = &mut tx_context::dummy();

    // 初始狀態
    assert_eq!(ctx.epoch(), 0);
    assert_eq!(ctx.epoch_timestamp_ms(), 0);

    // 模擬紀元變化
    ctx.increment_epoch_number();
    assert_eq!(ctx.epoch(), 1);

    // 模擬時間流逝（加上 1 天的毫秒數）
    ctx.increment_epoch_timestamp(24 * 60 * 60 * 1000);
    assert_eq!(ctx.epoch_timestamp_ms(), 86_400_000);
}
```

## 使用 `create` 進行完整控制 (Full Control with `create`)

為了完全控制所有上下文欄位（包括 gas 相關的值），使用 `tx_context::create`：

```move
use std::unit_test::assert_eq;

#[test]
fun test_with_full_context() {
    let ctx = &tx_context::create(
        @0xA,                    // 發送者
        tx_context::dummy_tx_hash_with_hint(1), // tx_hash
        10,                      // 紀元
        1700000000000,           // 紀元時間戳記（毫秒）
        0,                       // 已建立的 ID 數
        1000,                    // 參考 gas 價格
        1500,                    // gas 價格
        10_000_000,              // gas 預算
        option::none(),          // 贊助者（None = 無贊助者）
    );

    assert_eq!(ctx.gas_budget(), 10_000_000);
}
```

## 總結 (Summary)

| 函式                          | 使用情境                      |
| ----------------------------- | --------------------------------------------- |
| `dummy()`                     | 簡單測試的快速上下文                |
| `new()`                       | 自訂發送者、紀元或時間戳記            |
| `new_from_hint()`             | 類似 `new` 但從整數生成 tx_hash |
| `create()`                    | 完全控制（包含 gas 參數）         |
| `ids_created()`               | 檢查已建立的物件數                   |
| `last_created_object_id()`    | 取得最近建立的物件 ID                  |
| `increment_epoch_number()`    | 模擬紀元進度                    |
| `increment_epoch_timestamp()` | 模擬時間流逝                         |

## 進一步閱讀 (Further Reading)

- [交易上下文](./../programmability/transaction-context.md) - `TxContext` 及其在交易中角色的詳細概述
