---
description: "Move 測試工具：斷言巨集、assert_eq、assert_ref_eq，以及標準函式庫提供的輔助函式，用於撰寫表達力強的單元測試。"
---

# 單元測試工具 (Unit Test Utilities)

除了內建的 `assert!` 巨集，[標準函式庫](./../move-basics/standard-library.md)提供了常見的測試工具。最重要的定義在 [`std::unit_test`][stdlib-unit-test] 模組中。雖然不是必要的，但建議在測試中使用此模組。

## `assert!`

`assert!` 巨集是內建的語言功能，是驗證測試條件的最基本工具。它接受一個布林運算式，當運算式的值為 `false` 時會中止執行。如需詳細說明斷言和錯誤處理，請參閱 [中止執行](./../move-basics/assert-and-abort.md)。

```move
#[test]
fun test_addition() {
    let sum = 2 + 2;
    assert!(sum == 4);
}
```

在正式程式碼中，`assert!` 通常應該在第二個引數中包含中止程式碼以幫助識別失敗。但在測試中，中止程式碼不是必要的，也不會提供任何值。

```move
// 在正式程式碼中 - 需要中止程式碼
assert!(balance >= amount, EInsufficientBalance);

// 在測試程式碼中 - 中止程式碼為可選
assert!(balance >= amount);
```

## `assert_eq!` 和 `assert_ref_eq!`

雖然 `assert!` 有效，但它有一個限制：失敗時，它只顯示條件為假，不會洞察導致失敗的實際值。考慮這個測試：

```move
#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert!(balance == 1000); // 失敗時不會列印比較的值
}
```

如果此測試失敗，你只知道斷言失敗 - 不知道 `balance` 實際上是什麼。你需要新增除錯陳述式或進一步調查才能理解失敗原因。

來自 `std::unit_test` 的 `assert_eq!` 巨集解決了這個問題，它在斷言失敗時會列印兩個值：

```move
use std::unit_test::assert_eq;

#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert_eq!(balance, 1000); // 失敗時顯示："Assertion failed: 750 != 1000"
}
```

現在錯誤訊息顯示實際值 (`750`) 和預期值 (`1000`)，清楚地說明了出了什麼問題。這個除錯輸出有效是因為 `assert_eq!` 呼叫了 [`std::debug::print`](./../move-basics/standard-library.md) 函式，如果斷言失敗它會列印這些值。

若要透過參考進行比較，請使用 `assert_ref_eq!` 而不是 `assert_eq!`：

```move
use std::unit_test::assert_ref_eq;

#[test]
fun test_reference_equality() {
    let user = get_user();
    let expected = create_expected_user();
    assert_ref_eq!(&user, &expected);
}
```

## 黑洞函式：`destroy`

`destroy` 函式消費任何值，無論其具有什麼能力。這對於測試沒有 `drop` 能力的型別是必不可少的 - 沒有它，清理將需要為每個型別實現額外的邏輯。

```move
module std::unit_test;

/// 消費任何值 `T` 並使其消失。
public native fun destroy<T>(v: T);
```

考慮一個沒有 `drop` 的型別：

```move
module book::ticket;

/// 票是一個物件 - 沒有 `drop`。
public struct Ticket has key, store {
    id: UID,
    event_id: u64,
    seat: u64,
}

public fun new(event_id: u64, seat: u64, ctx: &mut TxContext): Ticket {
    Ticket { id: object::new(ctx), event_id, seat }
}
```

在正式程式碼中，`Ticket` 型別可能沒有刪除函式或需要在刪除前滿足某個條件。在這種情況下，`destroy` 是處理該值的最佳方式：

```move
use std::unit_test;

#[test]
fun test_ticket_creation() {
    let ctx = &mut tx_context::dummy();
    let ticket = ticket::new(1, 42, ctx);

    // 測試通過 - 但我們如何擺脫 `ticket`？

    unit_test::destroy(ticket); // 消費票
}
```

`destroy` 函式充當「黑洞」- 它接受任何型別並使其消失。這讓你可以專注於測試特定功能，而不被迫處理與你測試內容無關的清理邏輯。

> `destroy` 函式只在測試程式碼中可用。它不能在正式模組中使用。

在接下來的章節中，我們將涵蓋 Sui 特定的測試工具和功能。

[stdlib-unit-test]:
  https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/move-stdlib/sources/unit_test.move
