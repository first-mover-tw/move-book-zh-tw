---
description: 移動測試工具：assert 巨集（macros）、assert_eq、assert_ref_eq，以及用於撰寫易讀單元測試的標準函式庫輔助工具。
---

# 單元測試工具 (Unit Test Utilities) {#unit-test-utilities}

除了內建的 `assert!` 巨集，[標準函式庫](./../move-basics/standard-library.md)也提供了常用的測試工具。其中最重要的定義在 [`std::unit_test`][stdlib-unit-test] 模組中。雖然不是必要條件，但建議在測試中使用這個模組。

## `assert!` {#assert}

`assert!` 巨集是內建的語言功能，也是測試中驗證條件最基本的工具。它接受一個布林運算式，若該運算式求值為 `false` 則會中止。關於斷言與錯誤處理的詳細說明，請參閱[中止執行](./../move-basics/assert-and-abort.md)。

```move
#[test]
fun test_addition() {
    let sum = 2 + 2;
    assert!(sum == 4);
}
```

在發布的程式碼中，`assert!` 通常應該把中止碼作為第二個參數，以協助識別失敗原因。然而，在測試中，中止碼並非必要，也不提供任何價值。

```move
// 在發布的程式碼中 - 建議加上中止碼
assert!(balance >= amount, EInsufficientBalance);

// 在測試程式碼中 - 中止碼非必要
assert!(balance >= amount);
```

## `assert_eq!` 與 `assert_ref_eq!` (`assert_eq!` and `assert_ref_eq!`) {#assert_eq-and-assert_ref_eq}

雖然 `assert!` 可以運作，但它有個限制：當它失敗時，只會顯示條件為 false，而不會提供任何造成失敗的實際數值的資訊。考慮以下測試：

```move
#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert!(balance == 1000); // 失敗時不會印出比較的數值
}
```

如果這個測試失敗了，你只會知道斷言失敗了 —— 而不知道 `balance` 實際上是多少。你需要加上除錯陳述式或進一步調查才能理解失敗原因。

來自 `std::unit_test` 的 `assert_eq!` 巨集透過在斷言失敗時印出兩個值來解決這個問題：

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert_eq!(balance, 1000); // 失敗時印出："Assertion failed:", 750, "!=", 1000
}
```

現在錯誤訊息顯示了實際值 (`750`) 與預期值 (`1000`)，讓問題出在哪裡一目瞭然。這個除錯輸出之所以能運作，是因為 `assert_eq!` 呼叫了 [`std::debug::print`](./../move-basics/standard-library.md) 函式，該函式會在斷言失敗時印出這些值。

若要以參照方式比較，請使用 `assert_ref_eq!` 而非 `assert_eq!`：

```move
#[test_only]
use std::unit_test::assert_ref_eq;

#[test]
fun test_reference_equality() {
    let user = get_user();
    let expected = create_expected_user();
    assert_ref_eq!(&user, &expected);
}
```

## 黑洞函式：`destroy` (Black Hole Function: `destroy`) {#black-hole-function-destroy}

`destroy` 函式會消耗任何值，無論其能力（ability）為何。這對於測試沒有 `drop` 能力的型別而言是必要的 —— 沒有它，清理工作就需要為每個型別額外實作邏輯。

```move
module std::unit_test;

/// 在 `test` 模式下用來銷毀任何值的黑洞函式。
public native fun destroy<T>(v: T);
```

考慮一個沒有 `drop` 的型別：

```move
module book::ticket;

/// 一張票是一個 Object - 沒有 `drop`。
public struct Ticket has key, store {
    id: UID,
    event_id: u64,
    seat: u64,
}

public fun new(event_id: u64, seat: u64, ctx: &mut TxContext): Ticket {
    Ticket { id: object::new(ctx), event_id, seat }
}
```

在發布的程式碼中，`Ticket` 型別可能沒有刪除函式，或者要求在刪除前滿足某個條件。在這種情況下，`destroy` 是處理這個值的最佳方式：

```move
#[test_only]
use std::unit_test;

#[test]
fun test_ticket_creation() {
    let ctx = &mut tx_context::dummy();
    let ticket = ticket::new(1, 42, ctx);

    // 測試通過了 - 但我們要如何處理掉 `ticket`？

    unit_test::destroy(ticket); // 消耗掉這張票
}
```

`destroy` 函式的作用就像個「黑洞」—— 它接受任何型別並讓它消失。這讓你可以專注在測試特定功能上，而不必被迫處理與測試目標無關的清理邏輯。

> `destroy` 函式只在測試程式碼中可用，無法在正式環境的模組中使用。

在接下來的章節中，我們將涵蓋 Sui 特有的測試工具與功能。

[stdlib-unit-test]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/move-stdlib/sources/unit_test.move
