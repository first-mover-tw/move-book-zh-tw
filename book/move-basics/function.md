---
description: 'Functions in Move: declare, call, and return values from functions with support for multiple return values and type parameters.'
---

# 函式 (Functions)

函式是 Move 程式的構建塊。它們從 [使用者交易](./../concepts/what-is-a-transaction) 或其他函式中被呼叫，並將可執行的程式碼分組為可重用的單元。函式可以接收參數並傳回一個值。它們在模組層級中使用 `fun` 關鍵字宣告。與任何其他模組成員一樣，預設情況下它們是私有的，只能從模組內部存取。

```move file=packages/samples/sources/move-basics/function.move anchor=math

```

在此範例中，我們定義了一個 `add` 函式，它接收兩個 `u64` 類型的參數並傳回它們的和。同樣位於同一個模組中的 `test_add` 函式是一個呼叫 `add` 的測試函式。該測試使用 `assert!` 巨集將 `add` 的結果與預期值進行比較。如果 `assert!` 內部的條件評估為 false，執行將自動中斷。

## 函式宣告

> 在 Move 中，函式通常使用 **蛇形命名法 (snake_case)**。這意味著函式名稱應全部小寫，單字之間以底線分隔。例如 `do_something`、`add`、`get_balance`、`is_authorized` 等等。

函式使用 `fun` 關鍵字宣告，後接函式名稱（有效的 Move 識別碼）、括號中的參數清單以及傳回類型。函式主體是一個包含一系列語句和表達式的程式碼區塊。函式主體中的最後一個表達式即為函式的傳回值。

```move file=packages/samples/sources/move-basics/function.move anchor=return_nothing

```

## 存取函式

與其他模組成員一樣，函式可以匯入並透過路徑存取。路徑由模組路徑和函式名稱組成，以 `::` 分隔。例如，如果您在 `book` 套件的 `math` 模組中有一個名為 `add` 的函式，其完整路徑將是 `book::math::add`。如果模組已經匯入，您可以像下面的範例一樣直接將其存取為 `math::add`：

```move file=packages/samples/sources/move-basics/function_use.move anchor=use_math

```

## 多個傳回值

Move 函式可以傳回多個值，這在您需要從一個函式傳回多個資料片段時特別有用。傳回類型指定為類型的元組 (tuple)，傳回值也作為表達式的元組提供：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return

```

具有元組傳回值的函式呼叫結果，必須透過 `let (tuple)` 語法解構成變數：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_imm

```

如果宣告的任何值需要宣告為可變的，則在變數名稱前加上 `mut` 關鍵字：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_mut

```

如果某些參數不被使用，可以使用 `_` 符號忽略它們：

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_ignore

```

## 延伸閱讀

- Move 參考手冊中的 [函式 (Functions)](./../../reference/functions)。
