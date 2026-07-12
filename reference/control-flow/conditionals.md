---
title: 條件運算式 (Conditional Expressions) | 參考手冊
description: Move 條件式運算式參考 (Move Conditional Expressions Reference)：if、else 與 if-else
  語法，含型別規則與以運算式為基礎的語意。
---

# 條件 `if` 運算式

`if` 運算式指定僅當特定條件為真 (true) 時，才應求值某些程式碼。例如：

```move
if (x > 5) x = x - 5
```

該條件必須是一個型別為 `bool` 的運算式。

`if` 運算式可以選擇性地包含一個 `else` 子句，以指定當條件為假 (false) 時要求值的另一個運算式。

```move
if (y <= 10) y = y + 1 else y = 10
```

「真」分支或「假」分支其中之一將被求值，但不會同時被求值。任何一個分支都可以是單個運算式或運算式區塊。

條件運算式可能會產生數值，使 `if` 運算式具備一個結果。

```move
let z = if (x < 100) x else 100;
```

如果未指定 `else` 子句，假分支預設為單元型別 (unit value) `()`。以下兩者是等價的：

```move
if (condition) true_branch // 暗示預設為：else ()
if (condition) true_branch else ()
```

真分支和假分支中的運算式必須具有相容的型別。例如：

```move
// x 和 y 必須是 u64 整數
let maximum: u64 = if (x > y) x else y;

// highlight-error-start
// 錯誤！分支型別不同
let z = if (maximum < 10) 10u8 else 100u64;

// 錯誤！分支型別不同，因為預設的假分支是 () 而非 u64
let y = if (maximum >= 10) maximum;
// highlight-error-end
```

通常，`if` 運算式會與 [運算式區塊 (expression blocks)](./../variables#expression-blocks) 結合使用。

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

## 條件陳述式語法 (Grammar)

> _if-運算式_ → **if (** _運算式_ **)** _運算式_ _else-子句_<sub>_可選_</sub>
> _else-子句_ → **else** _運算式_
