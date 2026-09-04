---
description: Move 測試 (testing) 基礎：使用 `#[test]` 屬性撰寫測試、使用預期失敗，並在模組中組織僅限測試的原始碼。
title: 測試基礎 (Testing Basics)
keywords:
  - Move
  - Sui
  - Move tutorial
  - testing
  - basics
questions:
  - What is Testing Basics in Move?
  - How do I use Testing Basics in Move?
  - What is a Test?
  - What is Running Tests in Move?
answer: 'Move testing basics: write tests with the #[test] attribute, use expected failures, and organize test-only code in your modules.'
goal:
  description: 'Reader understands move testing basics: write tests with the #[test] attribute, use expected failures, and organize test-only code in your modules'
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

# 測試基礎 (Testing Basics) {#testing-basics}

Move 編譯器內建測試框架——測試以 Move 撰寫，並與你的原始碼放在一起。你可以使用 `#[test]` 標註函式，編譯器會處理探索與執行。VM 執行環境與正式環境相同，因此你的程式碼會以完全相同的語意執行。不過，測試中的網路與儲存功能是模擬的，行為不會完全等同於實際鏈上執行時的情況——在測試與物件、交易及其他平台特定功能的互動時，請記得這一點。

## 什麼是測試？ (What is a Test?) {#what-is-a-test}

測試是以 `#[test]` 屬性標註的函式。測試不可接受引數，也不應回傳值。執行測試命令時，系統會自動偵測並執行測試函式。若測試函式意外[中止](./../move-basics/assert-and-abort.md)，測試便會失敗。

```move
module book::my_module;

#[test]
fun test_addition() {
    assert!(2 + 2 == 4);
}

#[test]
fun test_that_aborts() {
    abort // 此測試將會失敗 - 非預期的中止
}

#[test, expected_failure]
fun test_expected_abort() {
    abort // 此測試將會通過 - 預期會中止
}
```

## 執行測試 (Running Tests) {#running-tests}

若要執行測試，請使用 `sui move test` 命令。編譯器會以 _test mode_ 建置套件，並執行套件中找到的所有測試。

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

## 篩選測試 (Filtering Tests) {#filtering-tests}

提供篩選字串即可執行特定測試。只有完整限定名稱包含該篩選條件的測試會執行：

```bash
# 執行名稱中包含 "addition" 的測試
sui move test addition

# 執行特定模組中的所有測試
sui move test my_module

# 執行特定測試
sui move test book::my_module::test_addition
```

## 預期失敗 (Expected Failures) {#expected-failures}

使用 `#[expected_failure]` 測試程式碼是否會在特定條件下中止。僅當程式中止時測試才會通過；若正常完成，測試便會失敗。

### 基本預期失敗 (Basic Expected Failure) {#basic-expected-failure}

```move
#[test, expected_failure]
fun test_division_by_zero() {
    let _ = 1 / 0; // 中止 - 測試通過
}
```

### 預期中止碼 (Expected Abort Code) {#expected-abort-code}

指定預期的中止碼，確保函式是因正確的原因失敗：

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

### 來自其他模組的中止碼 (Abort Codes from Other Modules) {#abort-codes-from-other-modules}

`abort_code` 引數也可以參考在其他模組中定義的常數——包括[標準函式庫](./../move-basics/standard-library)與 [Sui Framework](./../programmability/sui-framework)——只要寫出其完整路徑即可。可見性在此不重要：此屬性可以命名依賴項中的私有常數。這是測試預期會在依賴項*內部*失敗之函式的方式：

```move file=packages/samples/sources/testing/testing-basics.move anchor=foreign_abort_code

```

### 預期位置 (Expected Location) {#expected-location}

使用 `location` 指定中止應發生的位置：

```move
#[test, expected_failure(abort_code = EInvalidInput, location = book::errors)]
fun test_abort_location() {
    validate(0);
}

// 對目前模組中的中止使用 `location = Self`
#[test, expected_failure(abort_code = ENotFound, location = Self)]
fun test_abort_in_self() {
    abort ENotFound
}
```

## 僅測試程式碼 (Test-Only Code) {#test-only-code}

以 `#[test_only]` 標記的程式碼只會在測試模式中編譯。可將其用於測試工具、輔助函式，或不應存在於正式原始碼中的匯入。`#[test_only]` 函式通常會具有 `public` 或 `public(package)` 可見性，以便其他模組中的測試能夠呼叫它們——由於僅測試程式碼會從正式建置中移除，這不會影響套件的公開 API。

> 注意：一個實用的原則是，為僅測試函式加上 `_for_testing` 後綴，並為僅測試常數加上 `TEST_` 前綴。這有助於將它們與正式原始碼區分，也更容易在程式碼庫中找到它們。由於僅測試函式通常會執行正式原始碼無法執行的操作，這是確保你不會意外在正式原始碼中使用僅測試函式的好方法。

### 僅測試匯入 (Test-Only Imports) {#test-only-imports}

```move
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun test_with_assert_eq() {
    assert_eq!(2 + 2, 4);
}
```

### 僅測試函式 (Test-Only Functions) {#test-only-functions}

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

### 僅測試常數 (Test-Only Constants) {#test-only-constants}

```move
#[test_only]
const TEST_ADDRESS: address = @0xCAFE;
```

### 僅測試模組 (Test-Only Modules) {#test-only-modules}

整個模組都可以是僅測試模組：

```move
#[test_only]
module book::test_helpers;

public fun create_test_scenario(): u64 { 42 }
```

## 實用 CLI 選項 (Useful CLI Options) {#useful-cli-options}

| 選項                   | 說明                                                                            |
| ---------------------- | ------------------------------------------------------------------------------- |
| `<filter>`             | 僅執行符合篩選條件的測試（位置引數）                                            |
| `--coverage`           | 收集涵蓋率資訊（請參閱 [Coverage](./coverage.md)）                              |
| `--trace`              | 為涵蓋率 LCOV 輸出產生追蹤                                                      |
| `--statistics`         | 顯示執行統計資料，包括 gas 使用量（請參閱 [Gas Profiling](./gas-profiling.md)） |
| `--threads <n>`        | 平行測試執行的執行緒數量                                                        |
| `--rand-num-iters <n>` | [隨機測試](./random-test.md)的迭代次數                                          |
| `--seed <n>`           | 可重現隨機測試執行的種子                                                        |

## 測試輸出 (Test Output) {#test-output}

測試失敗時，輸出會顯示：

- 測試名稱與 FAIL 狀態
- 中止碼（如有）
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

## 後續步驟 (Next Steps) {#next-steps}

在接下來的章節中，你將學習如何撰寫良好的測試、如何使用測試工具、如何測試交易，以及如何熟練掌握測試框架。
