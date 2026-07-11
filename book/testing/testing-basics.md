---
description: 移動測試基礎 (Move Testing Basics)：使用 `#[test]` 屬性撰寫測試、使用預期失敗 (expected failures)，並在你的模組中組織僅供測試用的程式碼。
---

# 測試基礎 (Testing Basics) {#testing-basics}

Move 編譯器內建測試框架 - 測試以 Move 撰寫，與你的原始碼放在一起。你在函式上標註 `#[test]`，編譯器會負責發現與執行。VM 執行環境與正式環境相同，因此你的程式碼會以相同的語意執行。然而，網路與儲存功能在測試中是模擬的，與實際上鏈執行時的行為並不完全相同 - 這是在測試與物件、交易及其他平台特定功能互動時需要留意的地方。

## 什麼是測試？ (What is a Test?) {#what-is-a-test}

測試是標註了 `#[test]` 屬性的函式。測試不能接受參數，也不應該回傳值。執行測試指令時，測試函式會被自動偵測並執行。如果測試函式意外地
[abort](./../move-basics/assert-and-abort.md)，該測試就會失敗。

```move
module book::my_module;

#[test]
fun test_addition() {
    assert!(2 + 2 == 4);
}

#[test]
fun test_that_aborts() {
    abort // 此測試會失敗 - 意外的 abort
}

#[test, expected_failure]
fun test_expected_abort() {
    abort // 此測試會通過 - abort 是預期中的
}
```

## 執行測試 (Running Tests) {#running-tests}

要執行測試，使用 `sui move test` 指令。編譯器會以 _測試模式_ 建置套件，並執行套件中所有找到的測試。

```bash
sui move test
```

範例輸出：

```
Running Move unit tests
[ PASS    ] book::my_module::test_addition
[ FAIL    ] book::my_module::test_that_aborts
[ PASS    ] book::my_module::test_expected_abort
Test result: FAILED. Total tests: 3; passed: 2; failed: 1
```

## 篩選測試 (Filtering Tests) {#filtering-tests}

透過提供篩選字串來執行特定測試。只有完整限定名稱包含該篩選字串的測試才會被執行：

```bash
# 執行名稱中包含 "addition" 的測試
sui move test addition

# 執行特定模組中的所有測試
sui move test my_module

# 執行特定的測試
sui move test book::my_module::test_addition
```

## 預期失敗 (Expected Failures) {#expected-failures}

使用 `#[expected_failure]` 來測試程式碼在特定條件下會 abort。只有在該測試 abort 時才會通過；如果它正常完成，該測試就會失敗。

### 基本的預期失敗 (Basic Expected Failure) {#basic-expected-failure}

```move
#[test, expected_failure]
fun test_division_by_zero() {
    let _ = 1 / 0; // Aborts - 測試通過
}
```

### 預期的 Abort 代碼 (Expected Abort Code) {#expected-abort-code}

指定預期的 abort 代碼，以確保函式是因為正確的原因而失敗：

```move
module book::errors;

const EInvalidInput: u64 = 1;
const ENotFound: u64 = 2;

public fun validate(x: u64) {
    assert!(x > 0, EInvalidInput);
}

#[test, expected_failure(abort_code = EInvalidInput)]
fun test_validate_zero_fails() {
    validate(0); // 以 EInvalidInput abort - 測試通過
}

#[test, expected_failure(abort_code = ENotFound)]
fun test_wrong_error_code() {
    validate(0); // 以 EInvalidInput abort，而非 ENotFound - 測試失敗
}
```

### 來自其他模組的 Abort 代碼 (Abort Codes from Other Modules) {#abort-codes-from-other-modules}

`abort_code` 引數也可以透過寫出完整路徑，來參照定義在其他模組中的常數 - 包括
[Standard Library](./../move-basics/standard-library) 與
[Sui Framework](./../programmability/sui-framework)。可見性在這裡並不重要：該屬性可以指名依賴項的私有常數。這是測試某個預期會在依賴項 _內部_ 失敗的函式的方式：

```move file=packages/samples/sources/testing/testing-basics.move anchor=foreign_abort_code

```

### 預期的位置 (Expected Location) {#expected-location}

使用 `location` 指定 abort 應該發生的位置：

```move
#[test, expected_failure(abort_code = EInvalidInput, location = book::errors)]
fun test_abort_location() {
    validate(0);
}

// 對於發生在當前模組中的 abort 使用 `location = Self`
#[test, expected_failure(abort_code = ENotFound, location = Self)]
fun test_abort_in_self() {
    abort ENotFound
}
```

## 僅供測試用的程式碼 (Test-Only Code) {#test-only-code}

標記為 `#[test_only]` 的程式碼只會在測試模式下編譯。將它用於測試工具、輔助函式，或是不應該存在於正式環境程式碼中的 import。`#[test_only]` 函式通常會具有 `public` 或 `public(package)` 可見性，讓它們可以被其他模組中的測試呼叫 - 由於僅供測試用的程式碼會從正式建置中剝除，這不會影響你套件的公開 API。

> 備註：一個好的經驗法則是為僅供測試用的函式加上 `_for_testing` 後綴，並為僅供測試用的常數加上 `TEST_` 前綴。這有助於將它們與正式環境程式碼區分開來，並讓在程式碼庫中尋找它們變得更容易。既然僅供測試用的函式經常會做一些正式環境程式碼無法做的事，這是確保你不會意外在正式環境程式碼中使用僅供測試用函式的好方法。

### 僅供測試用的 Import (Test-Only Imports) {#test-only-imports}

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_with_assert_eq() {
    assert_eq!(2 + 2, 4);
}
```

### 僅供測試用的函式 (Test-Only Functions) {#test-only-functions}

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

### 僅供測試用的常數 (Test-Only Constants) {#test-only-constants}

```move
#[test_only]
const TEST_ADDRESS: address = @0xCAFE;
```

### 僅供測試用的模組 (Test-Only Modules) {#test-only-modules}

整個模組都可以是僅供測試用的：

```move
#[test_only]
module book::test_helpers;

public fun create_test_scenario(): u64 { 42 }
```

## 實用的 CLI 選項 (Useful CLI Options) {#useful-cli-options}

| 選項                   | 說明                                                                        |
| ---------------------- | --------------------------------------------------------------------------- |
| `<filter>`             | 只執行符合篩選字串的測試（位置引數）                                        |
| `--coverage`           | 收集覆蓋率資訊（見 [Coverage](./coverage.md)）                              |
| `--trace`              | 為覆蓋率 LCOV 輸出產生追蹤資料                                              |
| `--statistics`         | 顯示執行統計資訊，包括 gas 使用量（見 [Gas Profiling](./gas-profiling.md)） |
| `--threads <n>`        | 並行測試執行使用的執行緒數量                                                |
| `--rand-num-iters <n>` | [random tests](./random-test.md) 的疊代次數                                 |
| `--seed <n>`           | 用於可重現隨機測試執行結果的種子值                                          |

## 測試輸出 (Test Output) {#test-output}

當測試失敗時，輸出會顯示：

- 測試名稱與 FAIL 狀態
- Abort 代碼（如果有的話）
- 發生失敗的位置
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

## 後續步驟 (Next Steps) {#next-steps}

在接下來的章節中，你將學習如何撰寫良好的測試、如何使用測試工具、如何測試交易，以及如何精通這個測試框架。
