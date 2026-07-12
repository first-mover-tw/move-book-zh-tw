---
title: 單元測試 (Unit Tests) | 參考手冊
description:
  Move 單元測試參考手冊 (Move Unit Testing Reference)：`#[test]`、`#[expected_failure]`、`#[test_only]`
  標註 (annotations)、測試旗標 (test flags) 與執行選項 (execution options)。
---

# 單元測試 (Unit Tests) {#unit-tests}

Move 的單元測試在 Move 原始語言中使用三種標註（annotations）：

- `#[test]` 將函式標記為測試；
- `#[expected_failure]` 標記測試預期會失敗；
- `#[test_only]` 將模組或模組成員 ([`use`](./uses)、[函式](./functions)、[結構體](./structs) 或 [常數](./constants)) 標記為僅用於測試的程式碼。

這些標註可以放置在任何具備適當形式和能見度的項目上。每當模組或模組成員被標註為 `#[test_only]` 或 `#[test]` 時，它將不會包含在編譯後的位元組碼中，除非是為了測試而編譯。

## 測試標註 (Test Annotations) {#test-annotations}

`#[test]` 標註只能放置在沒有參數的函式上。此標註將函式標記為由單元測試框架執行的測試。

```move
#[test] // 有效
fun this_is_a_test() { ... }

#[test] // 由於測試接受參數，將導致編譯失敗
fun this_is_not_correct(arg: u64) { ... }
```

測試也可以標註為 `#[expected_failure]`。此標註標記該測試預期會引發錯誤。`#[expected_failure]` 標註有多個選項可用，以確保只有符合特定條件的失敗才會被標記為通過，這些選項詳見 [預期失敗](#expected-failures)。只有具有 `#[test]` 標註的函式才能同時標註為 `#[expected_failure]`。

以下是一些使用 `#[expected_failure]` 標註的簡單範例：

```move
#[test, expected_failure]
public fun this_test_will_abort_and_pass() { abort 1 }

#[test, expected_failure]
public fun test_will_error_and_pass() { 1/0; }

// 由於測試失敗且符合預期的中止代碼常數，因此會通過。
// ENotFound 是模組中定義的常數。
#[test, expected_failure(abort_code = ENotFound)]
public fun test_will_error_and_pass_abort_code() { abort ENotFound }

// 由於測試失敗的原因與預期不同，因此會失敗。
#[test, expected_failure(abort_code = my_module::ENotFound)]
public fun test_will_error_and_fail() { 1/0; }

#[test, expected_failure] // 一個屬性中可以有多個標註。此測試將通過。
public fun this_other_test_will_abort_and_pass() { abort 1 }
```

> **注意**：標註了 `#[test]` 和 `#[test_only]` 的函式也可以呼叫 [`entry`](./functions#entry-modifier) 函式，無論其能見度如何。

## 預期失敗 (Expected Failures) {#expected-failures}

你可以透過多種不同方式使用 `#[expected_failure]` 標註來指定不同型別的錯誤條件。它們是：

### 1. `#[expected_failure(abort_code = <constant>)]` {#1-expected_failureabort_code-constant}

如果測試在定義該常數的模組中以指定的常數值中止，則測試通過，否則失敗。這是測試預期失敗的推薦方式。

> **注意**：你可以在 `expected_failure` 標註中參考目前模組或套件之外的常數。

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

    // 失敗：由於我們預期的是來自錯誤模組的常數，因此不會通過。
    #[test, expected_failure(abort_code = ENotFound)]
    fun test_will_abort_and_pass() { other_module::will_abort() }
}
```

### 2. `#[expected_failure(arithmetic_error, location = <location>)]` {#2-expected_failurearithmetic_error-location-location}

指定測試預期在指定位置發生算術錯誤（例如整數溢位、除以零等）。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

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

    // 失敗：由於預期發生失敗的位置與實際發生失敗的位置不同，因此失敗。
    #[test, expected_failure(arithmetic_error, location = Self)]
    fun test_will_arith_error_and_fail() { other_module::will_arith_error() }
}
```

### 3. `#[expected_failure(out_of_gas, location = <location>)]` {#3-expected_failureout_of_gas-location-location}

指定測試預期在指定位置發生燃氣耗盡（out of gas）錯誤。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。

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

    // 失敗：由於預期發生失敗的位置與實際發生失敗的位置不同，因此失敗。
    #[test, expected_failure(out_of_gas, location = Self)]
    fun test_will_oog_and_fail() { other_module::will_oog() }
}
```

### 4. `#[expected_failure(vector_error, minor_status = <u64_opt>, location = <location>)]` {#4-expected_failurevector_error-minor_status-u64_opt-location-location}

指定測試預期在指定位置發生向量（vector）錯誤，並具有給定的 `minor_status`（如果有提供）。`<location>` 必須是指向模組位置的有效路徑，例如 `Self` 或 `my_package::my_module`。`<u64_opt>` 是一個選填參數，用於指定向量錯誤的次要狀態（minor status）。如果未指定，則只要測試發生任何次要狀態的向量錯誤，測試即通過。如果已指定，則僅當測試發生具有指定次要狀態的向量錯誤時，測試才通過。

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

    // 可以指定預期的次要狀態（即向量特定的錯誤代碼）。
    #[test, expected_failure(vector_error, minor_status = 1, location = Self)]
    fun native_abort_good_right_code() {
        vector::borrow(&vector<u64>[], 1);
    }

    // 失敗：錯誤正確，但位置錯誤。
    #[test, expected_failure(vector_error, location = pkg_addr::other_module)]
    fun vector_abort_same_module() {
        other_module::vector_borrow_empty();
    }

    // 失敗：錯誤和位置正確，但次要狀態不同，因此測試失敗。
    #[test, expected_failure(vector_error, minor_status = 0, location = Self)]
    fun vector_abort_wrong_minor_code() {
        vector::borrow(&vector<u64>[], 1);
    }
}
```

### 5. `#[expected_failure]` {#5-expected_failure}

如果測試以 _任何_ 錯誤代碼中止，測試即通過。在使用此方式標註預期失敗時，你應該 **_極其小心_**，並應始終優先選擇上述描述的其他方式。這類標註的範例如下：

```move
#[test, expected_failure]
fun test_will_abort_and_pass1() { abort 1 }

#[test, expected_failure]
fun test_will_arith_error_and_pass2() { 1/0; }
```

## 僅限測試標註 (Test Only Annotations) {#test-only-annotations}

模組及其任何成員都可以宣告為「僅限測試」。如果一個項目被標註為 `#[test_only]`，則該項目僅在測試模式下編譯時才會包含在編譯後的 Move 位元組碼中。此外，在非測試模式下編譯時，任何對 `#[test_only]` 模組的非測試 `use` 都會在編譯期間引發錯誤。

> **注意**：標註了 `#[test_only]` 的函式僅能從測試程式碼中呼叫，但它們本身不是測試，也不會由單元測試框架作為測試執行。

```move
#[test_only] // 僅限測試屬性可以附加到模組
module abc { ... }

#[test_only] // 僅限測試屬性可以附加到常數
const MY_ADDR: address = @0x1;

#[test_only] // .. 到使用 (use)
use pkg_addr::some_other_module;

#[test_only] // .. 到結構體 (struct)
public struct SomeStruct { ... }

#[test_only] // .. 以及函式。只能從測試代碼呼叫，但這本身 _不是_ 測試！
fun test_only_function(...) { ... }
```

## 執行單元測試 (Running Unit Tests) {#running-unit-tests}

使用 `sui move test` 指令為 [Move 套件](./packages) 執行單元測試。

執行測試時，每個測試結果將是 `PASS`（通過）、`FAIL`（失敗）或 `TIMEOUT`（逾時）。如果測試案例失敗，則會盡可能報告失敗的位置以及導致失敗的函式名稱。你可以在下面看到相關範例。

如果測試超過了任何單個測試可以執行的指令數量上限，則會被標記為逾時。可以使用下面介紹的選項更改此限制。此外，雖然測試結果始終是確定性的（deterministic），但預設情況下測試是並行執行的，因此除非使用單個執行緒執行（可透過選項配置），否則測試執行中測試結果的順序是非確定性的。

上述選項只是眾多用於微調測試和幫助除錯失敗測試的選項中的兩個。要查看所有可用選項及其說明，請向 `sui move test` 指令傳遞 `--help` 標記：

```
$ sui move test --help
```

## 範例 (Example) {#example}

以下範例顯示了一個使用部分單元測試功能的簡單模組：

首先建立一個空套件並切換到該目錄：

```bash
$ sui move new test_example; cd test_example
```

接下來在 `sources` 目錄下新增以下模組：

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
// 或者如果我們不關心中止代碼，則使用 #[test, expected_failure]
fun make_sure_zero_coin_fails() {
    let coin = Wrapper(0);
    let Wrapper(_) = make_sure_non_zero_coin(coin);
}

#[test_only] // 僅限測試輔助函式
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

然後你可以使用 `move test` 指令執行這些測試：

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

### 使用測試標記 (Using Test Flags) {#using-test-flags}

#### 指定要執行的特定測試 (Passing specific tests to run) {#passing-specific-tests-to-run}

你可以使用 `sui move test <str>` 執行特定的測試或一組測試。這將僅執行其完全限定名稱包含 `<str>` 的測試。例如，如果我們只想執行名稱中包含 `"non_zero"` 的測試：

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

這會限制任何單一測試可以消耗的燃氣量為 `<bound>`：

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
│    │         ------------------------- 在 0x0::my_module 的此函式中
│ 22 │         let coin = MyCoin(0);
│    │                           ^ 測試未按預期出錯。預期測試以代碼 0 中止 <部分截斷>
│
│
└──────────────────


┌── make_sure_zero_coin_fails2 ──────
│ error[E11001]: test failure
│    ┌─ ./sources/my_module.move:34:31
│    │
│ 33 │     fun make_sure_zero_coin_fails2() {
│    │         -------------------------- 在 0x0::my_module 的此函式中
│ 34 │         let mut coin = MyCoin(10);
│    │                               ^^ 測試未按預期出錯。預期測試以代碼 0 中止 <部分截斷>
│
│
└──────────────────

Test result: FAILED. Total tests: 3; passed: 0; failed: 3
```

#### `-s` 或 `--statistics` (`-s` or `--statistics`) {#s-or---statistics}

透過這些標記，你可以收集有關執行測試的統計資訊，並報告每個測試的執行時間和耗用的燃氣量。你還可以新增 `csv`（`sui move test -s csv`）以獲得 CSV 輸出格式的燃氣使用情況。例如，如果我們想查看上述範例中測試的統計資訊：

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
