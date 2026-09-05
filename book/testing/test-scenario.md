---
description: Sui Move 中的測試情境 (Test Scenario)：模擬多筆交易流程 (multi-transaction flows)、測試物件轉移 (object transfers)，並在測試中驗證共享物件行為 (shared object behavior)。
title: 測試情境 (Test Scenario)
keywords:
  - Move
  - Sui
  - Move tutorial
  - test
  - scenario
  - testing
questions:
  - What is Test Scenario in Move?
  - How do I use Test Scenario in Move?
  - What is Starting and Ending a Scenario in Move?
  - What is Transaction Simulation in Move?
answer: 'Test Scenario in Sui Move: simulate multi-transaction flows, test object transfers, and verify shared object behavior in tests.'
goal:
  description: 'Reader can test Scenario in Sui Move: simulate multi-transaction flows, test object transfers, and verify shared object behavior in tests'
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

# 測試情境 (Test Scenario) {#test-scenario}

來自 [Sui Framework](./../programmability/sui-framework.md) 的 `test_scenario` 模組提供了一種在測試中模擬多筆交易情境的方法。它會維護全域物件集區的檢視，並讓你測試物件如何在多筆交易之間建立、轉移及存取。

```move
#[test_only]
use sui::test_scenario;
```

## 情境的開始與結束 (Starting and Ending a Scenario) {#starting-and-ending-a-scenario}

測試情境會以 `test_scenario::begin` 開始，並將傳送者地址作為引數。
情境必須使用 `test_scenario::end` 結束以清理資源。未結束情境將導致
編譯錯誤。

> **注意**：每個測試應只有一個情境。在同一個測試中建立多個情境
> 可能會產生非預期結果，應避免這麼做。

```move
use sui::test_scenario;

#[test]
fun test_basic_scenario() {
    let alice = @0xA;

    // 以 alice 作為傳送者開始情境
    let mut scenario = test_scenario::begin(alice);

    // ... 執行操作 ...

    // 結束情境 - 回傳 TransactionEffects
    scenario.end();
}
```

## 交易模擬 (Transaction Simulation) {#transaction-simulation}

使用 `next_tx` 以指定的傳送者推進至新的交易。於前一筆交易中轉移的物件會在下一筆交易中可供使用。每次呼叫 `next_tx` 都會回傳 [`TransactionEffects`](#reading-transaction-effects)，其中包含前一筆交易中所發生事項的資訊。

```move
use sui::test_scenario;

#[test]
fun test_multi_transaction() {
    let alice = @0xA;
    let bob = @0xB;

    let mut scenario = test_scenario::begin(alice);

    // 第一筆交易：alice 建立物件
    // 此處建立的物件尚未存在於任何人的庫存中

    // 以 bob 作為傳送者推進至第二筆交易
    // 第一筆交易中的物件現在已可供使用
    let _effects = scenario.next_tx(bob);

    // ... bob 現在可以存取轉移給他的物件 ...

    scenario.end();
}
```

> 重要事項：在交易期間轉移的物件，只有在呼叫 `next_tx` 後才可供使用。
> 你無法在物件被轉移的同一筆交易中存取它。

## 存取擁有物件 (Accessing Owned Objects) {#accessing-owned-objects}

轉移至地址的[擁有物件](./../object/ownership.md#account-owner-or-single-owner)可以使用 `take_from_sender` 或 `take_from_address` 存取。接著可將該物件傳遞給函式、使用 `return_to_sender` 或 `return_to_address` 回傳，或使用 `public_transfer` 將其轉移至其他位置（如果物件具有 `store` 能力）。

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

    // 交易 1：建立項目並將其轉移給 alice
    {
        let item = create(100, scenario.ctx());
        transfer::public_transfer(item, alice);
    };

    // 交易 2：Alice 取得項目
    scenario.next_tx(alice);
    {
        // 從傳送者的庫存中取得最新的 Item
        let item = scenario.take_from_sender<Item>();
        assert_eq!(item.value(), 100);

        // 將項目回傳至傳送者的庫存
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 依 ID 取得 (Taking by ID) {#taking-by-id}

當存在多個相同型別的物件時，請使用 `take_from_sender_by_id` 或 `take_from_address_by_id` 取得特定物件：

```move
#[test]
fun test_take_by_id() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立兩個項目
    let item1 = create(100, scenario.ctx());
    let item2 = create(200, scenario.ctx());
    let id1 = object::id(&item1);

    transfer::public_transfer(item1, alice);
    transfer::public_transfer(item2, alice);

    scenario.next_tx(alice);
    {
        // 依 ID 取得特定項目
        let item = scenario.take_from_sender_by_id<Item>(id1);
        assert_eq!(item.value(), 100);
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 檢查物件可用性 (Checking Object Availability) {#checking-object-availability}

取得物件前，你可以檢查物件是否存在：

```move
#[test]
fun test_has_object() {
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 尚未存在任何項目
    assert!(!scenario.has_most_recent_for_sender<Item>());

    let item = create(100, scenario.ctx());
    transfer::public_transfer(item, alice);

    scenario.next_tx(alice);

    // 現在已有項目存在
    assert!(scenario.has_most_recent_for_sender<Item>());

    scenario.end();
}
```

## 存取共享物件 (Accessing Shared Objects) {#accessing-shared-objects}

[共享物件](./../object/ownership.md#shared-state)使用 `take_shared` 來存取，且必須透過 `return_shared` 回傳：

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

    // Bob 將其遞增
    scenario.next_tx(bob);
    {
        let mut counter = scenario.take_shared<Counter>();
        counter.increment();
        assert_eq!(counter.value(), 1);
        test_scenario::return_shared(counter);
    };

    // Alice 再次將其遞增
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

### `with_shared` 巨集 (The `with_shared` Macro) {#the-with_shared-macro}

為了讓原始碼更簡潔，請使用會自動處理取得與回傳的 `with_shared!` 巨集：

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

## 存取不可變物件 (Accessing Immutable Objects) {#accessing-immutable-objects}

[不可變（凍結）物件](./../object/ownership.md#immutable-frozen-state)可透過
`take_immutable` 存取，並以 `return_immutable` 歸還：

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

        // 將其歸還至全域庫存
        test_scenario::return_immutable(config);
    };

    scenario.end();
}
```

## 存取交易情境 (Accessing Transaction Context) {#accessing-transaction-context}

`ctx` 方法可讓你存取目前交易的 [`TxContext`](./../programmability/transaction-context.md)。
在呼叫需要情境的函式時使用它：

```move
#[test]
fun test_context_access() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 存取交易情境
    let ctx = scenario.ctx();

    // 將它用於需要情境的操作
    let item = create(100, ctx);
    transfer::public_transfer(item, alice);

    // 傳送者與我們傳給 begin() 的值相符
    assert_eq!(ctx.sender(), alice);

    scenario.end();
}
```

## 讀取交易效果 (Reading Transaction Effects) {#reading-transaction-effects}

`next_tx` 與 `end` 都會回傳 `TransactionEffects`，其中包含交易期間發生事項的資訊：

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

    // 取得第一筆交易的效果
    let effects = scenario.next_tx(alice);

    // 檢查建立的項目
    assert_eq!(effects.created().length(), 2);

    // 檢查轉移至帳戶的項目
    assert_eq!(effects.transferred_to_account().size(), 2);

    // 檢查發出的事件數量
    assert_eq!(effects.num_user_events(), 0);

    scenario.end();
}
```

### 可用的效果欄位 (Available Effect Fields) {#available-effect-fields}

| 方法                       | 回傳值                | 說明                 |
| -------------------------- | --------------------- | -------------------- |
| `created()`                | `vector<ID>`          | 此交易中建立的物件   |
| `written()`                | `vector<ID>`          | 此交易中修改的物件   |
| `deleted()`                | `vector<ID>`          | 此交易中刪除的物件   |
| `transferred_to_account()` | `VecMap<ID, address>` | 轉移至地址的物件     |
| `transferred_to_object()`  | `VecMap<ID, ID>`      | 轉移至其他物件的物件 |
| `shared()`                 | `vector<ID>`          | 此交易中共享的物件   |
| `frozen()`                 | `vector<ID>`          | 此交易中凍結的物件   |
| `num_user_events()`        | `u64`                 | 發出的事件數量       |

## 系統物件 (System Objects) {#system-objects}

使用 `create_system_objects` 讓 `Clock`、`Random` 和 `DenyList` 等系統物件可在測試中使用。如需更詳細的系統物件測試說明，請參閱 [使用系統物件](./using-system-objects.md)。

```move
use sui::clock::Clock;

#[test]
fun test_with_clock() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立系統物件（Clock、Random、DenyList）
    // 此呼叫會推進交易，因此物件可立即使用
    scenario.create_system_objects();

    {
        // 現在 Clock 可作為共享物件使用
        let clock = scenario.take_shared<Clock>();
        assert_eq!(clock.timestamp_ms(), 0);
        test_scenario::return_shared(clock);
    };

    scenario.end();
}
```

## Epoch 與時間操作 (Epoch and Time Manipulation) {#epoch-and-time-manipulation}

使用 `next_epoch` 與 `later_epoch` 測試[依賴時間的邏輯](./../programmability/epoch-and-time.md)：

```move
#[test]
fun test_epoch_advancement() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 檢查初始 epoch
    assert_eq!(scenario.ctx().epoch(), 0);

    // 推進至下一個 epoch
    scenario.next_epoch(alice);
    assert_eq!(scenario.ctx().epoch(), 1);

    // 同時推進 epoch 與時間（1000ms = 1 秒）
    scenario.later_epoch(1000, alice);
    assert_eq!(scenario.ctx().epoch(), 2);
    assert_eq!(scenario.ctx().epoch_timestamp_ms(), 1000);

    scenario.end();
}
```

## 完整範例 (Complete Example) {#complete-example}

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

    // 以 admin 身分開始情境
    let mut scenario = test_scenario::begin(admin);

    // Admin 為 alice 鑄造代幣
    {
        let token = mint(1000, scenario.ctx());
        transfer::public_transfer(token, alice);
    };

    // Alice 接收後轉移給 bob
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

    // 透過交易效果驗證最終狀態：`return_to_sender` 會記錄為
    // 最終交易效果中轉移回 bob 的操作
    let effects = scenario.end();
    assert_eq!(effects.transferred_to_account().size(), 1);
}
```

## 總結 (Summary) {#summary}

| 函式                        | 用途                         |
| --------------------------- | ---------------------------- |
| `begin(sender)`             | 開始新的情境                 |
| `end(scenario)`             | 結束情境並取得最終效果       |
| `next_tx(scenario, sender)` | 前進至下一筆交易             |
| `ctx(scenario)`             | 取得 `TxContext` 的可變參考  |
| `take_from_sender<T>`       | 從傳送者取得其擁有的物件     |
| `return_to_sender(obj)`     | 將物件回傳給傳送者           |
| `take_shared<T>`            | 取得共享物件                 |
| `return_shared(obj)`        | 回傳共享物件                 |
| `take_immutable<T>`         | 取得不可變物件               |
| `return_immutable(obj)`     | 回傳不可變物件               |
| `create_system_objects`     | 建立 Clock、Random、DenyList |
| `next_epoch`                | 前進至下一個 epoch           |
| `later_epoch(ms, sender)`   | 前進 epoch 與時間            |

## 延伸閱讀 (Further Reading) {#further-reading}

- [使用系統物件](./using-system-objects.md) - 在測試中建立及操作 Clock、Random、DenyList、Coin 與 Balance
- [測試工具](./test-utilities.md) - `assert_eq!`、`destroy` 與其他測試輔助工具
- [交易情境](./../programmability/transaction-context.md) - 了解 `TxContext` 及其欄位
- [物件擁有權](./../object/ownership.md) - 已擁有、共享與不可變物件的運作方式
- [Epoch 與時間](./../programmability/epoch-and-time.md) - 在 Sui 中使用時間
