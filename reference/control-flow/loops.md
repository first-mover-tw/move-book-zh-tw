---
title: 迴圈 (Loops) | 參考手冊
description: Move 迴圈建構參考手冊：while 迴圈、loop 運算式、for 迴圈、break、continue，以及迭代模式。
keywords:
  - Move
  - Sui
  - Move reference
  - loops
  - reference
questions:
  - How does Loops work in Move?
  - What is the syntax for Loops in Move?
  - What is while Loops in Move?
  - What is loop Expressions in Move?
answer: 'Move loop constructs reference: while loops, loop expressions, for loops, break, continue, and iteration patterns.'
goal:
  description: 'Reader understands move loop constructs reference: while loops, loop expressions, for loops, break, continue, and iteration patterns'
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

# Move 中的迴圈結構 (Loop Constructs in Move) {#loop-constructs-in-move}

許多程式需要對值進行迭代，而 Move 提供 `while` 與 `loop` 形式，讓你能在這些情境中撰寫程式碼。此外，你也可以在執行期間使用 `break`（離開迴圈）與 `continue`（略過本次迭代的其餘部分，並回到控制流程結構頂端）來修改這些迴圈的控制流程。

## `while` 迴圈 (`while` Loops) {#while-loops}

`while` 結構會重複執行主體（型別為 unit 的運算式），直到條件（型別為 `bool` 的運算式）求值為 `false`。

以下是一個簡單的 `while` 迴圈範例，用於計算從 `1` 到 `n` 的數字總和：

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

> 使用巨集而非迴圈，是達成更簡潔且易讀目的的更佳方式。
> 本文僅以上述函式 `sum` 為例，體驗巨集函式的魅力：

```move
fun sum(n: u64): u64 {
    vector::tabulate!(n, |i| i + 1).fold!(0, |sum, num| sum + num)
}
```

### 在 `while` 迴圈內使用 `break` (Using `break` Inside of `while` Loops) {#using-break-inside-of-while-loops}

在 Move 中，`while` 迴圈可以使用 `break` 提早離開。例如，假設我們正在尋找某個值在向量中的位置，並希望在找到它時 `break`：

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

在此，如果借用的向量值等於目標值，我們便將 `found` 旗標設為 `true`，接著呼叫 `break`，使程式離開迴圈。

最後請注意，`while` 迴圈的 `break` 無法接受值：`while` 迴圈一律回傳 unit 型別 `()`，因此 `break` 也是如此。

### 在 `while` 迴圈內使用 `continue` (Using `continue` Inside of `while` Loops) {#using-continue-inside-of-while-loops}

與 `break` 類似，Move 的 `while` 迴圈可以呼叫 `continue` 來略過部分迴圈主體。這讓我們能在條件不符合時略過部分計算，如以下範例所示：

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

此程式碼會迭代所提供的向量。對於每個項目，若該項目是偶數，便會將其加入 `even_sum`。但若不是，則會呼叫 `continue`，略過加總運算並回到 `while` 迴圈的條件檢查。

## `loop` 運算式 (`loop` Expressions) {#loop-expressions}

`loop` 運算式會重複執行迴圈主體（型別為 `()` 的運算式），直到遇到 `break`：

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

若沒有 `break`，迴圈將會永遠持續。在以下範例中，程式會永遠執行，因為 `loop` 沒有 `break`：

```move
fun foo() {
    let mut i = 0;
    loop { i = i + 1 }
}
```

### 在 `loop` 中搭配值使用 `break` (Using `break` with Values in `loop`) {#using-break-with-values-in-loop}

不同於一律回傳 `()` 的 `while` 迴圈，`loop` 可以透過 `break` 回傳一個值。如此一來，整體 `loop` 運算式便會求值為該型別的值。例如，我們可以使用 `loop` 與 `break` 重寫上述的 `find_position`，若找到該值便立即回傳其索引：

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

此迴圈會以 option 結果中斷，而作為函式主體中的最後一個運算式，它會產生該值作為最終函式結果。

### 在 `loop` 運算式內使用 `continue` (Using `continue` Inside of `loop` Expressions) {#using-continue-inside-of-loop-expressions}

如你所預期，`continue` 也能在 `loop` 內使用。以下是先前的 `sum_even` 函式，改為使用帶有 `break `and` continue` 的 `loop`，而非 `while`。

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

## `while` 與 `loop` 的型別 (The Type of `while` and `loop`) {#the-type-of-while-and-loop}

在 Move 中，迴圈是具有型別的運算式。`while` 運算式一律具有型別 `()`。

```move
let () = while (i < 10) { i = i + 1 };
```

若 `loop` 包含 `break`，該運算式便具有 break 的型別。不帶值的 break 具有 unit 型別 `()`。

```move
(loop { if (i < 10) i = i + 1 else break }: ());
let () = loop { if (i < 10) i = i + 1 else break };

let x: u64 = loop { if (i < 10) i = i + 1 else break 5 };
let x: u64 = loop { if (i < 10) { i = i + 1; continue} else break 5 };
```

此外，若迴圈包含多個 break，它們都必須回傳相同型別：

```move
// 無效 -- 第一個 break 回傳 ()，第二個回傳 5
let x: u64 = loop { if (i < 10) break else break 5 };
```

若 `loop` 沒有 `break`，則 `loop` 可以具有任何型別，如同 `return`、`abort`、`break` 與 `continue`。

```move
(loop (): u64);
(loop (): address);
(loop (): &vector<vector<u8>>);
```

若你需要更精確的控制流程，例如跳出巢狀迴圈，下一章將介紹 Move 中具標籤控制流程的使用方式。
