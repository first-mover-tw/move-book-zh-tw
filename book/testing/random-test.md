---
description: '使用 #[random_test] 在 Move (Move) 中進行基於屬性的測試：以隨機輸入執行測試，自動找出邊界案例。'
title: 隨機輸入 (Random Inputs)
keywords:
  - Move
  - Sui
  - Move tutorial
  - random
  - inputs
questions:
  - What is Random Inputs in Move?
  - How do I use Random Inputs in Move?
  - What is Basic Usage in Move?
  - What is Supported Types in Move?
answer: 'Property-based testing in Move with #[random_test]: run tests with randomized inputs to discover edge cases automatically.'
goal:
  description: 'Reader understands property-based testing in Move with #[random_test]: run tests with randomized inputs to discover edge cases automatically'
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

# 隨機輸入 (Random Inputs) {#random-inputs}

Move 編譯器支援透過 `#[random_test]`
屬性，以隨機產生的輸入執行測試。這可啟用以屬性為基礎的測試，讓測試使用隨機
產生的值執行多次，以找出你可能不會想到要手動測試的邊界案例。

> `#[random_test]` 屬性是用於測試輸入的編譯器功能，與用於鏈上隨機性的
> `sui::random` 模組不同。

## 基本用法 (Basic Usage) {#basic-usage}

使用 `#[random_test]` 標記函式，並以基本型別宣告參數。執行測試時，測試執行器
會為每個參數產生隨機值。

```move
module book::math;

public fun safe_add(a: u64, b: u64): u64 {
    if (a > 0xFFFFFFFFFFFFFFFF - b) {
        0xFFFFFFFFFFFFFFFF // 在最大值飽和
    } else {
        a + b
    }
}

#[random_test]
fun test_safe_add_never_overflows(a: u64, b: u64) {
    let result = safe_add(a, b);
    // 結果應始終 >= 兩個輸入值（不會因溢位而環繞）
    assert!(result >= a && result >= b);
}
```

## 支援的型別 (Supported Types) {#supported-types}

隨機輸入適用於所有基本型別：

| 型別                                      | 產生範圍                   |
| ----------------------------------------- | -------------------------- |
| `u8`, `u16`, `u32`, `u64`, `u128`, `u256` | 型別的完整範圍             |
| `bool`                                    | `true` 或 `false`          |
| `address`                                 | 隨機的 32 位元組地址       |
| `vector<T>`                               | 具有隨機元素的隨機長度向量 |

注意：`vector<T>` 中的 `T` 必須是基本型別或另一個向量（例如 `vector<vector<u8>>`）。

## 實務技巧 (Practical Tips) {#practical-tips}

**限制大型整數**：若你的函式預期接收較小的值，請使用較小的型別並進行轉型：

```move
#[random_test]
fun test_with_bounded_input(small: u8) {
    let bounded = (small as u64) % 100; // 0-99 範圍
    // ... 使用受限值進行測試
}
```

**避免未受限的向量**：`vector<u8>` 可能產生非常大的向量，導致測試緩慢或 gas
錯誤。建議使用固定大小的輸入，或手動建立向量：

```move
// 避免：可能產生巨大的向量
#[random_test]
fun test_bad(v: vector<u8>) { /* ... */ }

// 較佳：控制大小
#[random_test]
fun test_good(a: u8, b: u8, c: u8) {
    let v = vector[a, b, c];
    // ... 使用已知大小的向量進行測試
}
```

**補充而非取代**：隨機測試可找出未預期的邊界案例，但可能遺漏特定
情境。請搭配針對性的單元測試使用：

```move
use std::unit_test::assert_eq;

// 針對特定案例的測試
#[test]
fun test_add_zero() {
    assert_eq!(safe_add(std::u64::max_value!(), 0), std::u64::max_value!());
}

// 用於一般屬性的隨機測試
#[random_test]
fun test_add_commutative(a: u64, b: u64) {
    assert_eq!(safe_add(a, b), safe_add(b, a));
}
```

**使用 `assert_eq!` 以利偵錯**：隨機測試失敗時，你需要知道是哪組值
造成失敗。使用 [`assert_eq!`](./test-utilities.md#assert_eq-and-assert_ref_eq) 會在
失敗時印出兩個比較的值，使重現及偵錯問題更容易：

```move
use std::unit_test::assert_eq;

#[random_test]
fun test_double(value: u64) {
    let doubled = value * 2; // 這可能溢位，但為了簡潔起見，我們省略檢查。
    // 失敗時會印出："Assertion failed: <actual> != <expected>"
    assert_eq!(doubled / 2, value);
}
```

## 控制測試執行 (Controlling Test Runs) {#controlling-test-runs}

### 迭代次數 (Number of iterations) {#number-of-iterations}

預設情況下，隨機測試會使用不同輸入執行多次。使用 `--rand-num-iters` 控制
每個隨機測試執行的迭代次數：

```bash
# 每個隨機測試執行 100 次
sui move test --rand-num-iters 100
```

### 可重現的種子 (Reproducible seeds) {#reproducible-seeds}

隨機測試失敗時，輸出會包含種子以及重現方式：

```
┌── test_that_failed ────── (seed = 2033439370411573084)
│ ...
│ 此測試使用隨機產生的輸入。請使用 `test test_that_failed --seed 2033439370411573084` 重新執行，以重現此測試失敗。
│
└──────────────────
```

使用提供的種子重現完全相同的失敗：

```bash
sui move test test_that_failed --seed 2033439370411573084
```

## 限制 (Limitations) {#limitations}

- **無範圍限制**：你無法直接將隨機值限制為特定範圍；請如上所示使用模數
  或型別轉型
- **向量大小**：無法控制產生的向量長度

## 總結 (Summary) {#summary}

- 使用 `#[random_test]`（不是 `#[test]`）為測試函式啟用隨機輸入
- 參數必須是基本型別或基本型別的向量
- 使用較小的型別和轉型來限制輸入，以避免極端值
- 使用 `assert_eq!` 以取得更佳的失敗診斷資訊
- 使用 `--rand-num-iters` 控制迭代次數，並使用 `--seed` 重現失敗
- 使用隨機測試來補充而非取代針對性的單元測試
