---
description: Move 中的函式 (Functions)：宣告、呼叫函式並回傳值，支援多個回傳值與型別參數 (type parameters)。
title: 函式 (Functions)
keywords:
  - Move
  - Sui
  - Move tutorial
  - functions
questions:
  - What is Functions in Move?
  - How do I use Functions in Move?
  - What is Function Declaration in Move?
  - What is Accessing Functions in Move?
answer: 'Functions in Move: declare, call, and return values from functions with support for multiple return values and type parameters.'
goal:
  description: 'Reader understands functions in Move: declare, call, and return values from functions with support for multiple return values and type parameters'
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

# 函式 (Functions) {#functions}

函式是 Move 程式的建構區塊。它們可由[使用者交易](./../concepts/what-is-a-transaction)及其他函式呼叫，並將可執行程式碼組織為可重複使用的單位。函式可接受引數並回傳值。它們會在模組層級以 `fun` 關鍵字宣告。如同其他所有模組成員，預設為私有，只能從模組內存取；若要讓其他模組可見，將在本章稍後的[可見性修飾詞](./visibility)章節中說明。

```move file=packages/samples/sources/move-basics/function.move anchor=math

```

在此範例中，我們定義了一個 `add` 函式，它接受兩個 `u64` 型別的引數並回傳其總和。位於同一模組中的 `test_add` 函式是會呼叫 `add` 的測試函式。測試使用 `assert_eq!` 巨集比較 `add` 的結果與預期值。若兩個值不同，執行會自動中止。

## 函式宣告 (Function Declaration) {#function-declaration}

> 在 Move 中，函式通常使用 `snake_case` 命名慣例。這表示函式名稱應全部使用小寫字母，並以底線分隔單字。範例包括 `do_something`、`add`、`get_balance`、`is_authorized` 等。

函式會以 `fun` 關鍵字宣告，後接函式名稱（有效的 Move 識別字）、括號中的引數清單，以及回傳型別。函式主體是一個[區塊](./expression#blocks)，且如同任何區塊，沒有分號的最後一個運算式即為函式的回傳值。`return` 關鍵字可讓函式提早回傳；其餘[控制流程](./control-flow)運算式章節會涵蓋此內容。

```move file=packages/samples/sources/move-basics/function.move anchor=return_nothing

```

## 存取函式 (Accessing Functions) {#accessing-functions}

如同其他模組成員，函式可透過路徑匯入及存取。該路徑由模組路徑與函式名稱組成，並以 :: 分隔。例如，若 `book` 套件中 `math` 模組內有名為 `add` 的函式，其完整路徑會是 `book::math::add`。若模組已匯入——匯入方式會在[匯入模組](./importing-modules)章節中說明——你可直接以 `math::add` 存取它，如下列範例所示：

```move file=packages/samples/sources/move-basics/function_use.move anchor=use_math

```

## 多個回傳值 (Multiple Return Values) {#multiple-return-values}

Move 函式可回傳多個值，當你需要從函式回傳多筆資料時尤其實用。回傳型別會指定為型別元組，回傳值則會提供為運算式元組：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return

```

具有元組回傳值的函式呼叫結果，必須透過 `let (tuple)` 語法解構至變數中：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_imm

```

若任何已宣告的值需要宣告為可變動，請將 `mut` 關鍵字放在變數名稱之前：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_mut

```

若部分回傳值不需要，可使用 `_` 符號忽略：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_ignore

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[函式](./../../reference/functions)。
