# 測試 (Testing)

測試是軟體開發中至關重要的一環，尤其是在安全性與正確性至上的區塊鏈應用中。在本節中，我們將介紹 Move 測試的基礎知識，包括如何有效地編寫和組織測試。

## `#[test]` 屬性

Move 中的測試是標記有 `#[test]` 屬性的函式。此屬性告訴編譯器該函式是一個測試函式，應該在執行測試時運行。測試函式是普通函式，但它們必須不接收任何參數且沒有傳回值。它們會從位元組碼中排除，且永遠不會被發佈。

```move
module book::testing;

#[test_only]
use std::unit_test::assert_eq;

// test 屬性放置在 `fun` 關鍵字之前（可以放在上方，
// 也可以直接放在 `fun` 關鍵字之前，如 `#[test] fun my_test() { ... }`）
// 在此範例中，測試的名稱將是 `book::testing::simple_test`。
#[test]
fun simple_test() {
    let sum = 2 + 2;
    assert_eq!(sum, 4);
}

// 此測試的名稱將是 `book::testing::more_advanced_test`。
#[test] fun more_advanced_test() {
    let sum = 2 + 2 + 2;
    assert_eq!(sum, 4);
}
```

## 執行測試

要執行測試，您可以使用 `sui move test` 指令。此指令會首先在 **測試模式** 下編譯套件，然後執行套件中找到的所有測試。在測試模式下，`sources/` 和 `tests/` 目錄中的模組都會被處理並執行其中的測試。

```bash
$ sui move test
> UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
> INCLUDING DEPENDENCY Bridge
> INCLUDING DEPENDENCY DeepBook
> INCLUDING DEPENDENCY SuiSystem
> INCLUDING DEPENDENCY Sui
> INCLUDING DEPENDENCY MoveStdlib
> BUILDING book
> Running Move unit tests
> ...
```

<!-- TODO: fill output -->

## 使用 `#[expected_failure]` 測試失敗情況

針對預期失敗的情況，可以使用 `#[expected_failure]` 標記測試。當此屬性添加到 `#[test]` 函式時，會告訴編譯器該測試預期會失敗。當您想測試某個函式在滿足特定條件時是否會失敗，這非常有用。

> 注意：此屬性只能添加到 `#[test]` 函式。

該屬性可以接收一個參數，指定測試失敗時預期傳回的中斷程式碼 (abort code)。如果測試傳回的中斷程式碼與參數中指定的不符，測試將失敗。同樣地，如果執行沒有導致中斷，測試也會失敗。

```move
module book::testing_failure;

const EInvalidArgument: u64 = 1;

#[test]
#[expected_failure(abort_code = 0)]
fun test_fail() {
    abort 0 // 以程式碼 0 中斷
}

// 屬性可以組合在一起
#[test, expected_failure(abort_code = EInvalidArgument)]
fun test_fail_1() {
    abort EInvalidArgument // 以程式碼 EInvalidArgument 中斷
}
```

`abort_code` 參數可以使用測試模組中定義的常數，也可以從其他模組匯入。這是常數唯一可以在其他模組中被使用和「存取」的情況。

## 使用 `#[test_only]` 提供測試工具

在某些情況下，讓測試環境能夠存取某些內部函式或功能會很有幫助。這可以簡化測試過程並實現更徹底的測試。然而，重要的是要記住，這些函式不應包含在最終發佈的套件中。這就是 `#[test_only]` 屬性派上用場的地方。

```move
module book::testing;

#[test_only]
use std::unit_test::assert_eq;

// 使用了 `secret` 函式的公開函式。
public fun multiply_by_secret(x: u64): u64 {
    x * secret()
}

/// 不對外公開的私有函式。
fun secret(): u64 { 100 }

#[test_only]
/// 此函式僅供測試目的使用，可用於測試及其他僅限測試的函式中。
/// 注意可見性 — 對於 `#[test_only]`，通常使用 `public` 可見性。
public fun secret_for_testing(): u64 {
    secret()
}

#[test]
// 在測試環境中，我們可以存取 `secret_for_testing` 函式。
fun test_multiply_by_secret() {
    let expected = secret_for_testing() * 2;
    assert_eq!(multiply_by_secret(2), expected);
}
```

標記為 `#[test_only]` 的函式將對測試環境開放，如果其可見性設為 `public`，則也會對其他模組開放。

## 延伸閱讀

- Move 參考手冊中的 [單元測試 (Unit Testing)](/reference/unit-testing)。
