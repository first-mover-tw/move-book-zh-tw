---
description: Move 中的運算式 (Expressions)：常值、函式呼叫、區塊，以及 Move 語言中幾乎所有項目如何回傳值。
title: 運算式 (Expression)
keywords:
  - Move
  - Sui
  - Move tutorial
  - expression
questions:
  - What is Expression in Move?
  - How do I use Expression in Move?
  - What is Literals in Move?
  - What is Operators in Move?
answer: 'Expressions in Move: literals, function calls, blocks, and how almost everything returns a value in the Move language.'
goal:
  description: 'Reader understands expressions in Move: literals, function calls, blocks, and how almost everything returns a value in the Move language'
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

# 運算式 (Expression) {#expression}

在程式語言中，運算式是會回傳值的程式碼單位。在 Move 中，除了作為宣告的 `let` 陳述式以外，幾乎所有內容都是運算式。本節將介紹各類運算式，並引入作用域的概念。

> 運算式以分號 `;` 串接。若分號後方「沒有運算式」，編譯器會插入一個 _unit_ `()`——代表空運算式的值。

## 字面值 (Literals) {#literals}

在 [基本型別](./primitive-types) 章節中，我們介紹了 Move 的基本型別，並使用字面值加以說明。字面值是用來在原始碼中表示固定值的表示法。字面值可用於初始化變數，或直接將固定值作為引數傳遞給函式。Move 支援下列字面值：

- 布林值：`true` 與 `false`
- 整數值：`0`、`1`、`123123`
- 十六進位值：以 0x 為前綴、用於表示整數的數字，例如 `0x0`、`0x1`、`0x123`
- 位元組向量值：以 `b` 為前綴，例如 `b"bytes_vector"`
- 位元組值：以 `x` 為前綴的十六進位字面值，例如 `x"0A"`
- 字串值：以雙引號包覆的文字，例如 `"hello"`。與其他字面值不同，字串字面值的型別會由情境推斷——它可以是 `vector<u8>`，或兩種標準字串型別之一。字串會在 [字串](./string) 章節中詳細說明。

```move file=packages/samples/sources/move-basics/expression.move anchor=literals

```

## 運算子 (Operators) {#operators}

算術、邏輯與位元運算子用於對值執行運算。由於這些運算會產生值，因此被視為運算式。整數運算子及其會在何時中止，列於 [基本型別](./primitive-types#operations) 章節中。

```move file=packages/samples/sources/move-basics/expression.move anchor=operators

```

## 區塊 (Blocks) {#blocks}

區塊是由大括號 `{}` 包圍的一連串陳述式與運算式。它會回傳區塊中最後一個運算式的值（請注意，這個最後的運算式不可有結尾分號）。區塊本身就是運算式，因此可用於任何預期使用運算式的位置。

```move file=packages/samples/sources/move-basics/expression.move anchor=block

```

區塊也會界定 _作用域_：在區塊內宣告的變數只會存在到區塊的右大括號為止。當值的作用域結束時究竟會發生什麼，是 Move 中的重要問題；[所有權與作用域](./ownership-and-scope) 章節專門說明此議題。

## 函式呼叫 (Function Calls) {#function-calls}

下一節的 [函式](./function) 會詳細介紹函式。此處只需知道函式呼叫是一種運算式：它會呼叫函式，並回傳函式本體中最後一個運算式的值，前提是最後一個運算式沒有結尾分號。

```move file=packages/samples/sources/move-basics/expression.move anchor=fun_call

```

## 控制流程運算式 (Control Flow Expressions) {#control-flow-expressions}

控制流程運算式用於控制程式的流程。它們也是運算式，因此會回傳值。我們會在 [控制流程](./control-flow) 章節中介紹控制流程運算式。以下是非常簡要的概覽：

```move file=packages/samples/sources/move-basics/expression.move anchor=control_flow

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [相等性](./../../reference/equality)。
- Move 參考文件中的 [控制流程](./../../reference/control-flow)。
