---
description: "Sui Move 中的測試場景 (Test Scenario)：模擬多交易流程、測試物件轉移，並在測試中驗證共享物件的行為。"
---

# 測試場景 (Test Scenario)

來自 [Sui Framework](./../programmability/sui-framework.md) 的 `test_scenario` 模組提供了一種在測試中模擬多交易場景的方法。它維護全局物件池的視圖 (view)，並允許你測試物件如何在多個交易之間被建立、轉移和存取。

```move
#[test_only]
use sui::test_scenario;
```

## 開始和結束場景

測試場景以 `test_scenario::begin` 開始，該函式接受發送者地址作為參數。場景必須以 `test_scenario::end` 結束以清理資源。若未能結束場景將導致編譯錯誤。

> **注意：** 每個測試應該只有一個場景。在同一個測試中建立多個場景可能會產生意外結果，應避免這樣做。

```move
use sui::test_scenario;

#[test]
fun test_basic_scenario() {
    let alice = @0xA;

    // 以 alice 作為發送者開始一個場景
    let mut scenario = test_scenario::begin(alice);

    // ... 執行操作 ...

    // 結束場景 - 回傳交易效果 (TransactionEffects)
    scenario.end();
}
```

## 交易模擬

使用 `next_tx` 前進到具有指定發送者的新交易。在前一個交易中轉移的物件將在下一個交易中可用。每個 `next_tx` 調用都會回傳 [`TransactionEffects`](#reading-transaction-effects)，其中包含有關前一個交易中發生的事情的資訊。

```move
use sui::test_scenario;

#[test]
fun test_multi_transaction() {
    let alice = @0xA;
    let bob = @0xB;

    let mut scenario = test_scenario::begin(alice);

    // 第一筆交易：alice 建立一個物件
    // 這裡建立的物件尚未進入任何人的庫存

    // 前進到以 bob 為發送者的第二筆交易
    // 來自第一筆交易的物件現在可用了
    let _effects = scenario.next_tx(bob);

    // ... bob 現在可以存取轉移給他的物件 ...

    scenario.end();
}
```

> 重要：交易期間轉移的物件僅在調用 `next_tx` 後才可用。你無法在轉移物件的同一交易中存取它。

## 存取擁有的物件 (Owned Objects)

轉移到某個地址的[擁有物件](./../object/ownership.md#owned-by-an-address)可以使用 `take_from_sender` 或 `take_from_address` 來存取。然後該物件可以傳遞給函式，使用 `return_to_sender` 或 `return_to_address` 歸還，或者使用 `public_transfer` (如果物件具有 `store` 能力) 轉移到其他地方。

```move
module book::test_scenario_example;

public struct Item has key, store {
    id: UID,
    value: u64,
}

public fun create(value: u64, ctx: &mut TxContext): Item {
    Item { id: object::new(ctx), value }
}

public fun value(item: &Item): u64 { item.value }

#[test]
fun test_take_and_return() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 交易 1：建立並轉移一個 item 給 alice
    {
        let item = create(100, scenario.ctx());
        transfer::public_transfer(item, alice);
    };

    // 交易 2：Alice 取出該 item
    scenario.next_tx(alice);
    {
        // 從發送者的庫存中取出最近的 Item
        let item = scenario.take_from_sender<Item>();
        assert_eq!(item.value(), 100);

        // 將 item 歸還給發送者的庫存
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 透過 ID 取出

當存在多個相同型別的物件時，使用 `take_from_sender_by_id` 或 `take_from_address_by_id` 來取出特定的物件：

```move
#[test]
fun test_take_by_id() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立兩個 item
    let item1 = create(100, scenario.ctx());
    let item2 = create(200, scenario.ctx());
    let id1 = object::id(&item1);

    transfer::public_transfer(item1, alice);
    transfer::public_transfer(item2, alice);

    scenario.next_tx(alice);
    {
        // 透過 ID 取出特定的 item
        let item = scenario.take_from_sender_by_id<Item>(id1);
        assert_eq!(item.value(), 100);
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 檢查物件可用性

在取出物件之前，你可以檢查是否存在該物件：

```move
#[test]
fun test_has_object() {
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 尚未存在任何 item
    assert!(!scenario.has_most_recent_for_sender<Item>());

    let item = create(100, scenario.ctx());
    transfer::public_transfer(item, alice);

    scenario.next_tx(alice);

    // 現在有一個 item 存在
    assert!(scenario.has_most_recent_for_sender<Item>());

    scenario.end();
}
```

## 存取共享物件 (Shared Objects)

[共享物件](./../object/ownership.md#shared-state) 使用 `take_shared` 存取，並且必須使用 `return_shared` 歸還：

```move
module book::shared_counter;

public struct Counter has key {
    id: UID,
    value: u64,
}

public fun create(ctx: &mut TxContext) {
    transfer::share_object(Counter {
        id: object::new(ctx),
        value: 0,
    })
}

public fun increment(counter: &mut Counter) {
    counter.value = counter.value + 1;
}

public fun value(counter: &Counter): u64 { counter.value }

#[test]
fun test_shared_object() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let bob = @0xB;

    let mut scenario = test_scenario::begin(alice);

    // Alice 建立一個共享計數器
    create(scenario.ctx());

    // Bob 遞增它
    scenario.next_tx(bob);
    {
        let mut counter = scenario.take_shared<Counter>();
        counter.increment();
        assert_eq!(counter.value(), 1);
        test_scenario::return_shared(counter);
    };

    // Alice 再次遞增它
    scenario.next_tx(alice);
    {
        let mut counter = scenario.take_shared<Counter>();
        counter.increment();
        assert_eq!(counter.value(), 2);
        test_scenario::return_shared(counter);
    };

    scenario.end();
}
```

### `with_shared` 巨集

為了讓程式碼更簡潔，可以使用 `with_shared!` 巨集，它會自動處理取出和歸還：

```move
#[test]
fun test_with_shared_macro() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    create(scenario.ctx());
    scenario.next_tx(alice);

    scenario.with_shared!<Counter>(|counter, _scenario| {
        counter.increment();
        assert_eq!(counter.value(), 1);
    });

    scenario.end();
}
```

## 存取不可變物件 (Immutable Objects)

[不可變 (凍結) 物件](./../object/ownership.md#immutable-frozen-object) 使用 `take_immutable` 存取，並使用 `return_immutable` 歸還：

```move
module book::immutable_config;

public struct Config has key {
    id: UID,
    max_value: u64,
}

public fun create(max_value: u64, ctx: &mut TxContext) {
    transfer::freeze_object(Config {
        id: object::new(ctx),
        max_value,
    })
}

public fun max_value(config: &Config): u64 { config.max_value }

#[test]
fun test_immutable_object() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立一個不可變配置
    create(1000, scenario.ctx());

    scenario.next_tx(alice);
    {
        // 取出不可變物件
        let config = scenario.take_immutable<Config>();
        assert_eq!(config.max_value(), 1000);

        // 將其歸還給全局庫存
        test_scenario::return_immutable(config);
    };

    scenario.end();
}
```

## 存取交易上下文 (Transaction Context)

`ctx` 方法提供對當前交易的 [`TxContext`](./../programmability/transaction-context.md) 的存取。在調用需要上下文的函式時使用它：

```move
#[test]
fun test_context_access() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 存取交易上下文
    let ctx = scenario.ctx();

    // 將其用於需要上下文的操作
    let item = create(100, ctx);
    transfer::public_transfer(item, alice);

    // 發送者與我們傳遞給 begin() 的一致
    assert_eq!(ctx.sender(), alice);

    scenario.end();
}
```

## 讀取交易效果 (Transaction Effects)

`next_tx` 和 `end` 都會回傳 `TransactionEffects`，其中包含有關交易期間發生事件的資訊：

```move
#[test]
fun test_transaction_effects() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let bob = @0xB;
    let mut scenario = test_scenario::begin(alice);

    // 在第一筆交易中建立物件
    let item1 = create(100, scenario.ctx());
    let item2 = create(200, scenario.ctx());
    transfer::public_transfer(item1, alice);
    transfer::public_transfer(item2, bob);

    // 獲取第一筆交易的效果
    let effects = scenario.next_tx(alice);

    // 檢查建立了什麼
    assert_eq!(effects.created().length(), 2);

    // 檢查轉移到帳戶的物件
    assert_eq!(effects.transferred_to_account().size(), 2);

    // 檢查發出的事件數量
    assert_eq!(effects.num_user_events(), 0);

    scenario.end();
}
```

### 可用的效果欄位

| 方法 | 回傳值 | 描述 |
| -------------------------- | --------------------- | ------------------------------------ |
| `created()` | `vector<ID>` | 在此交易中建立的物件 |
| `written()` | `vector<ID>` | 在此交易中修改的物件 |
| `deleted()` | `vector<ID>` | 在此交易中刪除的物件 |
| `transferred_to_account()` | `VecMap<ID, address>` | 轉移到地址的物件 |
| `transferred_to_object()` | `VecMap<ID, ID>` | 轉移到其他物件的物件 |
| `shared()` | `vector<ID>` | 在此交易中共享的物件 |
| `frozen()` | `vector<ID>` | 在此交易中凍結的物件 |
| `num_user_events()` | `u64` | 發出的事件數量 |

## 系統物件 (System Objects)

使用 `create_system_objects` 讓 `Clock`、`Random` 和 `DenyList` 等系統物件在測試中可用。關於使用系統物件進行測試的更詳細介紹，請參見[使用系統物件](./using-system-objects.md)。

```move
use sui::clock::Clock;

#[test]
fun test_with_clock() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立系統物件 (Clock, Random, DenyList)
    scenario.create_system_objects();

    scenario.next_tx(alice);
    {
        // 現在 Clock 可作為共享物件使用
        let clock = scenario.take_shared<Clock>();
        assert_eq!(clock.timestamp_ms(), 0);
        test_scenario::return_shared(clock);
    };

    scenario.end();
}
```

## Epoch 和時間操作

使用 `next_epoch` 和 `later_epoch` 測試[依賴時間的邏輯](./../programmability/epoch-and-time.md)：

```move
#[test]
fun test_epoch_advancement() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 檢查初始 epoch
    assert_eq!(scenario.ctx().epoch(), 0);

    // 前進到下一個 epoch
    scenario.next_epoch(alice);
    assert_eq!(scenario.ctx().epoch(), 1);

    // 同時推進 epoch 和時間 (1000ms = 1 秒)
    scenario.later_epoch(1000, alice);
    assert_eq!(scenario.ctx().epoch(), 2);
    assert_eq!(scenario.ctx().epoch_timestamp_ms(), 1000);

    scenario.end();
}
```

## 完整範例

這是一個測試簡單代幣轉移流程的完整範例：

```move
module book::simple_token;

public struct Token has key, store {
    id: UID,
    amount: u64,
}

public fun mint(amount: u64, ctx: &mut TxContext): Token {
    Token { id: object::new(ctx), amount }
}

public fun amount(token: &Token): u64 { token.amount }

#[test]
fun test_token_transfer_flow() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let admin = @0xAD;
    let alice = @0xA;
    let bob = @0xB;

    // 以 admin 開始場景
    let mut scenario = test_scenario::begin(admin);

    // Admin 為 alice 鑄造代幣
    {
        let token = mint(1000, scenario.ctx());
        transfer::public_transfer(token, alice);
    };

    // Alice 接收並轉移給 bob
    scenario.next_tx(alice);
    {
        assert!(scenario.has_most_recent_for_sender<Token>());
        let token = scenario.take_from_sender<Token>();
        assert_eq!(token.amount(), 1000);
        transfer::public_transfer(token, bob);
    };

    // Bob 接收代幣
    scenario.next_tx(bob);
    {
        let token = scenario.take_from_sender<Token>();
        assert_eq!(token.amount(), 1000);
        scenario.return_to_sender(token);
    };

    // 透過效果驗證最終狀態
    let effects = scenario.end();
    assert_eq!(effects.transferred_to_account().size(), 0); // 最後一筆交易沒有轉移
}
```

## 總結

| 函式 | 用途 |
| --------------------------- | -------------------------------------- |
| `begin(sender)` | 開始一個新場景 |
| `end(scenario)` | 結束場景並獲取最終效果 |
| `next_tx(scenario, sender)` | 前進到下一筆交易 |
| `ctx(scenario)` | 獲取 `TxContext` 的可變引用 |
| `take_from_sender<T>` | 從發送者取出擁有物件 |
| `return_to_sender(obj)` | 將物件歸還給發送者 |
| `take_shared<T>` | 取出共享物件 |
| `return_shared(obj)` | 歸還共享物件 |
| `take_immutable<T>` | 取出不可變物件 |
| `return_immutable(obj)` | 歸還不可變物件 |
| `create_system_objects` | 建立 Clock, Random, DenyList |
| `next_epoch` | 前進到下一個 Epoch |
| `later_epoch(ms, sender)` | 推進 Epoch 和時間 |

## 延伸閱讀

- [使用系統物件](./using-system-objects.md) - 在測試中建立和操作 Clock, Random, DenyList, Coin 和 Balance
- [測試工具](./test-utilities.md) - `assert_eq!`, `destroy` 和其他測試輔助工具
- [交易上下文](./../programmability/transaction-context.md) - 理解 `TxContext` 及其欄位
- [物件所有權](./../object/ownership.md) - 擁有物件、共享物件和不可變物件如何運作
- [Epoch 和時間](./../programmability/epoch-and-time.md) - 在 Sui 中處理時間
