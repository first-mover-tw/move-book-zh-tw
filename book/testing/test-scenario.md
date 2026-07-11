---
description:
  Sui Move 測試場景 (Test Scenario)：模擬多筆交易流程、測試物件轉移，並驗證測試中的共享物件 (shared object)
  行為。
---

# 測試場景 (Test Scenario) {#test-scenario}

[Sui Framework](./../programmability/sui-framework.md) 中的 `test_scenario` 模組提供了一種在測試中模擬多筆交易場景的方式。它維護了一個全域物件池的視圖，讓你可以測試物件在多筆交易之間如何被建立、轉移與存取。

```move
#[test_only]
use sui::test_scenario;
```

## 開始與結束情境測試 (Starting and Ending a Scenario) {#starting-and-ending-a-scenario}

情境測試（test scenario）以 `test_scenario::begin` 開始，並以傳送者地址作為參數。
情境測試必須以 `test_scenario::end` 結束以清理資源。若沒有結束情境測試，將導致編譯錯誤。

> **注意：** 每個測試應該只有一個情境測試。在同一個測試中建立多個情境測試
> 可能會產生非預期的結果，應該避免這麼做。

```move
use sui::test_scenario;

#[test]
fun test_basic_scenario() {
    let alice = @0xA;

    // 以 alice 作為傳送者開始一個情境測試
    let mut scenario = test_scenario::begin(alice);

    // ... 執行操作 ...

    // 結束情境測試 - 回傳 TransactionEffects
    scenario.end();
}
```

## 交易模擬 (Transaction Simulation) {#transaction-simulation}

使用 `next_tx` 以指定的傳送者推進到新的交易。前一筆交易中轉移的物件，會在下一筆交易中變為可用。每次呼叫 `next_tx` 都會回傳
[`TransactionEffects`](#reading-transaction-effects)，其中包含前一筆交易發生了什麼事的資訊。

```move
use sui::test_scenario;

#[test]
fun test_multi_transaction() {
    let alice = @0xA;
    let bob = @0xB;

    let mut scenario = test_scenario::begin(alice);

    // 第一筆交易：alice 建立一個物件
    // 這裡建立的物件尚未進入任何人的庫存

    // 以 bob 作為傳送者推進到第二筆交易
    // 第一筆交易的物件現在已經可用
    let _effects = scenario.next_tx(bob);

    // ... bob 現在可以存取轉移給他的物件 ...

    scenario.end();
}
```

> 重要事項：在交易期間轉移的物件，只有在呼叫 `next_tx` 之後才會變為可用。
> 你無法在轉移物件的同一筆交易中存取該物件。

## 存取擁有的物件 (Accessing Owned Objects) {#accessing-owned-objects}

[擁有的物件](./../object/ownership.md#account-owner-or-single-owner) 轉移到某個地址後，可以使用 `take_from_sender` 或 `take_from_address`
來存取。接著該物件可以被傳入函式、透過 `return_to_sender` 或 `return_to_address` 回傳，或是使用
`public_transfer`（若該物件具有 `store` 能力）轉移到其他地方。

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

    // 交易 1：建立一個 item 並轉移給 alice
    {
        let item = create(100, scenario.ctx());
        transfer::public_transfer(item, alice);
    };

    // 交易 2：alice 取得該 item
    scenario.next_tx(alice);
    {
        // 從發送者的庫存中取得最新的 Item
        let item = scenario.take_from_sender<Item>();
        assert_eq!(item.value(), 100);

        // 將該 item 歸還到發送者的庫存
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 依 ID 取得物件 (Taking by ID) {#taking-by-id}

當存在多個相同型別的物件時，可以使用 `take_from_sender_by_id` 或
`take_from_address_by_id` 來取得特定的一個：

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
        // 依 ID 取得特定的 item
        let item = scenario.take_from_sender_by_id<Item>(id1);
        assert_eq!(item.value(), 100);
        scenario.return_to_sender(item);
    };

    scenario.end();
}
```

### 檢查物件可用性 (Checking Object Availability) {#checking-object-availability}

在取得物件之前，可以先檢查該物件是否存在：

```move
#[test]
fun test_has_object() {
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 目前尚未存在任何 item
    assert!(!scenario.has_most_recent_for_sender<Item>());

    let item = create(100, scenario.ctx());
    transfer::public_transfer(item, alice);

    scenario.next_tx(alice);

    // 現在已經存在一個 item
    assert!(scenario.has_most_recent_for_sender<Item>());

    scenario.end();
}
```

## 存取共享物件 (Accessing Shared Objects) {#accessing-shared-objects}

[共享物件](./../object/ownership.md#shared-state) 使用 `take_shared` 存取，並且必須用 `return_shared`
歸還：

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

    // Alice 建立一個共享的 counter
    create(scenario.ctx());

    // Bob 將它遞增
    scenario.next_tx(bob);
    {
        let mut counter = scenario.take_shared<Counter>();
        counter.increment();
        assert_eq!(counter.value(), 1);
        test_scenario::return_shared(counter);
    };

    // Alice 再次將它遞增
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

若要讓程式碼更簡潔，可以使用 `with_shared!` 巨集，它會自動處理取用與歸還：

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

[不可變（凍結）物件](./../object/ownership.md#immutable-frozen-state) 是透過
`take_immutable` 存取，並以 `return_immutable` 回傳：

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

    // 建立一個不可變的 config
    create(1000, scenario.ctx());

    scenario.next_tx(alice);
    {
        // 取得不可變物件
        let config = scenario.take_immutable<Config>();
        assert_eq!(config.max_value(), 1000);

        // 將它回傳至全域庫存
        test_scenario::return_immutable(config);
    };

    scenario.end();
}
```

## 存取交易情境 (Accessing Transaction Context) {#accessing-transaction-context}

`ctx` 方法提供對目前交易的 [`TxContext`](./../programmability/transaction-context.md)
的存取。當呼叫需要情境的函式時使用它：

```move
#[test]
fun test_context_access() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 存取交易情境
    let ctx = scenario.ctx();

    // 用於需要情境的操作
    let item = create(100, ctx);
    transfer::public_transfer(item, alice);

    // sender 與傳入 begin() 的值相符
    assert_eq!(ctx.sender(), alice);

    scenario.end();
}
```

## 讀取交易效果 (Reading Transaction Effects) {#reading-transaction-effects}

`next_tx` 與 `end` 都會回傳 `TransactionEffects`，其中包含交易期間發生了什麼事的資訊：

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

    // 檢查建立了什麼
    assert_eq!(effects.created().length(), 2);

    // 檢查轉移到帳戶的情況
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
| `transferred_to_account()` | `VecMap<ID, address>` | 轉移到地址的物件     |
| `transferred_to_object()`  | `VecMap<ID, ID>`      | 轉移到其他物件的物件 |
| `shared()`                 | `vector<ID>`          | 此交易中共享的物件   |
| `frozen()`                 | `vector<ID>`          | 此交易中凍結的物件   |
| `num_user_events()`        | `u64`                 | 發出的事件數量       |

## 系統物件 (System Objects) {#system-objects}

使用 `create_system_objects` 讓 `Clock`、`Random`、`DenyList` 等系統物件在測試中可用。若要更詳細了解如何搭配系統物件進行測試，請參閱
[使用系統物件](./using-system-objects.md)。

```move
use sui::clock::Clock;

#[test]
fun test_with_clock() {
    use std::unit_test::assert_eq;
    use sui::test_scenario;

    let alice = @0xA;
    let mut scenario = test_scenario::begin(alice);

    // 建立系統物件（Clock、Random、DenyList）
    // 此呼叫會推進交易，因此這些物件會立即可用
    scenario.create_system_objects();

    {
        // 現在 Clock 已可作為共享物件使用
        let clock = scenario.take_shared<Clock>();
        assert_eq!(clock.timestamp_ms(), 0);
        test_scenario::return_shared(clock);
    };

    scenario.end();
}
```

## Epoch 與時間操作 (Epoch and Time Manipulation) {#epoch-and-time-manipulation}

使用 `next_epoch` 和 `later_epoch` 測試[與時間相關的邏輯](./../programmability/epoch-and-time.md)：

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

    // 同時前進 epoch 與時間（1000ms = 1 秒）
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

    // 透過 effects 驗證最終狀態 - `return_to_sender` 在最後一筆交易的
    // effects 中會被記錄為轉回給 bob 的轉移
    let effects = scenario.end();
    assert_eq!(effects.transferred_to_account().size(), 1);
}
```

## 總結 (Summary) {#summary}

| 函式                        | 用途                         |
| --------------------------- | ---------------------------- |
| `begin(sender)`             | 開始一個新場景               |
| `end(scenario)`             | 結束場景並取得最終效果       |
| `next_tx(scenario, sender)` | 前進到下一筆交易             |
| `ctx(scenario)`             | 取得 `TxContext` 的可變參照  |
| `take_from_sender<T>`       | 從 sender 取得擁有的物件     |
| `return_to_sender(obj)`     | 將物件回傳給 sender          |
| `take_shared<T>`            | 取得共享物件                 |
| `return_shared(obj)`        | 回傳共享物件                 |
| `take_immutable<T>`         | 取得不可變物件               |
| `return_immutable(obj)`     | 回傳不可變物件               |
| `create_system_objects`     | 建立 Clock、Random、DenyList |
| `next_epoch`                | 前進到下一個 epoch           |
| `later_epoch(ms, sender)`   | 前進 epoch 與時間            |

## 延伸閱讀 (Further Reading) {#further-reading}

- [使用系統物件 (Using System Objects)](./using-system-objects.md) - 在測試中建立與操作 Clock、Random、
  DenyList、Coin 與 Balance
- [測試工具 (Test Utilities)](./test-utilities.md) - `assert_eq!`、`destroy` 及其他測試輔助工具
- [交易情境 (Transaction Context)](./../programmability/transaction-context.md) - 了解 `TxContext` 及
  其欄位
- [物件所有權 (Object Ownership)](./../object/ownership.md) - owned、shared 與 immutable 物件的運作方式
- [Epoch 與時間 (Epoch and Time)](./../programmability/epoch-and-time.md) - 在 Sui 中處理時間
