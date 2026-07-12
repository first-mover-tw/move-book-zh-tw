---
description: 撰寫有效 Move 測試的最佳實務 (Best Practices)：簡潔、聚焦且易於維護的測試，能捕捉智慧合約中的真實錯誤。
---

# 什麼是好測試 (What Makes a Good Test) {#what-makes-a-good-test}

撰寫測試是一回事，撰寫_好的_測試又是另一回事。一個只是存在的測試套件，如果沒有真正抓到 bug 或幫助你理解程式碼，只會提供錯誤的安全感。本節涵蓋區分有效測試與表面測試的原則與實務做法。

## 好測試的特徵 (Characteristics of Good Tests) {#characteristics-of-good-tests}

### 1. 測試應該簡潔 (1. Tests Should Be Concise) {#1-tests-should-be-concise}

每個測試都應該簡潔且切中要點。避免寫過長且複雜的測試。讓測試保持簡短，並專注於單一行為或情境。

### 2. 測試應該易讀 (2. Tests Should Be Readable) {#2-tests-should-be-readable}

測試作為程式碼預期行為的文件。任何閱讀測試的人都應該能快速理解測試的是什麼情境，以及預期的結果是什麼。

> **注意：** 讓過長函式呼叫更易讀的其中一個保證有效的方法，就是使用本章稍後會介紹的
> [Builder Pattern](./builder-pattern.md)。

```move
module book::readable_tests;

public struct Balance has copy, drop { value: u64 }

public fun new(value: u64): Balance { Balance { value } }
public fun add(balance: &mut Balance, amount: u64) { balance.value = balance.value + amount; }
public fun value(balance: &Balance): u64 { balance.value }

#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_add_increases_balance_by_specified_amount() {
    // Arrange：設定初始狀態
    let mut balance = new(100);

    // Act：執行被測試的操作
    balance.add(50);

    // Assert：驗證預期的結果
    assert_eq!(balance.value(), 150);
}
```

### 3. 測試應該只測一件事 (3. Tests Should Test One Thing) {#3-tests-should-test-one-thing}

每個測試都應該驗證單一行為或情境。當一個測試失敗時，你應該能立即知道哪裡出錯了。驗證多個不相關行為的測試會讓除錯更困難。

```move
module book::single_responsibility;

public struct Counter has copy, drop { value: u64 }

public fun increment(c: &mut Counter) { c.value = c.value + 1; }
public fun decrement(c: &mut Counter) { c.value = c.value - 1; }

#[test_only]
use std::unit_test::assert_eq;

// Good：為每個行為分別寫測試
#[test]
fun test_increment_adds_one() {
    let mut counter = Counter { value: 0 };
    counter.increment();
    assert_eq!(counter.value, 1);
}

#[test]
fun test_decrement_subtracts_one() {
    let mut counter = Counter { value: 1 };
    counter.decrement();
    assert_eq!(counter.value, 0);
}
```

## 要測試什麼 (What to Test) {#what-to-test}

### 測試合約，而非實作 (Test the Contract, Not the Implementation) {#test-the-contract-not-the-implementation}

專注於測試函式的可觀察行為——它們回傳什麼、產生什麼副作用——而不是它們內部如何達成。這讓你能夠重構實作而不破壞測試。

### 測試邊界情況 (Test Edge Cases) {#test-edge-cases}

邊界情況通常是 bug 藏身之處。對於數值運算，請考慮：

- 零值
- 最大值（`std::u64::max_value!()`、`std::u128::max_value!()`）
- 邊界條件（差一錯誤）
- 空集合

```move
module book::edge_cases;

public fun safe_divide(a: u64, b: u64): u64 {
    if (b == 0) return 0;
    a / b
}

#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_divide_normal_case() {
    assert_eq!(safe_divide(10, 2), 5);
}

#[test]
fun test_divide_by_zero_returns_zero() {
    assert_eq!(safe_divide(10, 0), 0);
}

#[test]
fun test_divide_zero_by_nonzero() {
    assert_eq!(safe_divide(0, 5), 0);
}
```

### 測試錯誤條件 (Test Error Conditions) {#test-error-conditions}

驗證你的程式碼在收到無效輸入時能正確失敗。使用 `#[expected_failure]` 來測試函式是否以正確的錯誤碼中止。在期望值中使用明確的錯誤常數，不要使用魔術數字。

```move
module book::error_conditions;

const EInsufficientBalance: u64 = 1;

public struct Wallet has copy, drop { balance: u64 }

public fun withdraw(wallet: &mut Wallet, amount: u64) {
    assert!(wallet.balance >= amount, EInsufficientBalance);
    wallet.balance = wallet.balance - amount;
}

#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_withdraw_succeeds_with_sufficient_balance() {
    let mut wallet = Wallet { balance: 100 };
    wallet.withdraw(50);
    assert_eq!(wallet.balance, 50);
}

#[test, expected_failure(abort_code = EInsufficientBalance)]
fun test_withdraw_fails_with_insufficient_balance() {
    let mut wallet = Wallet { balance: 50 };
    wallet.withdraw(100);
}
```

### 追求良好覆蓋率，但不要追逐數字 (Aim for Good Coverage, but Don't Chase Numbers) {#aim-for-good-coverage-but-dont-chase-numbers}

高測試覆蓋率是一個正向指標——這表示更多程式碼在測試中被執行，增加抓到 bug 的機會。達到良好的覆蓋率也顯示你已經思考過各種程式碼路徑與情境。

然而，覆蓋率不應該是撰寫測試的主要目標。一個覆蓋率 100% 的測試套件，如果測試沒有驗證有意義的行為，仍然可能漏掉關鍵 bug。純粹為了提升覆蓋率指標而存在、卻沒有斷言任何有用內容的測試，只會提供錯誤的安全感。

撰寫測試是為了驗證行為並抓到 bug。良好的覆蓋率應該是徹底測試的自然結果，而不是目的本身。若想了解更多關於測量與解讀覆蓋率的資訊，請參閱
[覆蓋率報告 (Coverage Reports)](./coverage.md)。

## 測試組織 (Test Organization) {#test-organization}

### 使用具描述性的名稱 (Use Descriptive Names) {#use-descriptive-names}

測試名稱應該描述被測試的情境以及預期的結果。一個好的命名慣例是 `test_<function>_<scenario>_<expected_result>`，或者就直接描述行為。無論你使用哪種命名慣例，都應該保持一致且容易理解。

### 將相關測試分組 (Group Related Tests) {#group-related-tests}

依照被測試的函式或所驗證的功能，有邏輯地組織測試。在 Move 中，你可以將測試放在與被測程式碼相同的模組中，或放在獨立的測試模組中。非常常見的做法是在 `tests/` 目錄中，為 `sources/` 目錄中的每個模組建立一個 `*_tests.move` 測試模組。

## 測試金字塔 (The Testing Pyramid) {#the-testing-pyramid}

一個平衡良好的測試套件通常遵循測試金字塔：

1. **單元測試 (Unit tests)**（底層）：許多小型、快速的測試，各自獨立驗證單一函式
2. **整合測試 (Integration tests)**（中層）：較少的測試，驗證元件之間如何協同運作
3. **端對端測試 (End-to-end tests)**（頂層）：極少的測試，驗證完整的使用者情境

目前，在 Move 中所有測試都是以單元測試的形式實作，但透過使用
[測試情境 (Test Scenario)](./test-scenario.md)，你可以在單一測試中測試多筆交易與使用者操作。

## 常見的測試錯誤 (Common Testing Mistakes) {#common-testing-mistakes}

### 只測試快樂路徑 (Testing Only the Happy Path) {#testing-only-the-happy-path}

不要只測試程式碼在一切順利時能正常運作。也要測試出錯時會發生什麼——無效輸入、邊界情況與錯誤條件。

### 過度模擬 (Over-Mocking) {#over-mocking}

雖然隔離性很重要，但過度模擬可能導致測試在真實整合會失敗的情況下依然通過。要在單元測試與使用真實元件的整合測試之間取得平衡。

### 忽視測試維護 (Ignoring Test Maintenance) {#ignoring-test-maintenance}

測試也是程式碼。保持測試乾淨，移除過時的測試，並在需求變更時更新它們。一個被忽視的測試套件會變成負債，而不是資產。
