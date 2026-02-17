---

description: "Expressions in Move: literals, function calls, blocks, and how almost everything returns a value in the Move language."
---

# 表達式 (Expression)

在程式語言中，表達式是傳回一個值的程式碼單位。在 Move 中，幾乎所有內容都是表達式，唯一的例外是 `let` 語句，它是一個宣告。在本節中，我們將介紹表達式的類型並引入作用域 (scope) 的概念。

> 表達式以分號 `;` 序列化。如果分號後「沒有表達式」，編譯器將插入一個 `unit ()`，它代表一個空的表達式。

## 常數值 (Literals)

在 [原始類型](./primitive-types) 章節中，我們介紹了 Move 的基本類型。為了說明這些類型，我們使用了常數值 (literal)。常數值是程式原始碼中表示固定值的記法。常數值可用於初始化變數，或直接作為參數傳遞給函式。Move 具有以下常數值：

- 布林值：`true` 和 `false`
- 整數值：`0`, `1`, `123123`
- 十六進位值：以 0x 開頭的數字表示整數，例如 `0x0`, `0x1`, `0x123`
- 位元組向量值：以 `b` 開頭，例如 `b"bytes_vector"`
- 位元組值：以 `x` 開頭的十六進位常數值，例如 `x"0A"`

```move file=packages/samples/sources/move-basics/expression.move anchor=literals

```

## 運算子 (Operators)

算術、邏輯和位元運算子用於對值執行運算。由於這些運算會產生值，因此它們被視為表達式。

```move file=packages/samples/sources/move-basics/expression.move anchor=operators

```

## 區塊 (Blocks)

區塊是封裝在大括號 `{}` 中的一系列語句 and 表達式。它傳回區塊中最後一個表達式的值（注意，這個最後的表達式不能以分號結尾）。區塊本身就是一個表達式，因此可以用在任何預期出現表達式的地方。

```move file=packages/samples/sources/move-basics/expression.move anchor=block

```

## 函式呼叫 (Function Calls)

我們在 [函式](./function) 章節中詳細介紹了函式。然而，我們在之前的章節中已經使用過函式呼叫，因此在這裡值得提一下。函式呼叫是一個呼叫函式並傳回函式主體中最後一個表達式值的表達式，前提是最後一個表達式沒有終止分號。

```move file=packages/samples/sources/move-basics/expression.move anchor=fun_call

```

## 流程控制表達式 (Control Flow Expressions)

流程控制表達式用於控制程式的流程。它們也是表達式，因此會傳回一個值。我們在 [流程控制](./control-flow) 章節中介紹了流程控制表達式。以下是一個非常簡要的概述：

```move file=packages/samples/sources/move-basics/expression.move anchor=control_flow

```
