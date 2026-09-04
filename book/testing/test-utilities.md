---
description: Move 測試工具 (Move test utilities)：用於撰寫具表達力單元測試的斷言巨集 (assert macros)、assert_eq、assert_ref_eq 與標準函式庫輔助工具。
title: 單元測試公用程式 (Unit Test Utilities)
keywords:
  - Move
  - Sui
  - Move tutorial
  - unit
  - test
  - utilities
  - testing
questions:
  - What is Unit Test Utilities in Move?
  - How do I use Unit Test Utilities in Move?
  - What is assert! in Move?
  - What is assert_eq! and assert_ref_eq! in Move?
answer: 'Move test utilities: assert macros, assert_eq, assert_ref_eq, and standard library helpers for writing expressive unit tests.'
goal:
  description: 'Reader understands move test utilities: assert macros, assert_eq, assert_ref_eq, and standard library helpers for writing expressive unit tests'
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

# 單元測試工具 (Unit Test Utilities) {#unit-test-utilities}

除了內建的 `assert!` 巨集外，[標準函式庫](./../move-basics/standard-library.md)也提供常用的測試工具。最重要的工具定義於 [`std::unit_test`][stdlib-unit-test] 模組中。雖非必要條件，但建議在測試中使用此模組。

## 斷言巨集 (`assert!`) {#assert}

`assert!` 巨集是內建語言功能，也是驗證測試條件最基本的工具。它接受一個布林運算式，若運算式評估為 `false` 即中止。關於斷言與錯誤處理的詳細說明，請參閱[中止執行](./../move-basics/assert-and-abort.md)。

```move
#[test]
fun test_addition() {
    let sum = 2 + 2;
    assert!(sum == 4);
}
```

在已發布的原始碼中，`assert!` 通常應將中止碼作為第二個引數，以協助識別失敗原因。不過在測試中，中止碼並非必要，也不提供任何價值。

```move
// 在已發布的原始碼中——建議使用中止碼
assert!(balance >= amount, EInsufficientBalance);

// 在測試原始碼中——不需要中止碼
assert!(balance >= amount);
```

## 相等斷言巨集與參考相等斷言巨集 (`assert_eq!` and `assert_ref_eq!`) {#assert_eq-and-assert_ref_eq}

雖然 `assert!` 可用，但有一項限制：當它失敗時，只會顯示條件為 false，無法了解導致失敗的實際值。請考慮以下測試：

```move
#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert!(balance == 1000); // 失敗時不會印出比較的值
}
```

若此測試失敗，你只知道斷言失敗，卻不知道 `balance` 的實際值。你需要加入偵錯陳述式或進一步調查，才能理解失敗原因。

`std::unit_test` 中的 `assert_eq!` 巨集會在斷言失敗時印出兩個值，藉此解決此問題：

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert_eq!(balance, 1000); // 失敗時印出："Assertion failed:", 750, "!=", 1000
}
```

現在錯誤訊息會顯示實際值（`750`）與預期值（`1000`），讓問題所在一目了然。此偵錯輸出之所以可行，是因為 `assert_eq!` 會呼叫 [`std::debug::print`](./../move-basics/standard-library.md) 函式，並在斷言失敗時印出值。

若要依參考比較，請使用 `assert_ref_eq!`，而非 `assert_eq!`：

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

`destroy` 函式會消耗任何值，無論其具備哪些能力。這對測試不具備 `drop` 能力的型別至關重要；若沒有它，清理作業將需要為每個型別實作額外邏輯。

```move
module std::unit_test;

/// 在 `test` 模式中銷毀任何值的黑洞函式。
public native fun destroy<T>(v: T);
```

請考慮一個不具備 `drop` 的型別：

```move
module book::ticket;

/// 票券是 Object——不具備 `drop`。
public struct Ticket has key, store {
    id: UID,
    event_id: u64,
    seat: u64,
}

public fun new(event_id: u64, seat: u64, ctx: &mut TxContext): Ticket {
    Ticket { id: object::new(ctx), event_id, seat }
}
```

在已發布的原始碼中，`Ticket` 型別可能沒有刪除函式，或要求在刪除前滿足某項條件。在此情況下，`destroy` 是處理該值的最佳方式：

```move
#[test_only]
use std::unit_test;

#[test]
fun test_ticket_creation() {
    let ctx = &mut tx_context::dummy();
    let ticket = ticket::new(1, 42, ctx);

    // 測試通過——但要如何處理 `ticket`？

    unit_test::destroy(ticket); // 消耗票券
}
```

`destroy` 函式的作用如同「黑洞」：它接受任何型別並使其消失。這讓你能將測試聚焦於特定功能，而不必處理與測試目標無關的清理邏輯。

> `destroy` 函式僅適用於測試原始碼，無法在正式環境模組中使用。

下一節將介紹 Sui 專用的測試工具與功能。

[stdlib-unit-test]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/move-stdlib/sources/unit_test.move
