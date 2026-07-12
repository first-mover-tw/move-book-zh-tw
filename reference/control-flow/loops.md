---
title: 迴圈 (Loops) | 參考手冊
description:
  迴圈語法參考 (Loop Constructs Reference)：涵蓋 while 迴圈、loop 運算式、for 迴圈、break、continue
  以及走訪模式。
---

# Move 中的迴圈結構 (Loop Constructs in Move)

許多程式需要對值進行迭代，Move 提供了 `while` 和 `loop` 形式來讓你撰寫這類程式碼。此外，你還可以在執行期間使用 `break`（退出迴圈）和 `continue`（跳過本次迭代的剩餘部分並回到控制結構的最頂部）來修改這些迴圈的控制流。

## `while` 迴圈 (`while` Loops)

`while` 結構會重複執行其主體（型別為單元的運算式），直到條件（型別為 `bool` 的運算式）求值為 `false`。

以下是一個簡單的 `while` 迴圈範例，計算從 `1` 到 `n` 的數字之和：

```move
fun sum(n: u64): u64 {
    let mut sum = 0;
    let mut i = 1;
    while (i <= n) {
        sum = sum + i;
        i = i + 1
    };

    sum
}
```

也允許無限 `while` 迴圈：

```move
fun foo() {
    while (true) { }
}
```

> 使用巨集（Macros）代替迴圈是實現更簡潔、更具可讀性目的的更好方法。
> 本文僅以上述函式 `sum` 為例，來體會巨集函式的魅力：

```move
fun sum(n: u64): u64 {
    vector::tabulate!(n, |i| i + 1).fold!(0, |sum, num| sum + num)
}
```

### 在 `while` 迴圈內部使用 `break` (Using `break` Inside of `while` Loops)

在 Move 中，`while` 迴圈可以使用 `break` 提前退出。例如，假設我們正在尋找向量中某個值的位置，並且希望在找到它時 `break`：

```move
fun find_position(values: &vector<u64>, target_value: u64): Option<u64> {
    let size = values.length();
    let mut i = 0;
    let mut found = false;

    while (i < size) {
        if (values[i] == target_value) {
            found = true;
            break
        };
        i = i + 1
    };

    if (found) {
        option::some(i)
    } else {
        option::none<u64>()
    }
}
```

這裡，如果借用的向量值等於我們的目標值，我們將 `found` 標誌設為 `true` 並呼叫 `break`，這將導致程式退出迴圈。

最後，請注意 `while` 迴圈的 `break` 不能帶有值：`while` 迴圈始終傳回單元型別 `()`，因此 `break` 也是如此。

### 在 `while` 迴圈內部使用 `continue` (Using `continue` Inside of `while` Loops)

與 `break` 類似，Move 的 `while` 迴圈可以呼叫 `continue` 來跳過迴圈主體的一部分。如果未滿足條件，這允許我們跳過部分計算，如下例所示：

```move
fun sum_even(values: &vector<u64>): u64 {
    let size = values.length();
    let mut i = 0;
    let mut even_sum = 0;

    while (i < size) {
        let number = values[i];
        i = i + 1;
        if (number % 2 == 1) continue;
        even_sum = even_sum + number;
    };
    even_sum
}
```

這段程式碼將迭代提供的向量。對於每個條目，如果該條目是偶數，它會將其加到 `even_sum` 中。如果不是，它將呼叫 `continue`，跳過加法運算並回到 `while` 迴圈的條件檢查。

## `loop` 運算式 (`loop` Expressions)

`loop` 運算式重複執行迴圈主體（型別為 `()` 的運算式），直到遇到 `break`：

```move
fun sum(n: u64): u64 {
    let mut sum = 0;
    let mut i = 1;

    loop {
       i = i + 1;
       if (i >= n) break;
       sum = sum + i;
    };

    sum
}
```

如果沒有 `break`，迴圈將永遠持續下去。在下例中，程式將永遠執行，因為 `loop` 中沒有 `break`：

```move
fun foo() {
    let mut i = 0;
    loop { i = i + 1 }
}
```

### 在 `loop` 中使用帶值的 `break` (Using `break` with Values in `loop`)

與始終傳回 `()` 的 `while` 迴圈不同，`loop` 可以使用 `break` 傳回一個值。這樣一來，整個 `loop` 運算式的求值結果就是該型別的值。例如，我們可以使用 `loop` 和 `break` 重寫上面的 `find_position`，在找到索引時立即傳回：

```move
fun find_position(values: &vector<u64>, target_value: u64): Option<u64> {
    let size = values.length();
    let mut i = 0;

    loop {
        if (values[i] == target_value) {
            break option::some(i)
        } else if (i >= size) {
            break option::none()
        };
        i = i + 1;
    }
}
```

此迴圈將以選項（Option）結果中斷，並且作為函式主體中的最後一個運算式，將產生該值作為最終的函式結果。

### 在 `loop` 運算式內部使用 `continue` (Using `continue` Inside of `loop` Expressions)

如你所料，`continue` 也可以在 `loop` 內部使用。以下是使用 `loop` 配合 `break` 和 `continue` 而非 `while` 重寫的 `sum_even` 函式。

```move
fun sum_even(values: &vector<u64>): u64 {
    let size = values.length();
    let mut i = 0;
    let mut even_sum = 0;

    loop {
        if (i >= size) break;
        let number = values[i];
        i = i + 1;
        if (number % 2 == 1) continue;
        even_sum = even_sum + number;
    };
    even_sum
}
```

## `while` 和 `loop` 的型別 (The Type of `while` and `loop`)

在 Move 中，迴圈是具備型別的運算式。`while` 運算式的型別始終為 `()`。

```move
let () = while (i < 10) { i = i + 1 };
```

如果 `loop` 包含 `break`，則運算式的型別為 break 的型別。不帶值的 break 具有單元型別 `()`。

```move
(loop { if (i < 10) i = i + 1 else break }: ());
let () = loop { if (i < 10) i = i + 1 else break };

let x: u64 = loop { if (i < 10) i = i + 1 else break 5 };
let x: u64 = loop { if (i < 10) { i = i + 1; continue} else break 5 };
```

此外，如果一個迴圈包含多個 break，它們必須全部傳回相同的型別：

```move
// 無效 -- 第一個 break 傳回 ()，第二個傳回 5
let x: u64 = loop { if (i < 10) break else break 5 };
```

如果 `loop` 沒有 `break`，則 `loop` 可以具有任何型別，就像 `return`、`abort`、`break` 和 `continue` 一樣。

```move
(loop (): u64);
(loop (): address);
(loop (): &vector<vector<u8>>);
```

如果你需要更精確的控制流（例如跳出巢狀迴圈），下一章將介紹 Move 中標籤控制流（labeled control flow）的使用。
