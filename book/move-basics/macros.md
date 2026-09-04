---
description: Move 中的巨集函式 (macro functions)：在編譯時期展開的函式 (compile-time expanded functions)，具有 Lambda 引數 (lambda arguments) — 如何使用標準函式庫巨集 (standard library macros) 並自行定義。
title: 巨集函式 (Macro Functions)
keywords:
  - Move
  - Sui
  - Move tutorial
  - macro
  - functions
questions:
  - What is Macro Functions in Move?
  - How do I use Macro Functions in Move?
  - What is a Macro Function?
  - What is Defining a Macro in Move?
answer: 'Macro functions in Move: compile-time expanded functions with lambda arguments - how to use standard library macros and define your own.'
goal:
  description: 'Reader understands macro functions in Move: compile-time expanded functions with lambda arguments - how to use standard library macros and define your own'
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

# 巨集函式 (Macro Functions) {#macro-functions}

在本章中，我們呼叫了不少名稱以驚嘆號結尾的函式：測試中的 `assert!` 與 `assert_eq!` 巨集，以及 [vector 巨集](./vector#vector-macros)，例如 `map!` 與 `fold!`。它們全都是 _巨集函式_；現在我們已了解 [函式](./function) 與 [泛型](./generics)，已具備理解其運作方式，以及定義自己巨集函式所需的一切知識。

## 什麼是巨集函式？ (What is a Macro Function?) {#what-is-a-macro-function}

巨集函式看起來與使用起來都像一般函式，但它不會存在於執行期。編譯器會改為 _展開_ 巨集：在每個呼叫位置，巨集主體會以內嵌方式替換，並將引數代入；之後才會對產生的程式碼進行型別檢查與編譯。巨集呼叫很容易辨識：巨集名稱後方一定會接著 `!` 符號。

這種編譯期展開讓巨集具備一般函式沒有的兩項能力：

- 它們可以接受 _lambda_——內嵌程式碼區塊——作為引數。Move 在執行期沒有函式值，但由於巨集會在編譯期間展開，lambda 會直接成為產生程式碼的一部分。
- 它們的主體會在展開 _之後_，依每個呼叫位置進行型別檢查，因此可進行一般 [泛型](./generics) 無法表達的操作——我們即將看到這一點。

## 定義巨集 (Defining a Macro) {#defining-a-macro}

巨集使用 `macro fun` 關鍵字定義。參數——包含型別參數——會加上 `$` 前綴，以標示它們是編譯期替換項目，而非執行期值：

```move file=packages/samples/sources/move-basics/macros.move anchor=max

```

`max` 巨集會回傳兩個引數中較大的值。請注意主體中值得注意的一點：它使用 `>` 運算子比較泛型型別 `$T` 的兩個值。一般泛型函式無法做到這點——不存在「可比較」的能力限制，因此 `fun max<T>(a: T, b: T)` 無法編譯。巨集完全避開了這個問題：在對主體進行型別檢查時，`$T` 已在每個呼叫位置替換為具體型別：

```move file=packages/samples/sources/move-basics/macros.move anchor=max_use

```

> 也請注意主體頂端的 `let a = $a;` 繫結。巨集引數會作為 _運算式_ 替換，而非計算完成的值：主體中每次出現 `$a` 都會再次評估引數運算式。將引數繫結至區域變數一次是良好習慣，可避免令人意外的重複評估。

## Lambda 引數 (Lambda Arguments) {#lambda-arguments}

巨集真正的威力來自 lambda 參數。lambda 型別寫作 `|argument_types|`（若會回傳值，則寫作 `|argument_types| -> return_type`），而呼叫端會使用 `|arguments| expression` 語法內嵌傳入 lambda：

```move file=packages/samples/sources/move-basics/macros.move anchor=repeat

```

```move file=packages/samples/sources/move-basics/macros.move anchor=repeat_use

```

lambda 可以讀取，甚至修改外層範圍的變數——上述 `repeat!` 呼叫會在每次迭代時更新區域變數 `sum`。這正是 [vector 巨集](./vector#vector-macros) 背後的機制：`v.do!(|el| ...)` 是帶有 lambda 參數的巨集，在編譯期間展開為一般迴圈。

## 延遲評估 (Lazy Evaluation) {#lazy-evaluation}

由於引數是替換而非預先計算，引數運算式可能評估一次、多次，或完全不評估。`assert!` 巨集是很好的例子：在 `assert!(condition, EMyError)` 中，只有條件失敗時才會評估錯誤碼運算式。這是特色——成功路徑不會付出失敗分支的成本——但也是上述重複評估注意事項的另一面：撰寫自己的巨集時，請思考每個 `$` 參數實際使用了幾次。

> 在呼叫位置展開還有另一項可見效果：巨集主體內引發的中止，會回報巨集 _呼叫_ 的行號，而非巨集定義內的行號。這是 [巧妙錯誤](./assert-and-abort#error-messages) 編碼的一部分，也是失敗的 `assert!` 或 `assert_eq!` 會指向你程式碼中的行，而非標準函式庫中某處的原因——在撰寫斷言輔助工具時，這是偏好巨集而非一般函式的好理由。

## 標準函式庫中的巨集 (Macros in the Standard Library) {#macros-in-the-standard-library}

[標準函式庫](./standard-library) 大量使用巨集，而巨集是操作其核心型別的慣用方式。我們已經看過 [vector 巨集](./vector#vector-macros)；`Option` 與整數型別也各自有一組巨集：

```move file=packages/samples/sources/move-basics/macros.move anchor=std_macros

```

以下快速說明可在哪裡找到它們：

- [std::vector](https://docs.sui.io/references/framework/std/vector) - `do!`、`map!`、`filter!`、
  `fold!`、`count!`、`any!`、`all!`、`tabulate!` 等；
- [std::option](https://docs.sui.io/references/framework/std/option) - `do!`、`map!`、
  `destroy_or!`、`extract_or!`、`is_some_and!`；
- 整數模組，例如 [std::u64](https://docs.sui.io/references/framework/std/u64) - `do!`、
  `range_do!`、`max_value!`；
- [std::unit_test](https://docs.sui.io/references/framework/std/unit_test) - `assert_eq!` 與
  `assert_ref_eq!`，可於測試中使用。

本節涵蓋巨集的日常使用方式；完整功能集——包含巨集的方法語法、型別位置中的 `$` 運算式，以及衛生規則——請參閱 Move 參考文件。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [巨集函式](./../../reference/functions/macros)。
