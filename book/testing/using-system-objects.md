---
description: 在 Move 測試中使用系統物件（system objects）：建立並操作 Clock、Random 和 DenyList，以測試時間、隨機性和拒絕清單。
---

# 在測試中建立與使用系統物件 (Creating and Using System Objects in Tests) {#creating-and-using-system-objects-in-tests}

有些測試需要 `Clock`、`Random` 或 `DenyList` 等系統物件。這些物件在網路上有
[固定地址](./../appendix/reserved-addresses.md)，並且在創世（genesis）時建立。在測試中，它們預設不存在，因此 Sui Framework 提供了 `#[test_only]` 函式來建立與操作這些物件。

## 時鐘 (Clock) {#clock}

[`Clock`](./../programmability/epoch-and-time.md#time) 提供目前的網路時間戳記。
使用 `clock::create_for_testing` 建立一個，並用 test-only 函式操作時間：

```move
use std::unit_test::assert_eq;
use sui::clock;

#[test]
fun test_clock() {
    let ctx = &mut tx_context::dummy();
    let mut clock = clock::create_for_testing(ctx);

    // 從 0 開始
    assert_eq!(clock.timestamp_ms(), 0);

    // 增加時間（以毫秒為單位）
    clock.increment_for_testing(1000);
    assert_eq!(clock.timestamp_ms(), 1000);

    // 設定絕對時間（必須 >= 目前時間）
    clock.set_for_testing(5000);
    assert_eq!(clock.timestamp_ms(), 5000);

    // 清理 - Clock 沒有 `drop`
    clock.destroy_for_testing();
}
```

若要在測試情境中共享 `Clock` 以供使用，呼叫 `share_for_testing`：

```move
#[test]
fun test_shared_clock() {
    let ctx = &mut tx_context::dummy();
    let clock = clock::create_for_testing(ctx);
    clock.share_for_testing();
}
```

## Random 隨機性 (Random) {#random}

`Random` 物件提供鏈上隨機性。在測試中，完整的 `Random` 共享物件只能透過 `random::create_for_testing` 在[測試情境](./test-scenario.md)中建立。然而，較好的做法是將程式碼結構設計成核心邏輯接收 `RandomGenerator` 參數——這樣就能在單元測試中直接用 `random::new_generator_for_testing()` 建立 generator，完全繞過 `Random` 物件。這種方式比較好處理，因為 `Random` 需要 `entry` 函式（無法回傳不可丟棄的值），使得斷言結果變得困難。

```move
use sui::random::{Self, Random, RandomGenerator};

// 若要使用 Random，函式必須有 `entry` 修飾詞，因此無法回傳
// 值，也不容易測試。
entry fun my_entry_function(r: &Random, ctx: &mut TxContext) {
    let mut gen = random::new_generator(r, ctx);
    let result = inner_function(&mut gen);
    result.destroy_or!(abort);
}

// 內部函式的範例，比進入點更容易測試。
public(package) fun inner_function(gen: &mut RandomGenerator): Option<u64> {
    if (gen.generate_bool()) {
        option::some(gen.generate_u64())
    } else {
        option::none()
    }
}

#[test]
fun test_simple_random() {
    // 非決定性種子，適合用於 fuzzing。每次執行結果都不同，
    // 所以不要斷言特定結果。
    let mut gen = random::new_generator_for_testing();
    let _result = inner_function(&mut gen);

    // 決定性（相同種子可重現）
    let seed: vector<u8> = "Arbitrary seed bytes";
    let mut gen = random::new_generator_from_seed_for_testing(seed);
    assert!(inner_function(&mut gen).is_none());

    // 不同的種子會得到不同——但仍可重現——的結果
    let mut gen = random::new_generator_from_seed_for_testing("move book");
    assert!(inner_function(&mut gen).is_some());
}
```

對於接收完整 `Random` 共享物件的進入點（唯一可能的方式是以參考 `&Random` 傳入），請使用[測試情境](./test-scenario.md)：

```move
use sui::random::{Self, Random};
use sui::test_scenario;

#[test]
fun test_random_shared() {
    let mut scenario = test_scenario::begin(@0x0);

    // 建立並共享 Random
    random::create_for_testing(scenario.ctx());
    scenario.next_tx(@0x0);

    let mut random = scenario.take_shared<Random>();

    // 以 32 位元組的隨機性初始化（使用前必須執行）
    random.update_randomness_state_for_testing(
        0,
        x"2020202020202020202020202020202020202020202020202020202020202020",
        scenario.ctx(),
    );

    my_entry_function(&random, scenario.ctx());

    test_scenario::return_shared(random);
    scenario.end();
}
```

## 拒絕清單 (DenyList) {#denylist}

`DenyList` 用於受監管的代幣，以封鎖特定地址。可用 `new_for_testing` 建立本地實例，或用 `create_for_testing` 建立共享實例：

```move
use sui::deny_list;
use sui::test_scenario;
use std::unit_test::destroy;

#[test]
fun test_deny_list() {
    let mut scenario = test_scenario::begin(@0x0);

    // 建立本地實例以進行簡單測試
    let deny_list = deny_list::new_for_testing(scenario.ctx());
    // ... 使用 deny_list
    destroy(deny_list);

    // 或建立共享的 DenyList
    deny_list::create_for_testing(scenario.ctx());
    scenario.next_tx(@0x0);
    // ... take_shared 並使用

    scenario.end();
}
```

## Coin 與 Balance (Coin and Balance) {#coin-and-balance}

如需測試 coin，請使用 `coin::mint_for_testing` 與 `balance::create_for_testing`：

```move
use std::unit_test::assert_eq;
use sui::coin;
use sui::balance;
use sui::sui::SUI;

#[test]
fun test_coins() {
    let ctx = &mut tx_context::dummy();

    // 建立任意型別的 coin
    let coin = coin::mint_for_testing<SUI>(1000, ctx);
    assert_eq!(coin.value(), 1000);

    // 銷毀並取回數值
    let value = coin.burn_for_testing();
    assert_eq!(value, 1000);

    // 直接建立 balance
    let balance = balance::create_for_testing<SUI>(500);
    let value = balance.destroy_for_testing();
    assert_eq!(value, 500);
}
```

## 一次建立所有系統物件 (Create All System Objects at Once) {#create-all-system-objects-at-once}

使用 [Test Scenario](./test-scenario.md) 時，你可以用 `create_system_objects` 一次建立所有系統物件。這會建立並共享 `Clock`、`Random` 與 `DenyList`：

```move
use sui::clock::Clock;
use sui::random::Random;
use sui::deny_list::DenyList;
use sui::test_scenario;

#[test]
fun test_with_all_system_objects() {
    let mut scenario = test_scenario::begin(@0xA);

    // 以共享物件的形式建立 Clock、Random 與 DenyList
    // （會推進交易，所以它們會立即可用）
    scenario.create_system_objects();

    // 依型別取得物件
    let clock = scenario.take_shared<Clock>();
    let random = scenario.take_shared<Random>();
    let deny_list = scenario.take_shared<DenyList>();

    // ... 使用這些物件

    // 使用完畢後歸還
    test_scenario::return_shared(clock);
    test_scenario::return_shared(random);
    test_scenario::return_shared(deny_list);

    scenario.end();
}
```

> 在測試中建立的系統物件不會有在正式網路上那種固定地址。
> 請使用 `take_shared<T>()` 依型別存取它們，而不是依 ID。

若要依 ID 取得特定的共享物件，請使用 `take_shared_by_id`：

```move
use sui::test_scenario::{Self, most_recent_id_shared};

#[test]
fun test_take_by_id() {
    let mut scenario = test_scenario::begin(@0xA);
    scenario.create_system_objects();

    // 取得最近一次共享的 Clock 的 ID
    let clock_id = most_recent_id_shared<Clock>().destroy_some();

    // 依 ID 取得
    let clock = scenario.take_shared_by_id<Clock>(clock_id);
    // ...
    test_scenario::return_shared(clock);

    scenario.end();
}
```

## 總結 (Summary) {#summary}

| 物件              | 建立方式                                | 僅供測試使用的功能                         |
| ----------------- | --------------------------------------- | ------------------------------------------ |
| `Clock`           | `clock::create_for_testing(ctx)`        | `increment_for_testing`, `set_for_testing` |
| `Random`          | `random::create_for_testing(ctx)`       | `update_randomness_state_for_testing`      |
| `RandomGenerator` | `random::new_generator_for_testing()`   | `new_generator_from_seed_for_testing`      |
| `DenyList`        | `deny_list::create_for_testing(ctx)`    | `new_for_testing`                          |
| `Coin<T>`         | `coin::mint_for_testing<T>(value, ctx)` | `burn_for_testing`                         |
| `Balance<T>`      | `balance::create_for_testing<T>(value)` | `destroy_for_testing`                      |
| 所有系統物件      | `scenario.create_system_objects()`      | 建立 Clock、Random、DenyList               |
