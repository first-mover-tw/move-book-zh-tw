---
title: 迴圈 (Loops) | 參考手冊
description:
  迴圈語法參考 (Loop Constructs Reference)：涵蓋 while 迴圈、loop 表達式、for 迴圈、break、continue
  以及走訪模式。
---

# Move 中的循環結構

許多程式需要對數值進行迭代，Move 提供了 `while` 和 `loop` 形式來允許你在這些情況下編寫程式碼。此外，你還可以在執行期間使用 `break`（退出循環）和 `continue`（跳過本次迭代的剩餘部分並返回控制流結構的頂部）來修改這些循環的控制流。

## `while` 循環

`while` 結構會重複主體（類型為 `()` 的表達式），直到條件（類型為 `bool` 的表達式）求值為 `false`。

這是一個簡單的 `while` 循環範例，用於計算從 `1` 到 `n` 的數字總和：

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

也允許無限 `while` 循環：

```move
fun foo() {
    while (true) { }
}
```

> 使用巨集 (Macros) 而非循環 (Loops) 來實現更簡潔、更具可讀性的目的是一種更好的方式。
> 本文僅以上述函式 `sum` 為例來體驗巨集函式的魅力：

```move
fun sum(n: u64): u64 {
    vector::tabulate!(n, |i| i + 1).fold!(0, |sum, num| sum + num)
}
```

### 在 `while` 循環中使用 `break`

在 Move 中，`while` 循環可以使用 `break` 提前退出。例如，假設我們正在尋找向量中某個值的直位置，並希望在找到它時 `break`：

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

這裡，如果借用的向量值等於我們的目標值，我們將 `found` 標記設置為 `true`，然後呼叫 `break`，這將導致程式退出循環。

最後請注意，`while` 循環的 `break` 不能帶有數值：`while` 循環始終回傳單元類型 `()`，因此 `break` 也是如此。

### 在 `while` 循環中使用 `continue`

與 `break` 類似，Move 的 `while` 循環可以呼叫 `continue` 來跳過部分循環主體。這允許我們在未滿足條件時跳過部分計算，如下例所示：

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

這段程式碼將遍歷提供的向量。對於每個項目，如果該項目是偶數，它將將其添加到 `even_sum` 中。然而，如果不是偶數，它將呼叫 `continue`，跳過加總操作並返回 `while` 循環的條件檢查。

## `loop` 表達式

`loop` 表達式會重複循環主體（類型為 `()` 的表達式），直到遇到 `break`：

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

如果沒有 `break`，循環將永遠進行下去。在下面的範例中，程式將永遠運行，因為 `loop` 沒有 `break`：

```move
fun foo() {
    let mut i = 0;
    loop { i = i + 1 }
}
```

### 在 `loop` 中使用 `break` 帶回傳值

與始終回傳 `()` 的 `while` 循環不同，`loop` 可以使用 `break` 回傳一個數值。這樣做，整個 `loop` 表達式的求值結果就是該類型的數值。例如，我們可以使用 `loop` 和 `break` 重寫上面的 `find_position`，如果找到則立即回傳索引：

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

這個循環將以選項 (option) 結果中斷，並且作為函式主體中的最後一個表達式，將產生該數值作為最終的函式結果。

### 在 `loop` 表達式中使用 `continue`

如你所料，`continue` 也可以在 `loop` 內使用。以下是使用 `loop` 配合 `break` 和 `continue` 而非 `while` 重寫的前一個 `sum_even` 函式。

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

在 Move 中，循環是具備類型的表達式。`while` 表達式的類型始終為 `()`。

```move
let () = while (i < 10) { i = i + 1 };
```

如果一個 `loop` 包含一個 `break`，該表達式的類型就是該中斷的回傳類型。沒有數值的中斷俱有單元類型 `()`。

```move
(loop { if (i < 10) i = i + 1 else break }: ());
let () = loop { if (i < 10) i = i + 1 else break };

let x: u64 = loop { if (i < 10) i = i + 1 else break 5 };
let x: u64 = loop { if (i < 10) { i = i + 1; continue} else break 5 };
```

此外，如果一個循環包含多個中斷，它們必須全部回傳相同的類型：

```move
// 無效 —— 第一個中斷回傳 ()，第二個回傳 5
let x: u64 = loop { if (i < 10) break else break 5 };
```

如果 `loop` 沒有 `break`，則 `loop` 可以具有任何類型，就像 `return`、`abort`、`break` 和 `continue` 一樣。

```move
(loop (): u64);
(loop (): address);
(loop (): &vector<vector<u8>>);
```

如果你需要甚至更精確的控制流，例如從巢狀循環中跳出，下一章將介紹 Move 中帶標籤的控制流用法。
