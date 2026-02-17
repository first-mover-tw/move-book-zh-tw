---
description: "使用 #[random_test] 在 Move 中進行基於屬性的測試 (property-based testing)：使用隨機輸入執行測試以自動發現邊緣案例。"
---

# 隨機輸入 (Random Inputs)

Move 編譯器支援透過 `#[random_test]` 屬性使用隨機輸入執行測試。這啟用了基於屬性的測試，其中測試會使用隨機生成的值多次執行，以發現你可能沒想到要手動測試的邊緣案例。

> `#[random_test]` 屬性是用於測試輸入的編譯器功能，與用於鏈上隨機性的 `sui::random` 模組不同。

## 基本用法

用 `#[random_test]` 標記函式並宣告原始型別 (primitive types) 的參數。測試執行器在執行測試時會為每個參數生成隨機值。

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
    // 結果應始終 >= 兩個輸入 (沒有溢位繞回)
    assert!(result >= a && result >= b);
}
```

## 支援的型別

隨機輸入適用於所有原始型別：

| 型別 | 生成範圍 |
| ----------------------------------------- | ----------------------------------------- |
| `u8`, `u16`, `u32`, `u64`, `u128`, `u256` | 該型別的完整範圍 |
| `bool` | `true` 或 `false` |
| `address` | 隨機 32 位元組地址 |
| `vector<T>` | 隨機長度的向量，包含隨機元素 |

注意：`vector<T>` 中的 `T` 必須是原始型別或另一個向量 (例如，`vector<vector<u8>>`)。

## 實用技巧

**限制大整數**：如果你的函式預期較小的值，請使用較小的型別並進行轉型：

```move
#[random_test]
fun test_with_bounded_input(small: u8) {
    let bounded = (small as u64) % 100; // 0-99 範圍
    // ... 使用受限值進行測試
}
```

**避免無界向量**：`vector<u8>` 可能生成非常大的向量，導致測試緩慢或 Gas 錯誤。優先選擇固定大小的輸入或手動建構向量：

```move
// 避免：可能生成巨大的向量
#[random_test]
fun test_bad(v: vector<u8>) { /* ... */ }

// 更好：控制大小
#[random_test]
fun test_good(a: u8, b: u8, c: u8) {
    let v = vector[a, b, c];
    // ... 使用已知大小的向量進行測試
}
```

**補充而非取代**：隨機測試可以發現意想不到的邊緣案例，但可能會遺漏特定情境。將它們與針對性的單元測試一起使用：

```move
use std::unit_test::assert_eq;

// 針對特定情況的測試
#[test]
fun test_add_zero() {
    assert_eq!(safe_add(std::u64::max(), 0), std::u64::max());
}

// 針對一般屬性的隨機測試
#[random_test]
fun test_add_commutative(a: u64, b: u64) {
    assert_eq!(safe_add(a, b), safe_add(b, a));
}
```

**使用 `assert_eq!` 以便更好地除錯**：當隨機測試失敗時，你需要知道哪些值導致了失敗。使用 [`assert_eq!`](./test-utilities.md#assert_eq-and-assert_ref_eq) 會在失敗時列印出兩個比較值，使重現和除錯問題變得更容易：

```move
use std::unit_test::assert_eq;

#[random_test]
fun test_double(value: u64) {
    let doubled = value * 2; // 這可能會溢位，但為了簡潔我們省略了檢查。
    // 失敗時列印: "Assertion failed: <actual> != <expected>"
    assert_eq!(doubled / 2, value);
}
```

## 控制測試運行

### 迭代次數

預設情況下，隨機測試會使用不同的輸入運行多次。使用 `--rand-num-iters` 來控制每個隨機測試運行的迭代次數：

```bash
# 每個隨機測試運行 100 次
sui move test --rand-num-iters 100
```

### 可重現的種子 (Reproducible seeds)

當隨機測試失敗時，輸出包含種子和重現說明：

```
┌── test_that_failed ────── (seed = 2033439370411573084)
│ ...
│ This test uses randomly generated inputs. Rerun with
│ `sui move test test_that_failed --seed 2033439370411573084`
│ to recreate this test failure.
└──────────────────
```

使用提供的種子來重現確切的失敗：

```bash
sui move test test_that_failed --seed 2033439370411573084
```

## 限制

- **無範圍約束**：你不能直接將隨機值限制在特定範圍內；如上所示使用模數運算 (modulo) 或型別轉型
- **向量大小**：無法控制生成的向量長度

## 總結

- 使用 `#[random_test]` (而非 `#[test]`) 為測試函式啟用隨機輸入
- 參數必須是原始型別或原始型別的向量
- 使用較小的型別和轉型來限制輸入，以避免極端值
- 使用 `assert_eq!` 以獲得更好的失敗診斷
- 使用 `--rand-num-iters` 控制迭代次數，並使用 `--seed` 重現失敗
- 使用隨機測試來補充，而不是取代針對性的單元測試
