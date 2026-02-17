---
description: "在 Move 測試中使用系統物件：建立和操作 Clock、Random 和 DenyList 以測試時間、隨機性和拒絕列表。"
---

# 在測試中建立和使用系統物件 (Creating and Using System Objects in Tests)

有些測試需要像 `Clock`、`Random` 或 `DenyList` 這樣的系統物件。這些物件在網路上具有[固定地址](./../appendix/reserved-addresses.md)並且是在創世期間建立的。在測試中，它們預設不存在，因此 Sui Framework 提供了 `#[test_only]` 函式來建立和操作它們。

## Clock (時鐘)

[`Clock`](./../programmability/epoch-and-time.md#clock) 提供當前網路時間戳記。使用 `clock::create_for_testing` 建立一個，並使用測試專用函式操作時間：

```move
use std::unit_test::assert_eq;
use sui::clock;

#[test]
fun test_clock() {
    let ctx = &mut tx_context::dummy();
    let mut clock = clock::create_for_testing(ctx);

    // 從 0 開始
    assert_eq!(clock.timestamp_ms(), 0);

    // 增加時間 (毫秒)
    clock.increment_for_testing(1000);
    assert_eq!(clock.timestamp_ms(), 1000);

    // 設定絕對時間 (必須 >= 當前時間)
    clock.set_for_testing(5000);
    assert_eq!(clock.timestamp_ms(), 5000);

    // 清理 - Clock 沒有 `drop` 能力
    clock.destroy_for_testing();
}
```

要在測試場景中共享 `Clock` 以供使用，請調用 `share_for_testing`：

```move
#[test]
fun test_shared_clock() {
    let ctx = &mut tx_context::dummy();
    let clock = clock::create_for_testing(ctx);
    clock.share_for_testing();
}
```

## Random (隨機數)

`Random` 物件提供鏈上隨機性。在測試中，完整的 `Random` 共享物件只能在[測試場景](./test-scenario.md)內部透過 `random::create_for_testing` 建立。然而，首選的方法是結構化你的程式碼，讓核心邏輯接受 `RandomGenerator` 參數 —— 這讓你可以使用 `random::new_generator_for_testing()` 直接在單元測試中建立生成器，完全繞過 `Random` 物件。這更容易使用，因為 `Random` 需要 `entry` 函式 (無法回傳非 drop 值)，這使得斷言結果變得更加困難。

```move
use sui::random::{Self, Random, RandomGenerator};

// 要使用 Random，函式必須有 `entry` 修飾符，因此它無法回傳值，
// 且不易測試。
entry fun my_entry_function(r: &Random, ctx: &mut TxContext) {
    let mut gen = random::new_generator(r, ctx);
    let result = inner_function(&mut gen);
    result.destroy_or!(abort);
}

// 內部函式的範例，比進入點 (entry point) 更容易測試。
public(package) fun inner_function(gen: &mut RandomGenerator): Option<u64> {
    if (gen.generate_bool()) {
        option::some(gen.generate_u64())
    } else {
        option::none()
    }
}

#[test]
fun test_simple_random() {
    // 確定性，總是相同的值。
    let mut gen = random::new_generator_for_testing();
    assert!(inner_function(&mut gen).is_none());

    // 確定性 (使用相同種子可重現)
    let seed = b"Arbitrary seed bytes";
    let mut gen = random::new_generator_from_seed_for_testing(seed);
    assert!(inner_function(&mut gen).is_some());
}
```

對於接受完整 `Random` 共享物件的進入點 (唯一可能的方法是將其作為引用 `&Random` 接收)，請使用[測試場景](./test-scenario.md)：

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

    // 使用種子位元組初始化 (使用前必需)
    random.update_randomness_state_for_testing(
        0,
        x"1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F1F",
        scenario.ctx(),
    );

    my_entry_function(&random, scenario.ctx());

    test_scenario::return_shared(random);
    scenario.end();
}
```

## DenyList (拒絕列表)

`DenyList` 用於受監管的代幣以封鎖特定地址。使用 `new_for_testing` 建立本地實例，或使用 `create_for_testing` 建立共享實例：

```move
use sui::deny_list;
use sui::test_scenario;
use std::unit_test::destroy;

#[test]
fun test_deny_list() {
    let mut scenario = test_scenario::begin(@0x0);

    // 為簡單測試建立本地實例
    let deny_list = deny_list::new_for_testing(scenario.ctx());
    // ... 使用 deny_list
    destroy(deny_list);

    // 或者建立共享 DenyList
    deny_list::create_for_testing(scenario.ctx());
    scenario.next_tx(@0x0);
    // ... take_shared 並使用

    scenario.end();
}
```

## Coin 和 Balance

要使用代幣進行測試，請使用 `coin::mint_for_testing` 和 `balance::create_for_testing`：

```move
use std::unit_test::assert_eq;
use sui::coin;
use sui::balance;
use sui::sui::SUI;

#[test]
fun test_coins() {
    let ctx = &mut tx_context::dummy();

    // 建立任何型別的代幣
    let coin = coin::mint_for_testing<SUI>(1000, ctx);
    assert_eq!(coin.value(), 1000);

    // 銷毀並取回值
    let value = coin.burn_for_testing();
    assert_eq!(value, 1000);

    // 直接建立餘額
    let balance = balance::create_for_testing<SUI>(500);
    let value = balance.destroy_for_testing();
    assert_eq!(value, 500);
}
```

## 一次建立所有系統物件

使用 [測試場景](./test-scenario.md) 時，可以使用 `create_system_objects` 一次建立所有系統物件。這將建立並共享 `Clock`、`Random` 和 `DenyList`：

```move
use sui::clock::Clock;
use sui::random::Random;
use sui::deny_list::DenyList;
use sui::test_scenario;

#[test]
fun test_with_all_system_objects() {
    let mut scenario = test_scenario::begin(@0xA);

    // 建立 Clock, Random 和 DenyList 作為共享物件
    scenario.create_system_objects();
    scenario.next_tx(@0xA);

    // 根據型別取出物件
    let clock = scenario.take_shared<Clock>();
    let random = scenario.take_shared<Random>();
    let deny_list = scenario.take_shared<DenyList>();

    // ... 使用物件

    // 完成後歸還它們
    test_scenario::return_shared(clock);
    test_scenario::return_shared(random);
    test_scenario::return_shared(deny_list);

    scenario.end();
}
```

> 在測試中建立的系統物件不會擁有它們在即時網路上具備的固定地址。使用 `take_shared<T>()` 按型別而不是按 ID 來存取它們。

要透過 ID 取出特定的共享物件，請使用 `take_shared_by_id`：

```move
use sui::test_scenario::{Self, most_recent_id_shared};

#[test]
fun test_take_by_id() {
    let mut scenario = test_scenario::begin(@0xA);
    scenario.create_system_objects();
    scenario.next_tx(@0xA);

    // 獲取最近共享 Clock 的 ID
    let clock_id = most_recent_id_shared<Clock>().destroy_some();

    // 透過 ID 取出
    let clock = scenario.take_shared_by_id<Clock>(clock_id);
    // ...
    test_scenario::return_shared(clock);

    scenario.end();
}
```

## 總結

| 物件 | 建立方式 | 測試專用功能 |
| ------------------ | --------------------------------------- | ------------------------------------------ |
| `Clock` | `clock::create_for_testing(ctx)` | `increment_for_testing`, `set_for_testing` |
| `Random` | `random::create_for_testing(ctx)` | `update_randomness_state_for_testing` |
| `RandomGenerator` | `random::new_generator_for_testing()` | `new_generator_from_seed_for_testing` |
| `DenyList` | `deny_list::create_for_testing(ctx)` | `new_for_testing` |
| `Coin<T>` | `coin::mint_for_testing<T>(value, ctx)` | `burn_for_testing` |
| `Balance<T>` | `balance::create_for_testing<T>(value)` | `destroy_for_testing` |
| 所有系統物件 | `scenario.create_system_objects()` | 建立 Clock, Random, DenyList |
