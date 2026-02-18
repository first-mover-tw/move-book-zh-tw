---
description: "Move 測試工具：assert 巨集、assert_eq、assert_ref_eq 以及用於撰寫表達性單元測試的標準函式庫輔助工具。"
---

# 單元測試工具 (Unit Test Utilities)

除了內建的 `assert!` 巨集外，[標準函式庫 (Standard Library)](./../move-basics/standard-library.md) 提供了常用的測試工具。其中最重要的是定義在 [`std::unit_test`][stdlib-unit-test] 模組中。雖然不是必須的，但建議在測試中使用此模組。

## `assert!`

`assert!` 巨集是內建的語言功能，也是驗證測試條件最基本的工具。它接受一個布林表達式，如果表達式計算結果為 `false`，則中止執行。關於斷言和錯誤處理的詳細解釋，請參見 [中止執行 (Aborting Execution)](./../move-basics/assert-and-abort.md)。

```move
#[test]
fun test_addition() {
    let sum = 2 + 2;
    assert!(sum == 4);
}
```

在已發布的程式碼中，`assert!` 通常應該有第二個參數作為中止代碼，以幫助識別失敗原因。然而，在測試中，中止代碼並非必要，也不提供任何價值。

```move
// 在發布的程式碼中 - 需要中止代碼
assert!(balance >= amount, EInsufficientBalance);

// 在測試程式碼中 - 中止代碼可選
assert!(balance >= amount);
```

## `assert_eq!` 和 `assert_ref_eq!` {#assert_eq-and-assert_ref_eq}

雖然 `assert!` 可以工作，但它有一個限制：當它失敗時，它只顯示條件為假，而不會給出導致失敗的實際數值。考慮這個測試：

```move
#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert!(balance == 1000); // 失敗時不列印出比較值
}
```

如果這個測試失敗，你只知道斷言失敗了 —— 不知道 `balance` 實際是多少。你需要添加除錯語句或進一步調查才能理解失敗原因。

`std::unit_test` 中的 `assert_eq!` 巨集解決了這個問題，當斷言失敗時，它會列印出兩個值：

```move
use std::unit_test::assert_eq;

#[test]
fun test_balance_update() {
    let balance = calculate_balance();
    assert_eq!(balance, 1000); // 失敗時顯示: "Assertion failed: 750 != 1000"
}
```

現在錯誤訊息顯示了實際值 (`750`) 和預期值 (`1000`)，讓人一眼就能看出出了什麼錯。這個除錯輸出之所以有效，是因為 `assert_eq!` 調用了 [`std::debug::print`](./../move-basics/standard-library.md) 函式，該函式會在斷言失敗時列印數值。

若要透過引用 (reference) 進行比較，請使用 `assert_ref_eq!` 而不是 `assert_eq!`：

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

`destroy` (銷毀) 函式可以消耗任何值，無論它具有什麼能力 (abilities)。這對於測試沒有 `drop` 能力的型別至關重要 —— 如果沒有它，清理工作將需要為每個型別實作額外的邏輯。

```move
module std::unit_test;

/// 消耗任何值 `T` 並使其消失。
public native fun destroy<T>(v: T);
```

考慮一個沒有 `drop` 的型別：

```move
module book::ticket;

/// Ticket 是一個 Object - 沒有 `drop` 能力。
public struct Ticket has key, store {
    id: UID,
    event_id: u64,
    seat: u64,
}

public fun new(event_id: u64, seat: u64, ctx: &mut TxContext): Ticket {
    Ticket { id: object::new(ctx), event_id, seat }
}
```

在已發布的程式碼中，`Ticket` 型別可能沒有刪除函式，或者要求在刪除前滿足特定條件。在這種情況下，`destroy` 是處理該值的最佳方式：

```move
use std::unit_test;

#[test]
fun test_ticket_creation() {
    let ctx = &mut tx_context::dummy();
    let ticket = ticket::new(1, 42, ctx);

    // 測試通過 - 但我們如何處理 `ticket` 呢？

    unit_test::destroy(ticket); // 消耗掉 ticket
}
```

`destroy` 函式就像一個「黑洞」—— 它接受任何型別並使其消失。這讓你能夠將測試專注於特定功能，而不必被迫處理與測試內容無關的清理邏輯。

> `destroy` 函式僅在測試程式碼中可用。它不能在生產模組中使用。

在接下來的章節中，我們將介紹 Sui 特定的測試工具和功能。

[stdlib-unit-test]:
  https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/move-stdlib/sources/unit_test.move
