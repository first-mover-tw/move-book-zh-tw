---
description: 巨集函式 (Macro Functions) in Move：編譯時期展開的函式，可接受 lambda 引數 —— 如何使用標準函式庫巨集，以及如何定義自己的巨集。
---

# Macro 函式 (Macro Functions) {#macro-functions}

在本章中，我們已經呼叫過不少名稱以驚嘆號結尾的函式：測試中的 `assert!` 和 `assert_eq!` 巨集，以及
[vector 巨集](./vector#vector-macros)，例如 `map!` 和 `fold!`。這些都是 _macro 函式_，既然我們已經了解
[函式](./function)和[泛型](./generics)，現在就有足夠的知識來理解它們的運作方式——以及如何定義自己的
macro 函式。

## 什麼是 Macro 函式？ (What is a Macro Function?) {#what-is-a-macro-function}

Macro 函式看起來、用起來都像一般函式，但它在執行期並不存在。相反地，編譯器會*展開*（expand）這個
macro：在每個呼叫點，macro 的主體會被就地替換，並代入引數，然後才對產生出來的程式碼進行型別檢查與編譯。
Macro 呼叫很容易辨認——macro 名稱後面一定會跟著 `!` 符號。

這種編譯期展開賦予了 macro 兩種一般函式所沒有的能力：

- 它們可以把 _lambda_——內嵌的程式碼區塊——當作引數。Move 在執行期沒有函式值，但因為 macro 是在編譯期
  展開，lambda 就只是變成產生出來的程式碼的一部分。
- 它們的主體是在展開*之後*、依每個呼叫點分別做型別檢查，這使得一些一般[泛型](./generics)無法表達的操作
  成為可能——我們馬上就會看到。

## 定義 Macro (Defining a Macro) {#defining-a-macro}

Macro 是用 `macro fun` 關鍵字定義的。參數——包括型別參數——都以 `$` 符號作為前綴，標示它們是編譯期替換
而非執行期的值：

```move file=packages/samples/sources/move-basics/macros.move anchor=max

```

`max` 這個 macro 會回傳兩個引數中較大的那一個。請注意主體中一個值得注意之處：它用 `>` 運算子比較兩個泛型
型別 `$T` 的值。一般泛型函式做不到這件事——沒有「可比較」的能力約束，所以 `fun max<T>(a: T, b: T)`
無法編譯通過。Macro 完全繞過了這個問題：等到主體進行型別檢查時，`$T` 在每個呼叫點都已經被替換成具體的
型別了：

```move file=packages/samples/sources/move-basics/macros.move anchor=max_use

```

> 另外請注意主體開頭的 `let a = $a;` 綁定。Macro 引數是以*運算式*的形式替換，而不是以計算過的值替換：
> 主體中每次出現 `$a` 都會再次求值那個引數運算式。把引數綁定到一個區域變數一次，是個好習慣，可以避免令人
> 意外的重複求值。

## Lambda 引數 (Lambda Arguments) {#lambda-arguments}

Macro 真正強大之處來自 lambda 參數。Lambda 型別寫作 `|argument_types|`（若有回傳值則寫成
`|argument_types| -> return_type`），呼叫端則使用 `|arguments| expression` 語法就地傳入 lambda：

```move file=packages/samples/sources/move-basics/macros.move anchor=repeat

```

```move file=packages/samples/sources/move-basics/macros.move anchor=repeat_use

```

Lambda 可以讀取、甚至修改外圍作用域的變數——上面的 `repeat!` 呼叫在每次迭代都更新了區域變數 `sum`。
這正是 [vector 巨集](./vector#vector-macros)背後的機制：`v.do!(|el| ...)` 就是一個帶有 lambda 參數的
macro，在編譯期會被展開成一般的迴圈。

## 惰性求值 (Lazy Evaluation) {#lazy-evaluation}

因為引數是被替換而非預先計算，一個引數運算式可能被求值一次、多次——或完全不求值。`assert!` 這個 macro
就是很好的例子：在 `assert!(condition, EMyError)` 中，錯誤碼運算式只有在條件失敗時才會被求值。這是一個
特性——在正常路徑上，失敗分支不會花費任何成本——但這也是上述重複求值注意事項的另一面：在撰寫自己的
macro 時，要想清楚每個 `$` 參數實際上會被使用幾次。

> 在呼叫點展開還有另一個可見的效果：macro 主體內觸發的 abort 會回報 macro *呼叫點*的行號，而不是
> macro 定義內部的行號。這是[巧妙錯誤](./assert-and-abort#error-messages)編碼的一部分，也是為什麼失敗
> 的 `assert!` 或 `assert_eq!` 會指向你程式碼中的那一行，而不是標準函式庫裡的某個地方——這也是撰寫斷言
> 輔助工具時，偏好使用 macro 而非一般函式的一個好理由。

## 標準函式庫中的 Macro (Macros in the Standard Library) {#macros-in-the-standard-library}

[標準函式庫](./standard-library)大量使用 macro，而它們正是操作其核心型別的慣用方式。我們已經看過
[vector 巨集](./vector#vector-macros)；`Option` 和整數型別也各自有自己的一套：

```move file=packages/samples/sources/move-basics/macros.move anchor=std_macros

```

以下快速整理一下可以在哪裡找到它們：

- [std::vector](https://docs.sui.io/references/framework/std/vector) —— `do!`、`map!`、`filter!`、
  `fold!`、`count!`、`any!`、`all!`、`tabulate!` 等等；
- [std::option](https://docs.sui.io/references/framework/std/option) —— `do!`、`map!`、
  `destroy_or!`、`extract_or!`、`is_some_and!`；
- 整數模組，例如 [std::u64](https://docs.sui.io/references/framework/std/u64) —— `do!`、
  `range_do!`、`max_value!`；
- [std::unit_test](https://docs.sui.io/references/framework/std/unit_test) —— `assert_eq!` 與
  `assert_ref_eq!`，可在測試中使用。

本節涵蓋的是 macro 的日常用法；完整的功能集——包括 macro 的方法語法、型別位置中的 `$` 運算式，以及
hygiene 規則——則記載於 Move Reference 中。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[Macro 函式](./../../reference/functions/macros)。
