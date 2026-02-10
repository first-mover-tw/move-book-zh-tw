---
title: '迴圈 | 參考手冊'
description: ''
---

# Move 中的迴圈結構 (Loop Constructs)

許多程式需要對數值進行迭代，Move 提供了 `while` 和 `loop` 形式來讓您在這些情況下編寫程式碼。此外，您還可以在執行期間使用 `break`（退出迴圈）和 `continue`（跳過本次迭代的剩餘部分，回到控制流結構的頂部）來修改這些迴圈的控制流程。

## `while` 迴圈

`while` 結構會重複執行主體（單元類型 `()` 的表達式），直到條件（`bool` 類型的表達式）評估為 `false` 為止。

以下是一個簡單 `while` 迴圈的範例，用於計算從 `1` 到 `n` 的數字總和：

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

> 使用宏 (Macros) 而非迴圈通常是實現更簡潔、更具可讀性目的的更好方法。本節僅以上述 `sum` 函式為例，來體驗宏函式的魅力：
```move
fun sum(n: u64): u64 {
    vector::tabulate!(n, |i| i + 1).fold!(0, |sum, num| sum + num)
}
```

### 在 `while` 迴圈內使用 `break`

在 Move 中，`while` 迴圈可以使用 `break` 提前退出。例如，假設我們正在尋找向量中某個數值的位置，並希望在找到它時 `break`：

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

在這裡，如果借用的向量數值等於我們的目標值，我們將 `found` 標誌設置為 `true`，然後呼叫 `break`，這將導致程式退出迴圈。

最後請注意，`while` 迴圈的 `break` 不能帶有數值：`while` 迴圈始終傳回單元類型 `()`，因此 `break` 也是如此。

### 在 `while` 迴圈內使用 `continue`

與 `break` 類似，Move 的 `while` 迴圈可以呼叫 `continue` 來跳過部分迴圈主體。這允許我們在不滿足條件時跳過部分計算，如下例所示：

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

這段程式碼將迭代提供的向量。對於每個項目，如果該項目是偶數，它將被加到 `even_sum` 中。如果不是，則它將呼叫 `continue`，跳過加法操作並返回到 `while` 迴圈的條件檢查。

## `loop` 表達式

`loop` 表達式會重複執行迴圈主體（類型為 `()` 的表達式），直到遇到 `break`：

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

如果沒有 `break`，迴圈將永遠持續下去。在下面的範例中，程式將永遠運行，因為 `loop` 沒有 `break`：

```move
fun foo() {
    let mut i = 0;
    loop { i = i + 1 }
}
```

### 在 `loop` 中使用帶有數值的 `break`

與始終傳回 `()` 的 `while` 迴圈不同，`loop` 可以使用 `break` 傳回一個數值。這樣做時，整個 `loop` 表達式的評估結果為該類型的數值。例如，我們可以使用 `loop` 和 `break` 重寫上面的 `find_position`，並在找到索引用時立即傳回：

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

這個迴圈將以選項 (option) 結果中斷，並且作為函式主體中的最後一個表達式，將產生該數值作為最終的函式結果。

### 在 `loop` 表達式內使用 `continue`

正如您所料，`continue` 也可以在 `loop` 內使用。以下是使用 `loop` 搭配 `break` 和 `continue` 而非 `while` 重寫的 `sum_even` 函式。

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

## `while` 和 `loop` 的類型

在 Move 中，迴圈是具類型的表達式。`while` 表達式始終具有類型 `()`。
```move
let () = while (i < 10) { i = i + 1 };
```

如果 `loop` 包含一個 `break`，則該表達式具有該 break 的類型。不帶數值的 break 具有單元類型 `()`。

```move
(loop { if (i < 10) i = i + 1 else break }: ());
let () = loop { if (i < 10) i = i + 1 else break };

let x: u64 = loop { if (i < 10) i = i + 1 else break 5 };
let x: u64 = loop { if (i < 10) { i = i + 1; continue} else break 5 };
```

此外，如果一個迴圈包含多個 break，它們必須傳回相同的類型：

```move
// 無效 —— 第一個 break 傳回 ()，第二個傳回 5
let x: u64 = loop { if (i < 10) break else break 5 };
```

如果 `loop` 沒有 `break`，則 `loop` 可以具有任何類型，就像 `return`、`abort`、`break` 和 `continue` 一樣。

```move
(loop (): u64);
(loop (): address);
(loop (): &vector<vector<u8>>);
```

如果您需要更精確的控制流程，例如從巢狀迴圈中跳出，下一章將介紹 Move 中具標籤的控制流程的用法。
