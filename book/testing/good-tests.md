---
description: "撰寫有效 Move 測試的最佳實踐：簡潔、專注且易於維護的測試，能捕捉智能合約中的真實錯誤。"
---

# 什麽是好的測試 (What Makes a Good Test)

撰寫測試是一回事，撰寫**好**的測試又是另一回事。如果一套測試僅僅是為了存在而存在，卻無法實際捕捉錯誤或幫助你理解程式碼，那它提供的只是虛假的安全感。本節將介紹區分有效測試與表面測試的原則和實踐。

## 好的測試特徵

### 1. 測試應該簡潔

每個測試都應該簡潔明瞭，直入主題。避免撰寫過長和複雜的測試。保持測試簡短，並專注於單一行為或情境。

### 2. 測試應該具備可讀性

測試作為程式碼預期行為的文件。任何閱讀測試的人都應該能迅速理解正在測試的情境以及預期的結果是什麼。

> **注意：** 讓長函式調用更具可讀性的保證方法之一是使用 [Builder 模式](./builder-pattern.md)，這將在本章後面介紹。

```move
#[test]
fun test_add_increases_balance_by_specified_amount() {
    // Arrange (安排): 設定初始狀態
    let mut balance = balance::new(100);

    // Act (執行): 執行被測試的操作
    balance.add(50);

    // Assert (斷言): 驗證預期結果
    assert_eq!(balance.value(), 150);
}
```

### 3. 測試應該只測一件事

每個測試應該只驗證單一行為或情境。當測試失敗時，你應該能立即知道出了什麼錯。驗證多個不相關行為的測試會使除錯變得更加困難。

```move
module book::single_responsibility;

public struct Counter has copy, drop { value: u64 }

public fun increment(c: &mut Counter) { c.value = c.value + 1; }
public fun decrement(c: &mut Counter) { c.value = c.value - 1; }

#[test_only]
use std::unit_test::assert_eq;

// Good: 每個行為有獨立的測試
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

## 該測試什麼

### 測試合約行為，而非實作細節

專注於測試函式的可觀察行為 —— 它們回傳什麼以及產生什麼副作用 —— 而不是它們內部如何實現。這讓你可以重構實作而不破壞測試。

### 測試邊緣案例

邊緣案例通常是錯誤隱藏的地方。對於數值運算，考慮：

- 零值
- 最大值 (`U64_MAX`, `U128_MAX`)
- 邊界條件 (差一位錯誤 off-by-one errors)
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

### 測試錯誤條件

驗證當給定無效輸入時，你的程式碼是否能適當地失敗。使用 `#[expected_failure]` 來測試函式是否以正確的錯誤代碼中止。在預期中使用明確的錯誤常數，不要使用魔術數字 (magic numbers)。

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

### 追求良好的覆蓋率，但不要盲目追求數字

高測試覆蓋率是一個正面指標 —— 它意味著你的更多程式碼在測試期間被執行到了，增加了捕捉錯誤的機會。達到良好的覆蓋率證明你已經考慮了各種程式路徑和情境。

然而，覆蓋率不應成為撰寫測試的主要目標。如果測試沒有驗證有意義的行為，即使是 100% 覆蓋率的測試套件也可能遺漏關鍵錯誤。僅僅為了提升覆蓋率指標而存在 —— 卻沒有斷言任何有用資訊 —— 的測試，提供的是虛假的信心。

撰寫測試是為了驗證行為並捕捉錯誤。良好的覆蓋率應該是徹底測試的自然結果，而非目的本身。關於測量和解讀覆蓋率的更多資訊，請參見[覆蓋率報告](./coverage.md)。

## 測試組織

### 使用描述性的名稱

測試名稱應描述被測試的情境和預期結果。一個好的命名慣例是 `test_<function>_<scenario>_<expected_result>` (測試_函式_情境_預期結果) 或簡單描述該行為。無論你使用什麼命名慣例，它應該保持一致且易於理解。

### 分組相關測試

按邏輯組織測試，可以根據它們測試的函式或驗證的功能。在 Move 中，你可以將測試放在與被測試程式碼相同的模組中，或者放在獨立的測試模組中。常見的做法是在 `tests/` 目錄中為 `sources/` 目錄中的每個模組建立一個測試模組 `*_tests.move`。

## 測試金字塔

一個平衡良好的測試套件通常遵循測試金字塔：

1. **單元測試** (基底)：大量的小型、快速測試，單獨驗證個別函式。
2. **整合測試** (中層)：較少的測試，驗證組件如何協同運作。
3. **端對端測試** (頂層)：少量測試，驗證完整的使用者情境。

目前在 Move 中，所有測試都是以單元測試的形式實現的，但通過使用 [測試場景 (Test Scenario)](./test-scenario.md)，你可以在單個測試中測試多個交易和使用者操作。

## 常見測試錯誤

### 只測試快樂路徑 (Happy Path)

不要只測試當一切順利時程式碼是否正常運作。測試當事情出錯時會發生什麼 —— 無效輸入、邊緣案例和錯誤條件。

### 過度 Mocking (Over-Mocking)

雖然隔離很重要，但過度使用 Mocking (模擬物件) 可能導致測試通過但實際整合卻失敗。應在使用真實組件的整合測試與單元測試之間取得平衡。

### 忽視測試維護

測試也是程式碼。保持它們整潔，移除過時的測試，並在需求變更時更新它們。被忽視的測試套件會變成負債而非資產。
