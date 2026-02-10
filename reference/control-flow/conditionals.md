---
title: '條件表達式 (Conditional Expressions) | 參考手冊'
description: "Move 條件表達式參考手冊：if、else 和 if-else 語法，包含類型規則和基於表達式的語義。"
---

# 條件 `if` 表達式

`if` 表達式指定僅當特定條件為真 (true) 時，才應求值某些程式碼。例如：

```move
if (x > 5) x = x - 5
```

該條件必須是一個類型為 `bool` 的表達式。

`if` 表達式可以選擇性地包含一個 `else` 子句，以指定當條件為假 (false) 時要求值的另一個表達式。

```move
if (y <= 10) y = y + 1 else y = 10
```

「真」分支或「假」分支其中之一將被求值，但不會同時被求值。任何一個分支都可以是單個表達式或表達式區塊。

條件表達式可能會產生數值，使 `if` 表達式具備一個結果。

```move
let z = if (x < 100) x else 100;
```

如果未指定 `else` 子句，假分支預設為單元類型 (unit value) `()`。以下兩者是等價的：

```move
if (condition) true_branch // 暗示預設為：else ()
if (condition) true_branch else ()
```

真分支和假分支中的表達式必須具有相容的類型。例如：

```move
// x 和 y 必須是 u64 整數
let maximum: u64 = if (x > y) x else y;

// highlight-error-start
// 錯誤！分支類型不同
let z = if (maximum < 10) 10u8 else 100u64;

// 錯誤！分支類型不同，因為預設的假分支是 () 而非 u64
let y = if (maximum >= 10) maximum;
// highlight-error-end
```

通常，`if` 表達式會與 [表達式區塊 (expression blocks)](./../variables#表達式區塊) 結合使用。

```move
let maximum = if (x > y) x else y;
if (maximum < 10) {
    x = x + 10;
    y = y + 10;
} else if (x >= 10 && y >= 10) {
    x = x - 10;
    y = y - 10;
}
```

## 條件語句語法 (Grammar)

> _if-表達式_ → **if (** _表達式_ **)** _表達式_ _else-子句_<sub>_可選_</sub>
> _else-子句_ → **else** _表達式_
