---
description: '函式 (Functions) in Move: declare, call, and return values from functions
  with support for multiple return values and type parameters.'
---

# 函式 (Functions) {#functions}

函式是 Move 程式的建構模組。它們從
[使用者交易](./../concepts/what-is-a-transaction)以及其他函式中被呼叫,並將可執行程式碼分組成可重複使用的單元。函式可以接收引數並回傳一個值。它們是以
`fun` 關鍵字在模組層級宣告的。就像其他任何模組成員一樣,預設情況下
它們是私有的,只能從模組內部存取;讓它們對其他
模組可見是[可見性修飾詞 (Visibility Modifiers)](./visibility)章節的主題,將在本章稍後介紹。

```move file=packages/samples/sources/move-basics/function.move anchor=math

```

在這個範例中,我們定義了一個函式 `add`,它接收兩個 `u64` 型別的引數並回傳它們的
總和。位於同一模組中的 `test_add` 函式是一個測試函式,它呼叫 `add`。這個
測試使用 `assert_eq!` 巨集來比較 `add` 的結果與預期值。如果
兩個值不同,執行會自動中止。

## 函式宣告 (Function Declaration) {#function-declaration}

> 在 Move 中,函式通常使用 `snake_case` 慣例命名。這代表函式
> 名稱應全部小寫,單字之間以底線分隔。範例包括
> `do_something`、`add`、`get_balance`、`is_authorized` 等等。

函式是以 `fun` 關鍵字宣告,後面接著函式名稱(一個有效的 Move
識別字)、括號中的引數清單,以及一個回傳型別。函式主體是一個
[區塊 (block)](./expression#blocks),而且就像任何區塊一樣,最後一個沒有分號的運算式就是
函式的回傳值。`return` 關鍵字允許提前回傳——這會在其他
[控制流程 (control flow)](./control-flow)運算式中一併說明。

```move file=packages/samples/sources/move-basics/function.move anchor=return_nothing

```

## 存取函式 (Accessing Functions) {#accessing-functions}

就像其他模組成員一樣,函式可以使用路徑匯入並存取。路徑
由模組路徑和函式名稱組成,以 :: 分隔。例如,如果你在
`book` 套件中的 `math` 模組裡有一個名為 `add` 的函式,它的完整路徑會是
`book::math::add`。如果模組已經被匯入——匯入在
[匯入模組 (Importing Modules)](./importing-modules)章節中有說明——你可以直接以 `math::add` 存取它,如同
以下範例:

```move file=packages/samples/sources/move-basics/function_use.move anchor=use_math

```

## 多重回傳值 (Multiple Return Values) {#multiple-return-values}

Move 函式可以回傳多個值,當你需要從一個函式回傳
不只一項資料時,這特別有用。回傳型別以型別的元組(tuple)指定,而
回傳值則以運算式的元組提供:

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return

```

具有元組回傳的函式呼叫結果,必須透過
`let (tuple)` 語法解構到變數中:

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_imm

```

如果任何已宣告的值需要宣告為可變的,`mut` 關鍵字要放在
變數名稱之前:

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_mut

```

如果有些回傳值不需要使用,可以用 `_` 符號忽略它們:

```move file=packages/samples/sources/move-basics/function.move anchor=tuple_return_ignore

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[函式 (Functions)](./../../reference/functions)。
