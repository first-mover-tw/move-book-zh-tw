---
title: 單元測試 (Unit Tests) | 參考手冊
description:
  Move 單元測試參考手冊 (Move Unit Testing Reference)：`#[test]`、`#[expected_failure]`、`#[test_only]`
  標註 (annotations)、測試旗標 (test flags) 與執行選項 (execution options)。
---

# 單元測試 (Unit Tests) {#unit-tests}

Move 使用三種標註來對原始碼進行單元測試：

- `#[test]` 標記一個函式為測試；
- `#[expected_failure]` 標記一個測試預期會失敗；
- `#[test_only]` 標記一個模組或模組成員（[`use`](./uses)、[函式](./functions)、[結構](./structs)或[常數](./constants)）為僅供測試使用的程式碼。

這些標註可以放在任何具備適當可見性的形式上。每當一個模組或模組成員被標註為 `#[test_only]` 或 `#[test]` 時，除非是為了測試而編譯，否則它將不會被包含在編譯後的位元組碼中。

## 測試標註 (Test Annotations) {#test-annotations}

`#[test]` 標註只能放在沒有參數的函式上。這個標註標記該函式為單元測試框架要執行的測試。

```move
#[test] // OK
fun this_is_a_test() { ... }

#[test] // 因為 test 帶了參數，會編譯失敗
fun this_is_not_correct(arg: u64) { ... }
```

測試也可以用 `#[expected_failure]` 標註。這個標註標記該測試預期會拋出錯誤。可以搭配 `#[expected_failure]` 標註使用的選項有很多，確保只有符合指定條件的失敗才會被標記為通過，這些選項詳見[預期失敗 (Expected Failures)](#expected-failures)。只有已標註 `#[test]` 的函式才能同時標註為 `#[expected_failure]`。

以下是使用 `#[expected_failure]` 標註的幾個簡單範例：

```move
#[test, expected_failure]
public fun this_test_will_abort_and_pass() { abort 1 }

#[test, expected_failure]
public fun test_will_error_and_pass() { 1/0; }

// 因為 test 以預期的 abort code 常數失敗，所以會通過。
// ENotFound 是定義在該模組中的常數。
#[test, expected_failure(abort_code = ENotFound)]
public fun test_will_error_and_pass_abort_code() { abort ENotFound }

// 因為 test 以不同於預期的錯誤失敗，所以會失敗。
#[test, expected_failure(abort_code = my_module::ENotFound)]
public fun test_will_error_and_fail() { 1/0; }

#[test, expected_failure] // 一個屬性內可以有多個。這個 test 會通過。
public fun this_other_test_will_abort_and_pass() { abort 1 }
```

> **注意**：`#[test]` 與 `#[test_only]` 函式也可以呼叫[`entry`](./functions#entry-modifier)函式，無論其可見性為何。

## 預期失敗 (Expected Failures) {#expected-failures}

有多種不同的方法可以使用 `#[expected_failure]` 註解來指定不同型別的錯誤條件。這些方法有：

### 1. `#[expected_failure(abort_code = <constant>)]` {#1-expected_failureabort_code-constant}

如果測試在定義該常數的模組中以指定的常數值中止（abort），則此測試會通過，否則會失敗。這是測試預期測試失敗的建議方式。

> **注意**：你可以在 `expected_failure` 註解中參照目前模組或套件之外的常數。

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

    // 失敗：不會通過，因為我們期望的是來自錯誤模組的常數。
    #[test, expected_failure(abort_code = ENotFound)]
    fun test_will_abort_and_pass() { other_module::will_abort() }
}
```

### 2. `#[expected_failure(arithmetic_error, location = <location>)]` {#2-expected_failurearithmetic_error-location-location}

這指定了測試預期會在指定位置以算術錯誤（例如整數溢位、除以零等）失敗。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

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

    // 失敗：會失敗，因為我們期望的失敗位置與測試實際失敗的位置不同。
    #[test, expected_failure(arithmetic_error, location = Self)]
    fun test_will_arith_error_and_fail() { other_module::will_arith_error() }
}
```

### 3. `#[expected_failure(out_of_gas, location = <location>)]` {#3-expected_failureout_of_gas-location-location}

這指定了測試預期會在指定位置以耗盡 gas 的錯誤失敗。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

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

    // 失敗：會失敗，因為我們期望的失敗位置與測試實際失敗的位置不同。
    #[test, expected_failure(out_of_gas, location = Self)]
    fun test_will_oog_and_fail() { other_module::will_oog() }
}
```

### 4. `#[expected_failure(vector_error, minor_status = <u64_opt>, location = <location>)]` {#4-expected_failurevector_error-minor_status-u64_opt-location-location}

這指定了測試預期會在指定位置以給定的 `minor_status`（如有提供）發生向量錯誤而失敗。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。`<u64_opt>` 是一個選用參數，用於指定向量錯誤的次要狀態。如果未指定，只要測試以任何次要狀態失敗，測試就會通過。如果有指定，只有當測試以指定次要狀態的向量錯誤失敗時，測試才會通過。

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

    // 可以指定次要狀態（也就是向量特有的錯誤碼）作為預期。
    #[test, expected_failure(vector_error, minor_status = 1, location = Self)]
    fun native_abort_good_right_code() {
        vector::borrow(&vector<u64>[], 1);
    }

    // 失敗：正確的錯誤，但位置錯誤。
    #[test, expected_failure(vector_error, location = pkg_addr::other_module)]
    fun vector_abort_same_module() {
        other_module::vector_borrow_empty();
    }

    // 失敗：正確的錯誤和位置，但次要狀態不同，所以此測試會失敗。
    #[test, expected_failure(vector_error, minor_status = 0, location = Self)]
    fun vector_abort_wrong_minor_code() {
        vector::borrow(&vector<u64>[], 1);
    }
}
```

### 5. `#[expected_failure]` {#5-expected_failure}

只要測試以*任何*錯誤碼中止（abort），就會通過。使用此方式標註預期測試失敗時，你應該要**非常小心**，並且應優先使用上述描述的方式之一。以下是這類註解的範例：

```move
#[test, expected_failure]
fun test_will_abort_and_pass1() { abort 1 }

#[test, expected_failure]
fun test_will_arith_error_and_pass2() { 1/0; }
```

## 僅供測試的標註 (Test Only Annotations) {#test-only-annotations}

模組及其任何成員都可以宣告為僅供測試使用。如果某個項目被標註為
`#[test_only]`，該項目只會在測試模式下編譯時被包含進編譯後的 Move bytecode。此外，
在非測試模式下編譯時，任何對 `#[test_only]` 模組的非測試 `use` 都會在編譯期間引發錯誤。

> **注意**：被標註為 `#[test_only]` 的函式只能被測試程式碼呼叫，
> 但它們本身並不是測試，也不會被單元測試框架當作測試來執行。

```move
#[test_only] // test only 屬性可以附加在模組上
module abc { ... }

#[test_only] // test only 屬性可以附加在常數上
const MY_ADDR: address = @0x1;

#[test_only] // .. 也可以附加在 use 上
use pkg_addr::some_other_module;

#[test_only] // .. 也可以附加在結構上
public struct SomeStruct { ... }

#[test_only] // .. 以及函式。只能從 test 程式碼中呼叫，但這**不是** test！
fun test_only_function(...) { ... }
```

## 執行單元測試 (Running Unit Tests) {#running-unit-tests}

使用 `sui move test` 指令來執行 [Move package](./packages) 的單元測試。

執行測試時，每個測試都會標示為 `PASS`、`FAIL` 或 `TIMEOUT`。如果測試案例失敗，系統會盡可能回報失敗的位置以及導致失敗的函式名稱。你可以在下方看到範例。

如果測試超過任何單一測試可執行的最大指令數，該測試將被標記為逾時。這個上限可以透過下列選項調整。此外，雖然測試的結果永遠是確定性的，但測試預設會平行執行，因此除非設定成只用單一執行緒執行，否則測試執行結果的順序是不確定的，這可以透過選項來設定。

上述選項只是眾多可以微調測試、協助除錯失敗測試的選項中的兩個。若要查看所有可用選項及每個選項的說明，請在 `sui move test` 指令中加上 `--help` 旗標：

```
$ sui move test --help
```

## 範例 (Example) {#example}

以下範例展示了一個使用部分單元測試功能的簡單模組：

首先建立一個空的套件並切換到該目錄：

```bash
$ sui move new test_example; cd test_example
```

接著在 `sources` 目錄下新增以下模組：

```move
// filename: sources/my_module.move
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
// 或 #[test, expected_failure]，如果我們不在意 abort code
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

接著你可以用 `move test` 指令來執行這些測試：

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

#### 指定要執行的特定測試 (Passing specific tests to run) {#passing-specific-tests-to-run}

你可以透過 `sui move test <str>` 執行特定測試，或一組測試。這只會執行完整限定名稱中包含 `<str>` 的測試。例如，如果我們只想執行名稱中包含 `"non_zero"` 的測試：

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

#### `-i <bound>` 或 `--gas_used <bound>` (`-i <bound>` or `--gas_used <bound>`) {#i-bound-or---gas_used-bound}

這會限制任何單一測試可消耗的 gas 量為 `<bound>`：

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

#### `-s` 或 `--statistics` (`-s` or `--statistics`) {#s-or---statistics}

透過這些旗標，你可以收集測試執行的統計資料，並回報每個測試的執行時間與所使用的 gas。你也可以額外加上 `csv`（`sui move test -s csv`）以 csv 格式輸出 gas 使用量。例如，如果我們想查看上述範例中測試的統計資料：

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
