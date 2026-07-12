---
description: 運算式 (Expressions) 中的字面值、函式呼叫、程式碼區塊，以及在 Move 語言中幾乎所有東西都會回傳一個值。
---

# 運算式 (Expression) {#expression}

在程式語言中，運算式是回傳一個值的程式碼單元。在 Move 中，幾乎所有東西都是運算式，唯一的例外是 `let` 陳述式，它是一個宣告。在本節中，我們將介紹運算式的種類，並引入作用域（scope）的概念。

> 運算式以分號 `;` 分隔。如果分號後面「沒有運算式」，編譯器會插入一個 _unit_ `()` —— 代表空運算式的值。

## 字面值 (Literals) {#literals}

在[基本型別](./primitive-types)一節中，我們介紹了 Move 的基本型別。而為了說明它們，我們使用了字面值。字面值是一種在原始碼中表示固定值的表示法。字面值可以用來初始化變數，或直接將固定值作為引數傳遞給函式。Move 有以下幾種字面值：

- 布林值：`true` 和 `false`
- 整數值：`0`、`1`、`123123`
- 十六進位值：以 0x 為前綴的數字，用來表示整數，例如 `0x0`、`0x1`、`0x123`
- 位元組向量值：以 `b` 為前綴，例如 `b"bytes_vector"`
- 位元組值：以 `x` 為前綴的十六進位字面值，例如 `x"0A"`
- 字串值：以雙引號括住的文字，例如 `"hello"`。與其他字面值不同的是，字串字面值的型別是由上下文推斷出來的 —— 它可以是 `vector<u8>` 或兩種標準字串型別之一。字串會在[字串](./string)一節中詳細介紹。

```move file=packages/samples/sources/move-basics/expression.move anchor=literals

```

## 運算子 (Operators) {#operators}

算術、邏輯與位元運算子用來對值執行運算。由於這些運算會產生值，因此它們被視為運算式。整數運算子——以及它們會在何時中止（abort）——列在[基本型別](./primitive-types#operations)一節中。

```move file=packages/samples/sources/move-basics/expression.move anchor=operators

```

## 區塊 (Blocks) {#blocks}

區塊是由大括號 `{}` 包住的一系列陳述式與運算式。它會回傳區塊中最後一個運算式的值（注意，這個最終的運算式不能有結尾分號）。區塊是一種運算式，因此它可以用在任何需要運算式的地方。

```move file=packages/samples/sources/move-basics/expression.move anchor=block

```

區塊同時也劃定了_作用域_（scope）：在區塊內宣告的變數，只存在到該區塊的結尾大括號為止。當作用域結束時，值究竟會發生什麼事，是 Move 中一個重要的問題，[所有權與作用域](./ownership-and-scope)一節就是專門討論這個主題。

## 函式呼叫 (Function Calls) {#function-calls}

我們會在緊接著的下一節——[函式](./function)——中詳細介紹函式。這裡只需要說明的是，函式呼叫是一種運算式：它會呼叫一個函式，並回傳該函式主體中最後一個運算式的值，前提是該最後一個運算式沒有結尾分號。

```move file=packages/samples/sources/move-basics/expression.move anchor=fun_call

```

## 控制流程運算式 (Control Flow Expressions) {#control-flow-expressions}

控制流程運算式用來控制程式的執行流程。它們同樣也是運算式，因此會回傳一個值。我們會在[控制流程](./control-flow)一節中介紹控制流程運算式。以下是一個非常簡短的概覽：

```move file=packages/samples/sources/move-basics/expression.move anchor=control_flow

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[相等性](./../../reference/equality)。
- Move Reference 中的[控制流程](./../../reference/control-flow)。
