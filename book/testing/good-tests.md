---
description: "撰寫有效測試的最佳實踐：簡潔、專注且易於維護的測試，能夠在智能合約中捕捉真實的漏洞。"
---

# 什麼構成一個好的測試 (What Makes a Good Test)

撰寫測試是一回事；撰寫 _好的_ 測試是另一回事。如果測試套件只是存在，但實際上無法捕捉漏洞或幫助您理解程式碼，那麼它只會提供虛假的信心。本節涵蓋區分有效測試與膚淺測試的原則和實踐。

## 好測試的特徵

### 1. 測試應該簡潔

每個測試應該簡潔明瞭。避免撰寫過長且複雜的測試。保持測試簡短，專注於單一行為或場景。

### 2. 測試應該具有可讀性

測試是程式碼預期行為的文檔。任何人閱讀測試時，應該能迅速理解測試的場景和預期結果。

> **注意：** 使長函式呼叫更易讀的方法之一是使用[建構器模式](./builder-pattern.md)，這將在本章後面介紹。

```move
#[test]
fun test_add_increases_balance_by_specified_amount() {
    // 安排：設定初始狀態
    let mut balance = balance::new(100);

    // 執行：執行正在測試的操作
    balance.add(50);

    // 斷言：驗證預期結果
    assert_eq!(balance.value(), 150);
}
```

### 3. 測試應該測試一件事

每個測試應該驗證單一行為或場景。當測試失敗時，您應該立即知道出了什麼問題。驗證多個不相關行為的測試會使除錯更加困難。

```move
module book::single_responsibility;

public struct Counter has copy, drop { value: u64 }

public fun increment(c: &mut Counter) { c.value = c.value + 1; }
public fun decrement(c: &mut Counter) { c.value = c.value - 1; }

#[test_only]
use std::unit_test::assert_eq;

// 好的做法：為每個行為分離測試
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

## 要測試什麼

### 測試合約，而非實現

專注於測試函式的可觀察行為 — 它們回傳什麼以及產生什麼副作用 — 而非它們在內部如何達成。這使您能夠重構實現而不破壞測試。

### 測試邊界情況

邊界情況是漏洞經常隱藏的地方。對於數值操作，應考慮：

- 零值
- 最大值（`U64_MAX`、`U128_MAX`）
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

### 測試錯誤情況

驗證您的程式碼在給定無效輸入時是否適當地失敗。使用 `#[expected_failure]` 測試函式是否以正確的錯誤碼中止。在期望值中使用明確的錯誤常數，不要使用魔法數字。

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

### 追求好的覆蓋率，但不要盲目追逐數字

高測試覆蓋率是一個正面指標 — 這意味著在測試期間更多的程式碼被執行，增加了捕捉漏洞的機會。達到良好覆蓋率表明您已經思考過各種程式碼路徑和場景。

然而，覆蓋率不應該是撰寫測試的主要目標。100% 覆蓋率的測試套件仍然可能遺漏關鍵漏洞，如果測試不驗證有意義的行為。只為了增加覆蓋率指標而存在的測試 — 沒有斷言任何有用的東西 — 提供虛假信心。

撰寫測試以驗證行為並捕捉漏洞。好的覆蓋率應該是徹底測試的自然結果，而不是目標本身。有關測量和解釋覆蓋率的更多資訊，請參見[覆蓋率報告](./coverage.md)。

## 測試組織

### 使用具描述性的名稱

測試名稱應該描述正在測試的場景和預期結果。一個好的命名慣例是 `test_<function>_<scenario>_<expected_result>` 或簡單地描述行為。無論您使用什麼命名慣例，它應該是一致且易於理解的。

### 分組相關的測試

邏輯上組織測試，可按其測試的函式或它驗證的功能進行組織。在 Move 中，您可以在與程式碼相同的模組中放置測試，或在單獨的測試模組中放置。通常會為 `sources/` 目錄中的每個模組在 `tests/` 目錄中建立一個測試模組 `*_tests.move`。

## 測試金字塔

一個均衡的測試套件通常遵循測試金字塔：

1. **單元測試**（基層）：許多小而快的測試，驗證隔離的個別函式
2. **整合測試**（中層）：較少的測試，驗證組件如何協同工作
3. **端對端測試**（頂層）：少量測試，驗證完整的使用者場景

目前在 Move 中，所有測試都實現為單元測試，但通過使用[測試場景](./test-scenario.md)，您可以在單一測試中測試多個交易和使用者操作。

## 常見的測試錯誤

### 僅測試正常路徑

不要只測試程式碼在一切正常時的工作情況。測試當事情出錯時會發生什麼 — 無效輸入、邊界情況和錯誤條件。

### 過度模擬

雖然隔離很重要，但過度模擬可能導致測試通過，但實際整合會失敗。在單元測試與使用真實組件的整合測試之間求取平衡。

### 忽視測試維護

測試也是程式碼。保持它們整潔，刪除已過時的測試，並在需求改變時更新它們。一個被忽視的測試套件會成為負債而非資產。
