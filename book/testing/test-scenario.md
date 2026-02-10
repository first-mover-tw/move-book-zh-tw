---
description: "Sui Move 中的測試情境：模擬多交易流程、測試物件轉移，並在測試中驗證共享物件行為。"
---

# 測試情境 (Test Scenario)

[Sui Framework](./../programmability/sui-framework.md) 的 `test_scenario` 模組提供了一種方式來模擬測試中的多交易情境。它維護全域物件池的視圖，並允許你測試物件如何在多個交易中建立、轉移和存取。

```move
#[test_only]
use sui::test_scenario;
```

## 開始和結束情境

測試情境以 `test_scenario::begin` 開始，它以發送者位址作為參數。情境必須以 `test_scenario::end` 結束以清理資源。如果未正確結束情境，將導致編譯錯誤。

> **注意：** 每個測試中應該只有一個情境。在同一測試中建立多個情境可能會產生意外結果，應該避免。

```move
use sui::test_scenario;

#[test]
fun test_basic_scenario() {
    let alice = @0xA;

    // 以 alice 作為發送者啟動情境
    let mut scenario = test_scenario::begin(alice);

    // ... 執行操作 ...

    // 結束情境 - 返回 TransactionEffects
    scenario.end();
}
```

## 交易模擬

使用 `next_tx` 推進到新交易並指定發送者。在前一交易中轉移的物件將在下一個交易中可用。每個 `next_tx` 呼叫返回 [`TransactionEffects`](#讀取交易效果) 包含有關前一個交易中發生的訊息。

```move
use sui::test_scenario;

#[test]
fun test_multi_transaction() {
    let alice = @0xA;
    let bob = @0xB;

    let mut scenario = test_scenario::begin(alice);

    // 第一個交易：alice 建立物件
    // 在此建立的物件尚未在任何人的物件清單中

    // 推進到第二個交易，bob 為發送者
    // 第一個交易中的物件現在可用
    let _effects = scenario.next_tx(bob);

    // ... bob 現在可以存取轉移給他的物件 ...

    scenario.end();
}
```

> 重要：交易期間轉移的物件只有在呼叫 `next_tx` 後才可用。你不能在轉移物件的同一交易中存取該物件。

## 存取擁有的物件

[擁有的物件](./../object/ownership.md#owned-by-an-address) 轉移到位址可以使用 `take_from_sender` 或 `take_from_address` 存取。然後可以將物件傳遞給函式、使用 `return_to_sender` 或 `return_to_address` 返回，或使用 `public_transfer` 轉移到其他地方（如果物件有 `store` 能力）。

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

    // 交易 1：建立物件並轉移到 alice
    {
        let item = create(100, scenario.ctx());
        transfer::public_transfer(item, alice);
    };

    // 交易 2：Alice 取得物件
    scenario.next_tx(alice);
    {
        // 從發送者的物件清單中取得最近的 Item
        let item = scenario.take_from_sender<Item>();
        assert_eq!(item.value(), 100);

        // 返回物件到發送者的物件清單
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 按 ID 取得

當存在多個相同類型的物件時，使用 `take_from_sender_by_id` 或 `take_from_address_by_id` 取得特定物件：

```move
#[test]
fun test_take_by_id() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立兩個物件
    let item1 = create(100, scenario.ctx());
    let item2 = create(200, scenario.ctx());
    let id1 = object::id(&item1);

    transfer::public_transfer(item1, alice);
    transfer::public_transfer(item2, alice);

    scenario.next_tx(alice);
    {
        // 按 ID 取得特定物件
        let item = scenario.take_from_sender_by_id<Item>(id1);
        assert_eq!(item.value(), 100);
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 檢查物件可用性

在取得物件之前，可以檢查是否存在物件：

```move
#[test]
fun test_has_object() {
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 尚無物件存在
    assert!(!scenario.has_most_recent_for_sender<Item>());

    let item = create(100, scenario.ctx());
    transfer::public_transfer(item, alice);

    scenario.next_tx(alice);

    // 現在物件存在
    assert!(scenario.has_most_recent_for_sender<Item>());

    scenario.end();
}
```

## 存取共享物件

[共享物件](./../object/ownership.md#shared-state) 使用 `take_shared` 存取，必須使用 `return_shared` 返回：

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

    // Alice 建立共享計數器
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

為了更簡潔的程式碼，使用 `with_shared!` 巨集自動處理取得和返回：

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

## 存取不可變物件

[不可變（凍結）物件](./../object/ownership.md#immutable-frozen-object) 使用 `take_immutable` 存取，使用 `return_immutable` 返回：

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

    // 建立不可變設定
    create(1000, scenario.ctx());

    scenario.next_tx(alice);
    {
        // 取得不可變物件
        let config = scenario.take_immutable<Config>();
        assert_eq!(config.max_value(), 1000);

        // 返回到全域物件清單
        test_scenario::return_immutable(config);
    };

    scenario.end();
}
```

## 存取交易上下文

`ctx` 方法提供對目前交易的 [`TxContext`](./../programmability/transaction-context.md) 的存取。當呼叫需要上下文的函式時使用它：

```move
#[test]
fun test_context_access() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 存取交易上下文
    let ctx = scenario.ctx();

    // 使用它進行需要上下文的操作
    let item = create(100, ctx);
    transfer::public_transfer(item, alice);

    // 發送者與傳遞給 begin() 的相符
    assert_eq!(ctx.sender(), alice);

    scenario.end();
}
```

## 讀取交易效果

`next_tx` 和 `end` 都返回 `TransactionEffects`，其中包含有關交易期間發生的訊息：

```move
#[test]
fun test_transaction_effects() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let bob = @0xB;
    let mut scenario = test_scenario::begin(alice);

    // 在第一個交易中建立物件
    let item1 = create(100, scenario.ctx());
    let item2 = create(200, scenario.ctx());
    transfer::public_transfer(item1, alice);
    transfer::public_transfer(item2, bob);

    // 取得第一個交易的效果
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

| 方法                       | 返回              | 描述                       |
| -------------------------- | --------------- | -------------------------- |
| `created()`                | `vector<ID>`    | 在此交易中建立的物件       |
| `written()`                | `vector<ID>`    | 在此交易中修改的物件       |
| `deleted()`                | `vector<ID>`    | 在此交易中刪除的物件       |
| `transferred_to_account()` | `VecMap<ID, address>` | 轉移到位址的物件      |
| `transferred_to_object()`  | `VecMap<ID, ID>` | 轉移到其他物件的物件     |
| `shared()`                 | `vector<ID>`    | 在此交易中共享的物件       |
| `frozen()`                 | `vector<ID>`    | 在此交易中凍結的物件       |
| `num_user_events()`        | `u64`           | 發出的事件數量             |

## 系統物件

使用 `create_system_objects` 使系統物件如 `Clock`、`Random` 和 `DenyList` 在測試中可用。有關使用系統物件進行測試的更詳細說明，請參閱 [使用系統物件](./using-system-objects.md)。

```move
use sui::clock::Clock;

#[test]
fun test_with_clock() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立系統物件（Clock、Random、DenyList）
    scenario.create_system_objects();

    scenario.next_tx(alice);
    {
        // 現在 Clock 作為共享物件可用
        let clock = scenario.take_shared<Clock>();
        assert_eq!(clock.timestamp_ms(), 0);
        test_scenario::return_shared(clock);
    };

    scenario.end();
}
```

## 紀元和時間操作

使用 `next_epoch` 和 `later_epoch` 測試 [時間相關邏輯](./../programmability/epoch-and-time.md)：

```move
#[test]
fun test_epoch_advancement() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 檢查初始紀元
    assert_eq!(scenario.ctx().epoch(), 0);

    // 推進到下一個紀元
    scenario.next_epoch(alice);
    assert_eq!(scenario.ctx().epoch(), 1);

    // 一起推進紀元和時間（1000ms = 1 秒）
    scenario.later_epoch(1000, alice);
    assert_eq!(scenario.ctx().epoch(), 2);
    assert_eq!(scenario.ctx().epoch_timestamp_ms(), 1000);

    scenario.end();
}
```

## 完整範例

以下是測試簡單代幣轉移流程的完整範例：

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

    // 以 admin 開始情境
    let mut scenario = test_scenario::begin(admin);

    // Admin 為 alice 鑄造代幣
    {
        let token = mint(1000, scenario.ctx());
        transfer::public_transfer(token, alice);
    };

    // Alice 接收並轉移到 bob
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

    // 通過效果驗證最終狀態
    let effects = scenario.end();
    assert_eq!(effects.transferred_to_account().size(), 0); // 最終交易中無轉移
}
```

## 總結

| 函式                        | 用途                           |
| --------------------------- | ------------------------------ |
| `begin(sender)`             | 啟動新情境                     |
| `end(scenario)`             | 結束情境並取得最終效果         |
| `next_tx(scenario, sender)` | 推進到下一個交易               |
| `ctx(scenario)`             | 取得 `TxContext` 的可變參考    |
| `take_from_sender<T>`       | 從發送者取得擁有的物件         |
| `return_to_sender(obj)`     | 返回物件到發送者               |
| `take_shared<T>`            | 取得共享物件                   |
| `return_shared(obj)`        | 返回共享物件                   |
| `take_immutable<T>`         | 取得不可變物件                 |
| `return_immutable(obj)`     | 返回不可變物件                 |
| `create_system_objects`     | 建立 Clock、Random、DenyList   |
| `next_epoch`                | 推進到下一個紀元               |
| `later_epoch(ms, sender)`   | 推進紀元和時間                 |

## 延伸閱讀

- [使用系統物件](./using-system-objects.md) - 在測試中建立和操作 Clock、Random、DenyList、Coin 和 Balance
- [測試工具](./test-utilities.md) - `assert_eq!`、`destroy` 和其他測試幫助函式
- [交易上下文](./../programmability/transaction-context.md) - 理解 `TxContext` 及其欄位
- [物件所有權](./../object/ownership.md) - 擁有、共享和不可變物件的運作方式
- [紀元和時間](./../programmability/epoch-and-time.md) - 在 Sui 中使用時間
