---
title: 單元測試 (Unit Tests) | 參考手冊
description: Move 單元測試 (unit testing) 參考手冊 (reference)：#[test]、#[expected_failure]、#[test_only] 註解 (annotations)、測試旗標 (test flags) 與執行選項 (execution options)。
keywords:
  - Move
  - Sui
  - Move reference
  - unit
  - tests
  - reference
  - testing
questions:
  - How does Unit Tests work in Move?
  - What is the syntax for Unit Tests in Move?
  - What is Test Annotations in Move?
  - What is Expected Failures in Move?
answer: 'Move unit testing reference: #[test], #[expected_failure], #[test_only] annotations, test flags, and execution options.'
goal:
  description: 'Reader understands move unit testing reference: #[test], #[expected_failure], #[test_only] annotations, test flags, and execution options'
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

# 單元測試 (Unit Tests) {#unit-tests}

Move 的單元測試在 Move 原始碼語言中使用三種註解：

- `#[test]` 將函式標記為測試；
- `#[expected_failure]` 標記預期會失敗的測試；
- `#[test_only]` 將模組或模組成員（[`use`](./uses)、[函式](./functions)、
  [結構](./structs)或[常數](./constants)）標記為僅納入測試的程式碼。

這些註解可套用於任何具有任意可見性的適當形式。只要模組或模組成員標註為
`#[test_only]` 或 `#[test]`，除非為測試而編譯，否則不會納入已編譯的位元組碼。

## 測試標註 (Test Annotations) {#test-annotations}

`#[test]` 標註只能放在沒有參數的函式上。此標註會將該函式標記為由單元測試執行工具執行的測試。

```move
#[test] // 正確
fun this_is_a_test() { ... }

#[test] // 由於測試接受一個引數，因此將無法編譯
fun this_is_not_correct(arg: u64) { ... }
```

測試也可以標註為 `#[expected_failure]`。此標註表示該測試預期會引發錯誤。`#[expected_failure]` 標註可搭配多個選項使用，以確保只有符合指定條件的失敗會被標記為通過；這些選項詳述於[預期失敗](#expected-failures)。只有具有 `#[test]` 標註的函式，也可以標註為 #`[expected_failure]`。

以下列出一些使用 `#[expected_failure]` 標註的簡單範例：

```move
#[test, expected_failure]
public fun this_test_will_abort_and_pass() { abort 1 }

#[test, expected_failure]
public fun test_will_error_and_pass() { 1/0; }

// 由於測試以預期的中止碼常數失敗，因此將通過。
// ENotFound 是在模組中定義的常數。
#[test, expected_failure(abort_code = ENotFound)]
public fun test_will_error_and_pass_abort_code() { abort ENotFound }

// 由於測試以與預期不同的錯誤失敗，因此將失敗。
#[test, expected_failure(abort_code = my_module::ENotFound)]
public fun test_will_error_and_fail() { 1/0; }

#[test, expected_failure] // 一個屬性中可以有多個標註。此測試將通過。
public fun this_other_test_will_abort_and_pass() { abort 1 }
```

> **注意**：`#[test]` 和 `#[test_only]` 函式也可以呼叫 [`entry`](./functions#entry-modifier) 函式，無論其可見性為何。

## 預期失敗 (Expected Failures) {#expected-failures}

你可以透過多種不同方式使用 `#[expected_failure]` 註解，來指定不同類型的錯誤條件。如下所示：

### 1. 指定中止碼 (1. `#[expected_failure(abort_code = <constant>)]`) {#1-expected_failureabort_code-constant}

若測試在定義該常數的模組中，以指定的常數值中止，則此測試會通過；否則會失敗。這是測試預期測試失敗情況的建議方式。

> **注意**：你可以在 `expected_failure` 註解中參考目前模組或套件以外的常數。

```move
module pkg_addr::other_module {
    const ENotFound: u64 = 1;
    public fun will_abort() {
        abort ENotFound
    }
}

module pkg_addr::my_module {
    use pkg_addr::other_module;
    const ENotFound: u64 = 1;

    #[test, expected_failure(abort_code = ENotFound)]
    fun test_will_abort_and_pass() { abort ENotFound }

    #[test, expected_failure(abort_code = other_module::ENotFound)]
    fun test_will_abort_and_pass() { other_module::will_abort() }

    // 失敗：因為預期的是錯誤模組中的常數，所以不會通過。
    #[test, expected_failure(abort_code = ENotFound)]
    fun test_will_abort_and_pass() { other_module::will_abort() }
}
```

### 2. 指定算術錯誤 (2. `#[expected_failure(arithmetic_error, location = <location>)]`) {#2-expected_failurearithmetic_error-location-location}

這會指定測試預期在指定位置因算術錯誤而失敗（例如整數溢位、除以零等）。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

```move
module pkg_addr::other_module {
    public fun will_arith_error() { 1/0; }
}

module pkg_addr::my_module {
    use pkg_addr::other_module;

    #[test, expected_failure(arithmetic_error, location = Self)]
    fun test_will_arith_error_and_pass1() { 1/0; }

    #[test, expected_failure(arithmetic_error, location = pkg_addr::other_module)]
    fun test_will_arith_error_and_pass2() { other_module::will_arith_error() }

    // 失敗：因為預期失敗的位置與測試實際失敗的位置不同，
    // 所以會失敗。
    #[test, expected_failure(arithmetic_error, location = Self)]
    fun test_will_arith_error_and_fail() { other_module::will_arith_error() }
}
```

### 3. 指定 gas 耗盡錯誤 (3. `#[expected_failure(out_of_gas, location = <location>)]`) {#3-expected_failureout_of_gas-location-location}

這會指定測試預期在指定位置因 gas 耗盡錯誤而失敗。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

```move
module pkg_addr::other_module {
    public fun will_oog() { loop {} }
}

module pkg_addr::my_module {
    use pkg_addr::other_module;

    #[test, expected_failure(out_of_gas, location = Self)]
    fun test_will_oog_and_pass1() { loop {} }

    #[test, expected_failure(arithmetic_error, location = pkg_addr::other_module)]
    fun test_will_oog_and_pass2() { other_module::will_oog() }

    // 失敗：因為預期失敗的位置與測試實際失敗的位置不同，
    // 所以會失敗。
    #[test, expected_failure(out_of_gas, location = Self)]
    fun test_will_oog_and_fail() { other_module::will_oog() }
}
```

### 4. 指定向量錯誤 (4. `#[expected_failure(vector_error, minor_status = <u64_opt>, location = <location>)]`) {#4-expected_failurevector_error-minor_status-u64_opt-location-location}

這會指定測試預期在指定位置因向量錯誤而失敗，並使用指定的 `minor_status`（若有提供）。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。`<u64_opt>` 是選用參數，用於指定向量錯誤的次要狀態。若未指定，測試只要因任何次要狀態而失敗即可通過。若有指定，測試只有在因指定次要狀態的向量錯誤而失敗時才會通過。

```move
module pkg_addr::other_module {
    public fun vector_borrow_empty() {
        &vector<u64>[][1];
    }
}

module pkg_addr::my_module {
    #[test, expected_failure(vector_error, location = Self)]
    fun vector_abort_same_module() {
        vector::borrow(&vector<u64>[], 1);
    }

    #[test, expected_failure(vector_error, location = pkg_addr::other_module)]
    fun vector_abort_same_module() {
        other_module::vector_borrow_empty();
    }

    // 可以指定預期的次要狀態（亦即向量專用錯誤碼）。
    #[test, expected_failure(vector_error, minor_status = 1, location = Self)]
    fun native_abort_good_right_code() {
        vector::borrow(&vector<u64>[], 1);
    }

    // 失敗：錯誤正確，但位置錯誤。
    #[test, expected_failure(vector_error, location = pkg_addr::other_module)]
    fun vector_abort_same_module() {
        other_module::vector_borrow_empty();
    }

    // 失敗：錯誤與位置皆正確，但次要狀態不同，因此此測試會失敗。
    #[test, expected_failure(vector_error, minor_status = 0, location = Self)]
    fun vector_abort_wrong_minor_code() {
        vector::borrow(&vector<u64>[], 1);
    }
}
```

### 5. 任意錯誤碼 (5. `#[expected_failure]`) {#5-expected_failure}

若測試以 _任何_ 錯誤碼中止，則此測試會通過。使用此方式標註預期測試失敗時，應該 **_極度謹慎_**，並且一律優先使用上述任一方式。這類註解的範例如下：

```move
#[test, expected_failure]
fun test_will_abort_and_pass1() { abort 1 }

#[test, expected_failure]
fun test_will_arith_error_and_pass2() { 1/0; }
```

## 僅供測試的註解 (Test Only Annotations) {#test-only-annotations}

模組及其任何成員都可以宣告為僅供測試。若項目標註為
`#[test_only]`，則只有在測試模式下編譯時，該項目才會被納入已編譯的 Move 位元組碼中。此外，在測試模式以外進行編譯時，任何非測試用途對 `#[test_only]`
模組的 `use` 都會在編譯期間引發錯誤。

> **注意**：標註為 `#[test_only]` 的函式僅能從測試原始碼中呼叫，
> 但它們本身並非測試，且單元測試框架不會將其作為測試執行。

```move
#[test_only] // 僅供測試的屬性可附加至模組
module abc { ... }

#[test_only] // 僅供測試的屬性可附加至常數
const MY_ADDR: address = @0x1;

#[test_only] // .. 可附加至 use
use pkg_addr::some_other_module;

#[test_only] // .. 可附加至結構
public struct SomeStruct { ... }

#[test_only] // .. 以及函式。只能從測試原始碼呼叫，但這_不是_測試！
fun test_only_function(...) { ... }
```

## 執行單元測試 (Running Unit Tests) {#running-unit-tests}

使用 `sui move test` 指令來執行 [Move 套件](./packages)的單元測試。

執行測試時，每個測試都會是 `PASS`、`FAIL` 或 `TIMEOUT`。如果測試案例失敗，將會盡可能回報失敗位置，以及導致失敗的函式名稱。你可以在下方看到範例。

若測試超過任何單一測試可執行的最大指令數量，該測試將被標記為逾時。你可以透過下列選項變更此上限。此外，雖然測試結果一律具確定性，測試預設會平行執行；因此，除非僅使用一個執行緒執行，否則單次測試執行中的測試結果排序並不具確定性。你可以透過選項設定此行為。

前述選項只是眾多可微調測試並協助偵錯失敗測試的選項中的兩個。若要查看所有可用選項及各選項的說明，請將 `--help` 旗標傳遞給 `sui move test` 指令：

```
$ sui move test --help
```

## 範例 (Example) {#example}

以下範例顯示使用部分單元測試功能的簡單模組：

首先，建立空白套件並切換至該目錄：

```bash
$ sui move new test_example; cd test_example
```

接著，在 `sources` 目錄下新增以下模組：

```move
// 檔案名稱：sources/my_module.move
module test_example::my_module;

public struct Wrapper(u64)

const ECoinIsZero: u64 = 0;

public fun make_sure_non_zero_coin(coin: Wrapper): Wrapper {
    assert!(coin.0 > 0, ECoinIsZero);
    coin
}

#[test]
fun make_sure_non_zero_coin_passes() {
    let coin = Wrapper(1);
    let Wrapper(_) = make_sure_non_zero_coin(coin);
}

#[test, expected_failure(abort_code = ECoinIsZero)]
// 如果不在意中止碼，也可使用 #[test, expected_failure]
fun make_sure_zero_coin_fails() {
    let coin = Wrapper(0);
    let Wrapper(_) = make_sure_non_zero_coin(coin);
}

#[test_only] // 僅供測試使用的輔助函式
fun make_coin_zero(coin: &mut Wrapper) {
    coin.0 = 0;
}

#[test, expected_failure(abort_code = ECoinIsZero)]
fun make_sure_zero_coin_fails2() {
    let mut coin = Wrapper(10);
    coin.make_coin_zero();
    let Wrapper(_) = make_sure_non_zero_coin(coin);
}
```

### 執行測試 (Running Tests) {#running-tests}

接著，你可以使用 `move test` 指令執行這些測試：

```bash
$ sui move test
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING test_example
Running Move unit tests
[ PASS    ] 0x0::my_module::make_sure_non_zero_coin_passes
[ PASS    ] 0x0::my_module::make_sure_zero_coin_fails
[ PASS    ] 0x0::my_module::make_sure_zero_coin_fails2
Test result: OK. Total tests: 3; passed: 3; failed: 0
```

### 使用測試旗標 (Using Test Flags) {#using-test-flags}

#### 傳遞要執行的特定測試 (Passing specific tests to run) {#passing-specific-tests-to-run}

你可以使用 `sui move test <str>` 執行特定測試或一組測試。這只會執行完整限定名稱中包含 `<str>` 的測試。例如，若我們只想執行名稱中含有 `"non_zero"` 的測試：

```bash
$ sui move test non_zero
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING test_example
Running Move unit tests
[ PASS    ] 0x0::my_module::make_sure_non_zero_coin_passes
Test result: OK. Total tests: 1; passed: 1; failed: 0
```

#### gas 上限 `-i <bound>` 或 `--gas_used <bound>` (`-i <bound>` or `--gas_used <bound>`) {#i-bound-or---gas_used-bound}

這會將任何單一測試可消耗的 gas 數量限制為 `<bound>`：

```bash
$ sui move test -i 0
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING test_example
Running Move unit tests
[ TIMEOUT ] 0x0::my_module::make_sure_non_zero_coin_passes
[ FAIL    ] 0x0::my_module::make_sure_zero_coin_fails
[ FAIL    ] 0x0::my_module::make_sure_zero_coin_fails2

Test failures:

Failures in 0x0::my_module:

┌── make_sure_non_zero_coin_passes ──────
│ Test timed out
└──────────────────


┌── make_sure_zero_coin_fails ──────
│ error[E11001]: test failure
│    ┌─ ./sources/my_module.move:22:27
│    │
│ 21 │     fun make_sure_zero_coin_fails() {
│    │         ------------------------- In this function in 0x0::my_module
│ 22 │         let coin = MyCoin(0);
│    │                           ^ Test did not error as expected. Expected test to abort with code 0 <SNIP>
│
│
└──────────────────


┌── make_sure_zero_coin_fails2 ──────
│ error[E11001]: test failure
│    ┌─ ./sources/my_module.move:34:31
│    │
│ 33 │     fun make_sure_zero_coin_fails2() {
│    │         -------------------------- In this function in 0x0::my_module
│ 34 │         let mut coin = MyCoin(10);
│    │                               ^^ Test did not error as expected. Expected test to abort with code 0 <SNIP>
│
│
└──────────────────

Test result: FAILED. Total tests: 3; passed: 0; failed: 3
```

#### 統計資料 `-s` 或 `--statistics` (`-s` or `--statistics`) {#s-or---statistics}

使用這些旗標，你可以收集已執行測試的統計資料，並報告每項測試的執行時間與使用的 gas。你還可以額外加入 `csv`（`sui move test -s csv`），以 csv 輸出格式取得 gas 使用量。例如，若我們想查看上述範例中測試的統計資料：

```bash
$ sui move test -s
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING test_example
Running Move unit tests
[ PASS    ] 0x0::my_module::make_sure_non_zero_coin_passes
[ PASS    ] 0x0::my_module::make_sure_zero_coin_fails
[ PASS    ] 0x0::my_module::make_sure_zero_coin_fails2

Test Statistics:

┌────────────────────────────────────────────────┬────────────┬───────────────────────────┐
│                   Test Name                    │    Time    │         Gas Used          │
├────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ 0x0::my_module::make_sure_non_zero_coin_passes │   0.001    │             1             │
├────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ 0x0::my_module::make_sure_zero_coin_fails      │   0.001    │             1             │
├────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ 0x0::my_module::make_sure_zero_coin_fails2     │   0.001    │             1             │
└────────────────────────────────────────────────┴────────────┴───────────────────────────┘

Test result: OK. Total tests: 3; passed: 3; failed: 0
```
