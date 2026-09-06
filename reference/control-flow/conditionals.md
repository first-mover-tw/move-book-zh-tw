---
title: 條件運算式 (Conditional Expressions) | 參考手冊
description: Move 條件運算式 (conditional expressions) 參考：if、else 與 if-else 語法 (syntax)，以及型別規則 (type rules) 與運算式導向語意 (expression-based semantics)。
keywords:
  - Move
  - Sui
  - Move reference
  - conditional
  - expressions
  - reference
questions:
  - How does Conditional Expressions work in Move?
  - What is the syntax for Conditional Expressions in Move?
  - What is Grammar for Conditionals in Move?
answer: 'Move conditional expressions reference: if, else, and if-else syntax with type rules and expression-based semantics.'
goal:
  description: 'Reader understands move conditional expressions reference: if, else, and if-else syntax with type rules and expression-based semantics'
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

# 條件式 `if` 運算式 (Conditional `if` Expressions) {#conditional-if-expressions}

`if` 運算式指定只有在特定條件為真時，才應評估某些程式碼。
例如：

```move
if (x > 5) x = x - 5
```

條件必須是型別為 `bool` 的運算式。

`if` 運算式可選擇性地包含 `else` 子句，以指定條件為假時要評估的另一個運算式。

```move
if (y <= 10) y = y + 1 else y = 10
```

會評估「真」分支或「假」分支其中之一，但不會兩者皆評估。任一分支都可以是單一運算式或運算式區塊。

條件運算式可以產生值，因此 `if` 運算式會有結果。

```move
let z = if (x < 100) x else 100;
```

若未指定 `else` 子句，假分支預設為單位值。以下兩者等效：

```move
if (condition) true_branch // 隱含預設值：else ()
if (condition) true_branch else ()
```

真分支與假分支中的運算式必須具有相容的型別。例如：

```move
// x 和 y 必須是 u64 整數
let maximum: u64 = if (x > y) x else y;

// highlight-error-start
// 錯誤！分支型別不同
let z = if (maximum < 10) 10u8 else 100u64;

// 錯誤！分支型別不同，因為預設假分支是 () 而非 u64
let y = if (maximum >= 10) maximum;
// highlight-error-end
```

通常會將 `if` 運算式與
[運算式區塊](./../variables#expression-blocks) 一同使用。

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

## 條件式語法 (Grammar for Conditionals) {#grammar-for-conditionals}

> _if-expression_ → **if (** _expression_ **)** _expression_ _else-clause_<sub>_opt_</sub> >
> _else-clause_ → **else** _expression_
