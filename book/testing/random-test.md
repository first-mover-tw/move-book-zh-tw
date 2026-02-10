---
description: "基於屬性的測試在 Move 中使用 #[random_test]：使用隨機化輸入執行測試，以自動發現邊界情況。"
---

# 隨機輸入 (Random Inputs)

Move 編譯器支援透過 `#[random_test]` 屬性以隨機化輸入執行測試。這啟用了基於屬性的測試，其中測試以隨機產生的值執行多次，以發現您可能不會想到手動測試的邊界情況。

> `#[random_test]` 屬性是編譯器的測試輸入功能，與用於鏈上隨機性的 `sui::random` 模組不同。

## 基本用法 (Basic Usage)

使用 `#[random_test]` 標記函式並宣告基本型別的參數。測試執行器將在測試執行時為每個參數產生隨機值。

```move
module book::math;

// 安全加法函式，防止溢位
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
    // 結果應該始終 >= 兩個輸入（無溢位換行）
    assert!(result >= a && result >= b);
}
```

## 支援的型別 (Supported Types)

隨機輸入適用於所有基本型別：

| 型別                                       | 產生的範圍                           |
| ----------------------------------------- | ----------------------------------------- |
| `u8`, `u16`, `u32`, `u64`, `u128`, `u256` | 該型別的完整範圍                    |
| `bool`                                    | `true` 或 `false`                         |
| `address`                                 | 隨機 32 位元組地址                    |
| `vector<T>`                               | 隨機長度向量及隨機元素 |

注意：`vector<T>` 中的 `T` 必須是基本型別或另一個向量（例如 `vector<vector<u8>>`）。

## 實用技巧 (Practical Tips)

**限制大整數**：如果您的函式預期小值，使用較小的型別並轉換：

```move
#[random_test]
fun test_with_bounded_input(small: u8) {
    let bounded = (small as u64) % 100; // 0-99 範圍
    // ... 使用有界值進行測試
}
```

**避免無界向量**：`vector<u8>` 可以產生非常大的向量，導致測試緩慢或燃料錯誤。更傾向於固定大小輸入或手動構造向量：

```move
// 避免：可能產生巨大向量
#[random_test]
fun test_bad(v: vector<u8>) { /* ... */ }

// 更好：控制大小
#[random_test]
fun test_good(a: u8, b: u8, c: u8) {
    let v = vector[a, b, c];
    // ... 使用已知大小的向量進行測試
}
```

**補充，不是取代**：隨機測試發現意外的邊界情況，但可能會遺漏特定場景。與有針對性的單元測試一起使用：

```move
use std::unit_test::assert_eq;

// 特定情況的有針對性測試
#[test]
fun test_add_zero() {
    assert_eq!(safe_add(std::u64::max(), 0), std::u64::max());
}

// 一般屬性的隨機測試
#[random_test]
fun test_add_commutative(a: u64, b: u64) {
    assert_eq!(safe_add(a, b), safe_add(b, a));
}
```

**使用 `assert_eq!` 獲得更好的除錯**：當隨機測試失敗時，您需要知道哪些值導致失敗。使用 [`assert_eq!`](./test-utilities.md#assert_eq-and-assert_ref_eq) 會在失敗時列印兩個比較值，使重現和除錯問題更容易：

```move
use std::unit_test::assert_eq;

#[random_test]
fun test_double(value: u64) {
    let doubled = value * 2; // 這可能溢位，但為簡潔起見我們省略檢查。
    // 失敗時，列印："斷言失敗：<實際值> != <預期值>"
    assert_eq!(doubled / 2, value);
}
```

## 控制測試執行 (Controlling Test Runs)

### 迭代次數 (Number of iterations)

預設情況下，隨機測試以不同的輸入執行多次。使用 `--rand-num-iters` 控制每個隨機測試執行的迭代次數：

```bash
# 執行每個隨機測試 100 次
sui move test --rand-num-iters 100
```

### 可重現的種子 (Reproducible seeds)

當隨機測試失敗時，輸出包括種子和重現的指示：

```
┌── test_that_failed ────── (seed = 2033439370411573084)
│ ...
│ 此測試使用隨機產生的輸入。重新執行時，使用
│ `sui move test test_that_failed --seed 2033439370411573084`
│ 以重現此測試失敗。
└──────────────────
```

使用提供的種子重現確切的失敗：

```bash
sui move test test_that_failed --seed 2033439370411573084
```

## 限制 (Limitations)

- **無範圍限制**：您不能直接將隨機值限制在特定範圍；如上所示，使用模數或型別轉換
- **向量大小**：無法控制產生的向量長度

## 摘要 (Summary)

- 使用 `#[random_test]`（不是 `#[test]`）啟用測試函式的隨機化輸入
- 參數必須是基本型別或基本型別的向量
- 使用較小的型別和轉換來限制輸入，避免極端值
- 使用 `assert_eq!` 獲得更好的失敗診斷
- 使用 `--rand-num-iters` 控制迭代，使用 `--seed` 重現失敗
- 使用隨機測試補充而不是取代有針對性的單元測試
