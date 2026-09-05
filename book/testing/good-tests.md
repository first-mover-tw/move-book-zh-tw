---
description: 編寫有效 Move 測試的最佳實務：簡潔、聚焦且易於維護的測試，可捕捉智慧合約中的實際錯誤。
title: 什麼是好的測試 (Test)
keywords:
  - Move
  - Sui
  - Move tutorial
  - what
  - makes
  - good
  - test
  - testing
questions:
  - What Makes a Good Test?
  - How do I use What Makes a Good Test in Move?
  - What is Characteristics of Good Tests in Move?
  - What to Test?
answer: 'Best practices for writing effective Move tests: concise, focused, and maintainable tests that catch real bugs in smart contracts.'
goal:
  description: 'Reader understands best practices for writing effective Move tests: concise, focused, and maintainable tests that catch real bugs in smart contracts'
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

# 什麼是好的測試 (What Makes a Good Test) {#what-makes-a-good-test}

撰寫測試是一回事；撰寫*好的*測試則是另一回事。如果測試套件實際上無法捕捉錯誤或協助你理解程式碼，僅僅存在就會帶來錯誤的信心。本節將介紹有效測試與流於表面的測試之間的原則與實務差異。

## 好測試的特性 (Characteristics of Good Tests) {#characteristics-of-good-tests}

### 1. 測試應簡潔明瞭 (1. Tests Should Be Concise) {#1-tests-should-be-concise}

每個測試都應簡潔且切中要點。避免撰寫過長且複雜的測試。讓測試保持簡短，並專注於單一行為或情境。

### 2. 測試應易於閱讀 (2. Tests Should Be Readable) {#2-tests-should-be-readable}

測試可作為程式碼預期行為的文件。任何閱讀測試的人都應能快速理解正在測試的情境，以及預期結果為何。

> **注意**：讓較長的函式呼叫更易於閱讀的可靠方法之一，是使用本章稍後介紹的
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
    // 安排：設定初始狀態
    let mut balance = new(100);

    // 執行：進行受測操作
    balance.add(50);

    // 驗證：確認預期結果
    assert_eq!(balance.value(), 150);
}
```

### 3. 測試應只測試一件事 (3. Tests Should Test One Thing) {#3-tests-should-test-one-thing}

每個測試都應驗證單一行為或情境。當測試失敗時，你應能立即知道哪裡出了問題。驗證多個無關行為的測試會使除錯更加困難。

```move
module book::single_responsibility;

public struct Counter has copy, drop { value: u64 }

public fun increment(c: &mut Counter) { c.value = c.value + 1; }
public fun decrement(c: &mut Counter) { c.value = c.value - 1; }

#[test_only]
use std::unit_test::assert_eq;

// 良好：為每個行為建立個別測試
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

### 測試契約，而非實作 (Test the Contract, Not the Implementation) {#test-the-contract-not-the-implementation}

請專注測試函式可觀察到的行為——它們回傳什麼，以及會產生哪些副作用——而非其內部如何達成。如此一來，你便能在不破壞測試的情況下重構實作。

### 測試邊界案例 (Test Edge Cases) {#test-edge-cases}

錯誤經常隱藏在邊界案例中。對於數值運算，請考慮：

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

確認程式碼在收到無效輸入時會適當地失敗。使用 `#[expected_failure]` 測試函式是否以正確的錯誤碼中止。請在預期結果中使用明確的錯誤常數，不要使用魔術數字。

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

### 追求良好涵蓋率，但不要追逐數字 (Aim for Good Coverage, but Don't Chase Numbers) {#aim-for-good-coverage-but-dont-chase-numbers}

高測試涵蓋率是正面的指標——它表示測試期間會執行更多程式碼，因而提高捕捉錯誤的機會。達到良好的涵蓋率，代表你已考慮過各種程式碼路徑與情境。

然而，涵蓋率不應是撰寫測試的首要目標。即使測試套件有 100% 涵蓋率，若測試未驗證有意義的行為，仍可能遺漏關鍵錯誤。僅為提高涵蓋率指標而存在、卻未驗證任何有用內容的測試，會帶來錯誤的信心。

請撰寫測試以驗證行為並捕捉錯誤。良好的涵蓋率應是完整測試的自然結果，而非目的本身。如需了解如何測量及解讀涵蓋率，請參閱 [Coverage Reports](./coverage.md)。

## 測試組織 (Test Organization) {#test-organization}

### 使用描述性的名稱 (Use Descriptive Names) {#use-descriptive-names}

測試名稱應描述受測情境與預期結果。良好的命名慣例是 `test_<function>_<scenario>_<expected_result>`，或直接描述該行為。無論你使用何種命名慣例，都應保持一致且易於理解。

### 將相關測試分組 (Group Related Tests) {#group-related-tests}

請依測試的函式或驗證的功能，以合乎邏輯的方式組織測試。在 Move 中，你可以將測試放在與受測程式碼相同的模組中，或放在獨立的測試模組中。常見做法是為 `sources/` 目錄中的每個模組，在 `tests/` 目錄建立一個測試模組 `*_tests.move`。

## 測試金字塔 (The Testing Pyramid) {#the-testing-pyramid}

平衡良好的測試套件通常遵循測試金字塔：

1. **單元測試**（底層）：許多小型且快速的測試，用於獨立驗證個別函式
2. **整合測試**（中層）：較少的測試，用於驗證元件如何共同運作
3. **端對端測試**（頂層）：少量測試，用於驗證完整的使用者情境

目前 Move 中所有測試皆實作為單元測試，但透過
[Test Scenario](./test-scenario.md)，你可以在單一測試中測試多筆交易與使用者操作。

## 常見的測試錯誤 (Common Testing Mistakes) {#common-testing-mistakes}

### 只測試順利路徑 (Testing Only the Happy Path) {#testing-only-the-happy-path}

不要只測試一切順利時程式碼是否能運作。也要測試出錯時會發生什麼事——無效輸入、邊界案例及錯誤條件。

### 過度模擬 (Over-Mocking) {#over-mocking}

雖然隔離很重要，但過度模擬可能導致即使實際整合會失敗，測試仍然通過。請在單元測試與使用真實元件的整合測試之間取得平衡。

### 忽略測試維護 (Ignoring Test Maintenance) {#ignoring-test-maintenance}

測試也是程式碼。請保持其整潔、移除過時的測試，並在需求變更時更新它們。遭到忽略的測試套件會成為負擔，而非資產。
