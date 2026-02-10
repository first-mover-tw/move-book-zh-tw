---
description: "Move 測試基礎：使用 #[test] 屬性撰寫測試、使用預期失敗，以及在模組中組織僅測試用程式碼。"
---

# 測試基礎 (Testing Basics)

Move 編譯器有內建的測試框架 - 測試用 Move 撰寫並存在於原始碼旁邊。你可以用 `#[test]` 註解標記函式，編譯器會負責發現和執行。VM 執行環境與生產環境相同，因此你的程式碼執行時具有相同的語義。然而，網路和儲存功能在測試中是模擬的，在實際鏈上執行時的行為不完全相同 - 這是測試與物件、交易和其他平台特定功能互動時需要留意的地方。

## 什麼是測試？(What is a Test?)

測試是以 `#[test]` 屬性標記的函式。測試無法接收引數且不應該回傳值。測試函式在執行測試命令時會被自動發現和執行。如果測試函式 [中止](./../move-basics/assert-and-abort.md) 了，測試會失敗。

```move
module book::my_module;

#[test]
fun test_addition() {
    assert!(2 + 2 == 4);
}

#[test]
fun test_that_aborts() {
    abort // 這個測試會失敗 - 意外中止
}

#[test, expected_failure]
fun test_expected_abort() {
    abort // 這個測試會通過 - 預期中止
}
```

## 執行測試 (Running Tests)

要執行測試，使用 `sui move test` 命令。編譯器會以 _測試模式_ 構建套件並執行在套件中找到的所有測試。

```bash
sui move test
```

輸出範例：

```
Running Move unit tests
[ PASS    ] book::my_module::test_addition
[ FAIL    ] book::my_module::test_that_aborts
[ PASS    ] book::my_module::test_expected_abort
Test result: FAILED. Total tests: 3; passed: 2; failed: 1
```

## 篩選測試 (Filtering Tests)

透過提供篩選字串來執行特定測試。只有完全限定名稱包含篩選條件的測試才會執行：

```bash
# 執行名稱中包含 "addition" 的測試
sui move test addition

# 執行特定模組中的所有測試
sui move test my_module

# 執行特定測試
sui move test book::my_module::test_addition
```

## 預期失敗 (Expected Failures)

使用 `#[expected_failure]` 來測試程式碼在某些條件下是否中止。測試只有在中止時才會通過；如果正常完成，測試會失敗。

### 基本預期失敗 (Basic Expected Failure)

```move
#[test, expected_failure]
fun test_division_by_zero() {
    let _ = 1 / 0; // 中止 - 測試通過
}
```

### 預期中止程式碼 (Expected Abort Code)

指定預期的中止程式碼以確保函式因正確的原因而失敗：

```move
module book::errors;

const EInvalidInput: u64 = 1;
const ENotFound: u64 = 2;

public fun validate(x: u64) {
    assert!(x > 0, EInvalidInput);
}

#[test, expected_failure(abort_code = EInvalidInput)]
fun test_validate_zero_fails() {
    validate(0); // 以 EInvalidInput 中止 - 測試通過
}

#[test, expected_failure(abort_code = ENotFound)]
fun test_wrong_error_code() {
    validate(0); // 以 EInvalidInput 中止，而非 ENotFound - 測試失敗
}
```

### 預期位置 (Expected Location)

使用 `location` 指定中止應該發生的位置：

```move
#[test, expected_failure(abort_code = EInvalidInput, location = book::errors)]
fun test_abort_location() {
    validate(0);
}

// 針對目前模組中的中止使用 `location = Self`
#[test, expected_failure(abort_code = 1, location = Self)]
fun test_abort_in_self() {
    abort 1
}
```

## 僅測試用程式碼 (Test-Only Code)

以 `#[test_only]` 標記的程式碼僅在測試模式下編譯。使用它來放置測試工具、幫助函式或不應該在生產程式碼中出現的導入。`#[test_only]` 函式通常具有 `public` 或 `public(package)` 可見性以便可以從其他模組中的測試呼叫 - 由於僅測試用程式碼會從生產構建中去除，這不會影響你的套件的公開 API。

> 注意：一個好的經驗法則是在僅測試用函式和常數中加上 `_for_testing` 後綴。這有助於區分它們和生產程式碼，並使在程式碼庫中找到它們更容易。由於僅測試用函式通常做一些生產程式碼無法做的事，這是一個好方法來確保你不會意外在生產程式碼中使用僅測試用函式。

### 僅測試用導入 (Test-Only Imports)

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_with_assert_eq() {
    assert_eq!(2 + 2, 4);
}
```

### 僅測試用函式 (Test-Only Functions)

```move
#[test_only]
fun setup_test_data(): vector<u64> {
    vector[1, 2, 3, 4, 5]
}

#[test]
fun test_sum() {
    let data = setup_test_data();
    let mut sum = 0;
    data.do!(|x| sum = sum + x);
    assert!(sum == 15);
}
```

### 僅測試用常數 (Test-Only Constants)

```move
#[test_only]
const TEST_ADDRESS: address = @0xCAFE;
```

### 僅測試用模組 (Test-Only Modules)

整個模組可以是僅測試用的：

```move
#[test_only]
module book::test_helpers;

public fun create_test_scenario(): u64 { 42 }
```

## 有用的 CLI 選項 (Useful CLI Options)

| 選項                   | 說明                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| `<filter>`             | 只執行符合篩選條件的測試（位置引數）                                |
| `--coverage`           | 收集覆蓋率資訊（見 [覆蓋率](./coverage.md)）                            |
| `--trace`              | 為覆蓋率 LCOV 輸出產生追蹤                                                |
| `--statistics`         | 顯示執行統計包括 gas 使用情況（見 [Gas 分析](./gas-profiling.md)) |
| `--threads <n>`        | 並行測試執行的執行緒數量                                           |
| `--rand-num-iters <n>` | [隨機測試](./random-test.md) 的迭代次數                               |
| `--seed <n>`           | 可重現隨機測試執行的種子                                                  |

## 測試輸出 (Test Output)

當測試失敗時，輸出會顯示：

- 測試名稱和失敗狀態
- 中止程式碼（如果有的話）
- 失敗發生的位置
- 用於除錯的堆疊追蹤

```table
┌── test_that_failed ──────
│ error[E11001]: test failure
│    ┌─ ./sources/module.move:15:9
│    │
│ 15 │         assert!(balance == 100);
│    │         ^^^^^^^^^^^^^^^^^^^^^^^ Test was not expected to error, but it
│    │         aborted with code 1 originating in the module 0x0::module
│
└──────────────────
```

## 後續步驟 (Next Steps)

在接下來的部分中，你將學習如何撰寫好的測試、如何使用測試工具、如何測試交易以及如何精通測試框架。
