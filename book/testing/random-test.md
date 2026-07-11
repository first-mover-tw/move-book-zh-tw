---
description: 使用 `#[random_test]` 進行 Move 屬性測試 (Property-based testing in Move with
  `#[random_test]`)：以隨機輸入執行測試，自動發現邊界案例 (edge case)。
---

# 隨機輸入 (Random Inputs) {#random-inputs}

Move 編譯器支援透過 `#[random_test]` 屬性以隨機輸入執行測試。這讓基於屬性的測試（property-based testing）成為可能，測試會以隨機產生的值多次執行，藉此找出你可能想不到手動測試的邊界情況。

> `#[random_test]` 屬性是用於測試輸入的編譯器功能，與用於鏈上隨機性的 `sui::random` 模組是分開的。

## 基本用法 (Basic Usage) {#basic-usage}

用 `#[random_test]` 標記函式，並宣告基本型別的參數。測試執行器在測試執行時，會為每個參數產生隨機值。

```move
module book::math;

public fun safe_add(a: u64, b: u64): u64 {
    if (a > 0xFFFFFFFFFFFFFFFF - b) {
        0xFFFFFFFFFFFFFFFF // 在最大值處飽和 (saturate at max)
    } else {
        a + b
    }
}

#[random_test]
fun test_safe_add_never_overflows(a: u64, b: u64) {
    let result = safe_add(a, b);
    // 結果應該永遠 >= 兩個輸入值(不會發生溢位回繞)
    assert!(result >= a && result >= b);
}
```

## 支援的型別 (Supported Types) {#supported-types}

隨機輸入支援所有基本型別：

| 型別                                      | 產生範圍                   |
| ----------------------------------------- | -------------------------- |
| `u8`、`u16`、`u32`、`u64`、`u128`、`u256` | 該型別的完整範圍           |
| `bool`                                    | `true` 或 `false`          |
| `address`                                 | 隨機的 32 位元組位址       |
| `vector<T>`                               | 隨機長度、元素也隨機的向量 |

註：`vector<T>` 中的 `T` 必須是基本型別，或另一個向量（例如 `vector<vector<u8>>`）。

## 實用技巧 (Practical Tips) {#practical-tips}

**限制大整數範圍**：如果你的函式預期接收較小的值，使用較小的型別並轉型：

```move
#[random_test]
fun test_with_bounded_input(small: u8) {
    let bounded = (small as u64) % 100; // 0-99 範圍
    // ... 以受限值進行測試
}
```

**避免無限制的向量**：`vector<u8>` 可能會產生非常大的向量，導致測試變慢或發生 gas 錯誤。建議使用固定大小的輸入，或手動建構向量：

```move
// 避免：可能產生巨大的向量
#[random_test]
fun test_bad(v: vector<u8>) { /* ... */ }

// 較好：控制大小
#[random_test]
fun test_good(a: u8, b: u8, c: u8) {
    let v = vector[a, b, c];
    // ... 以已知大小的向量進行測試
}
```

**互補而非取代**：隨機測試能找出意料之外的邊界情況，但可能會漏掉特定情境。應搭配針對性的單元測試一起使用：

```move
use std::unit_test::assert_eq;

// 針對特定情境的測試
#[test]
fun test_add_zero() {
    assert_eq!(safe_add(std::u64::max_value!(), 0), std::u64::max_value!());
}

// 針對一般性質的隨機測試
#[random_test]
fun test_add_commutative(a: u64, b: u64) {
    assert_eq!(safe_add(a, b), safe_add(b, a));
}
```

**使用 `assert_eq!` 以獲得更好的除錯資訊**：當隨機測試失敗時，你需要知道是哪些值導致了失敗。使用 [`assert_eq!`](./test-utilities.md#assert_eq-and-assert_ref_eq) 會在失敗時印出兩個被比較的值，讓重現與除錯問題更容易：

```move
use std::unit_test::assert_eq;

#[random_test]
fun test_double(value: u64) {
    let doubled = value * 2; // 這可能會溢位，但為求簡潔我們省略了檢查。
    // 失敗時會印出："Assertion failed: <actual> != <expected>"
    assert_eq!(doubled / 2, value);
}
```

## 控制測試執行 (Controlling Test Runs) {#controlling-test-runs}

### 迭代次數 (Number of iterations) {#number-of-iterations}

預設情況下，隨機測試會以不同輸入執行多次。使用 `--rand-num-iters` 來控制每個隨機測試的執行次數：

```bash
# 讓每個隨機測試執行 100 次
sui move test --rand-num-iters 100
```

### 可重現的種子 (Reproducible seeds) {#reproducible-seeds}

當隨機測試失敗時，輸出內容會包含種子（seed）以及重現方式：

```
┌── test_that_failed ────── (seed = 2033439370411573084)
│ ...
│ This test uses randomly generated inputs. Rerun with `test test_that_failed --seed 2033439370411573084` to recreate this test failure.
│
└──────────────────
```

使用提供的種子來重現確切的失敗情況：

```bash
sui move test test_that_failed --seed 2033439370411573084
```

## 限制 (Limitations) {#limitations}

- **無範圍限制**：你無法直接將隨機值限制在特定範圍內；請如上所示使用取模（modulo）或型別轉型
- **向量大小**：無法控制產生的向量長度

## 總結 (Summary) {#summary}

- 使用 `#[random_test]`（而非 `#[test]`）來為測試函式啟用隨機化輸入
- 參數必須是基本型別或基本型別的向量
- 使用較小的型別並轉型來限制輸入，以避免極端值
- 使用 `assert_eq!` 以獲得更好的失敗診斷資訊
- 使用 `--rand-num-iters` 控制迭代次數，並用 `--seed` 重現失敗情況
- 使用隨機測試來互補而非取代針對性的單元測試
