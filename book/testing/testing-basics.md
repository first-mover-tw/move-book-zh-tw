---
description: 'Move 測試基礎：使用 #[test] 屬性撰寫測試、使用預期失敗 (expected failures)，以及在模組中組織測試專用 (test-only) 程式碼。'
---

# 測試基礎 (Testing Basics)

Move 編譯器內建了一個測試框架 —— 測試是用 Move 撰寫的，並與你的原始碼並存。你使用 `#[test]` 標註函式，編譯器會處理發現和執行。VM 執行環境與生產環境相同，因此你的程式碼會在相同的語義下運行。然而，網路和存儲功能在測試中是模擬的，其行為與實際鏈上執行時不完全相同 —— 在測試與物件、交易和其他平台特定功能的互動時，這是一點需要注意的地方。

## 什麼是測試？

測試是一個標註了 `#[test]` 屬性的函式。測試不能接受參數，也不應回傳值。執行測試命令時，測試函式會被自動檢測並執行。如果測試函式意外[中止 (aborts)](./../move-basics/assert-and-abort.md)，則測試失敗。

```move
module book::my_module;

#[test]
fun test_addition() {
    assert!(2 + 2 == 4);
}

#[test]
fun test_that_aborts() {
    abort // 這個測試將會失敗 (FAIL) - 意外的中止
}

#[test, expected_failure]
fun test_expected_abort() {
    abort // 這個測試將會通過 (PASS) - 中止是預期的
}
```

## 執行測試

要執行測試，請使用 `sui move test` 命令。編譯器會以_測試模式_建置套件，並執行在套件中找到的所有測試。

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

## 過濾測試

透過提供過濾字串來執行特定測試。只有完全限定名稱 (fully qualified name) 包含該過濾字串的測試才會執行：

```bash
# 執行名稱中包含 "addition" 的測試
sui move test addition

# 執行特定模組中的所有測試
sui move test my_module

# 執行特定測試
sui move test book::my_module::test_addition
```

## 預期失敗 (Expected Failures) {#expected-failures}

使用 `#[expected_failure]` 來測試程式碼在特定條件下是否會中止。只有當程式碼中止時，測試才會通過；如果它正常完成，測試就會失敗。

### 基本預期失敗

```move
#[test, expected_failure]
fun test_division_by_zero() {
    let _ = 1 / 0; // Aborts (中止) - 測試通過
}
```

### 預期中止代碼 (Abort Code)

指定預期的中止代碼，以確保函式是因為正確的原因而失敗：

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
    validate(0); // 以 EInvalidInput 中止，而不是 ENotFound - 測試失敗
}
```

### 預期位置 (Expected Location)

使用 `location` 指定中止應該發生的位置：

```move
#[test, expected_failure(abort_code = EInvalidInput, location = book::errors)]
fun test_abort_location() {
    validate(0);
}

// 對於當前模組中的中止，使用 `location = Self`
#[test, expected_failure(abort_code = 1, location = Self)]
fun test_abort_in_self() {
    abort 1
}
```

## 測試專用程式碼 (Test-Only Code)

標記為 `#[test_only]` 的程式碼僅在測試模式下編譯。將其用於測試工具、輔助函式或不應存在於生產程式碼中的引入 (imports)。通常 `#[test_only]` 函式具有 `public` 或 `public(package)` 可見性，以便其他模組中的測試可以調用它們 —— 由於測試專用程式碼會從生產構建中剝離，這不會影響你套件的公開 API。

> 注意：一個好的經驗法則是為測試專用函式和常數加上 `_for_testing` 後綴。這有助於將它們與生產程式碼區分開來，並使它們在程式碼庫中更容易找到。鑑於測試專用函式通常會做生產程式碼不能做的事情，這是一個確保你不會在生產程式碼中意外使用測試專用函式的好方法。

### 測試專用引入 (Test-Only Imports)

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_with_assert_eq() {
    assert_eq!(2 + 2, 4);
}
```

### 測試專用函式 (Test-Only Functions)

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

### 測試專用常數 (Test-Only Constants)

```move
#[test_only]
const TEST_ADDRESS: address = @0xCAFE;
```

### 測試專用模組 (Test-Only Modules)

整個模組都可以是測試專用的：

```move
#[test_only]
module book::test_helpers;

public fun create_test_scenario(): u64 { 42 }
```

## 常用的 CLI 選項

| 選項                   | 描述                                                                    |
| ---------------------- | ----------------------------------------------------------------------- |
| `<filter>`             | 僅執行符合過濾條件的測試 (位置參數)                                     |
| `--coverage`           | 收集覆蓋率資訊 (參見 [覆蓋率](./coverage.md))                           |
| `--trace`              | 為覆蓋率 LCOV 輸出生成追蹤紀錄                                          |
| `--statistics`         | 顯示執行統計資訊，包括 Gas 使用量 (參見 [Gas 分析](./gas-profiling.md)) |
| `--threads <n>`        | 平行測試執行的執行緒數量                                                |
| `--rand-num-iters <n>` | [隨機測試](./random-test.md) 的迭代次數                                 |
| `--seed <n>`           | 用於可重現隨機測試運行的種子                                            |

## 測試輸出

當測試失敗時，輸出會顯示：

- 測試名稱和 FAIL (失敗) 狀態
- 中止代碼 (如果有的話)
- 發生失敗的位置
- 用於除錯的堆疊追蹤 (stack trace)

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

## 下一步

在接下來的章節中，你將學習如何撰寫好的測試、如何使用測試工具、如何測試交易以及如何精通測試框架。
