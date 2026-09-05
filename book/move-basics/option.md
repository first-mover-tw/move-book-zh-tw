---
description: Move 中的選項類型 (Option type)：表示可能不存在的值、建立與檢查選項、安全擷取值，以及使用選項巨集 (option macros) 處理選項。
title: 選項 (Option)
keywords:
  - Move
  - Sui
  - Move tutorial
  - option
questions:
  - What is Option in Move?
  - How do I use Option in Move?
  - What is The Option Type in Move?
  - What is Creating and Using an Option in Move?
answer: 'The Option type in Move: represent a value that may be absent, create and inspect options, extract values safely, and process them with option macros.'
goal:
  description: 'Reader understands the Option type in Move: represent a value that may be absent, create and inspect options, extract values safely, and process them with option macros'
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

# 選項 (Option) {#option}

有些資料本質上是可選的：使用者可能有也可能沒有中間名，查詢可能找到也可能找不到相符項目。Move 沒有 `null` 或 `undefined` 值——`String` 型別的變數一定持有一個字串——因此，必須以其他方式表達值不存在的情況。

第一個直覺可能是保留一個特殊值作為標記：以空字串表示缺少的中間名，以零表示缺少的數字。這種方式可行——直到空字串成為有效輸入，而且每個函式都必須記住哪些值是「實際」值、哪些是預留位置。標準函式庫提供了更好的工具：`Option` 型別，這是 Move 從 Rust 借用的概念。

## Option 型別 (The Option Type) {#the-option-type}

`Option<Element>` 是 `Element` 型別值的包裝器，且一定處於兩種狀態之一，慣例上稱為 `Some` 與 `None`：

- `Some` - 此選項包含一個值；
- `None` - 此選項為空。

選項不會與其包裝的值混淆：`Option<String>` 並非 `String`，必須先檢查並取出該值才能使用。值可能不存在的情況會成為型別的一部分，顯示在每個簽章中，而非每個呼叫端都必須記住的慣例。

`Option` 定義於[標準函式庫](./standard-library)，且如同 `vector`，會被[隱含匯入](./standard-library#implicit-imports)——不需要 `use` 陳述式即可在任何模組中使用。`Element` 型別參數使其成為[泛型](./generics)：同一份定義可用於 `Option<u64>`、`Option<String>` 與任何其他元素型別。

以下是上述問題中的使用者紀錄，並以 `Option<String>` 表達可選欄位：

```move file=packages/samples/sources/move-basics/option.move anchor=registry

```

`middle_name` 欄位的型別精確表達了特殊值方式無法表達的內容：該值可能不存在，且沒有任何 `String`——不論是否為空——被保留作為標記。兩種情況分別使用 `option::some(value)` 與 `option::none()` 建立：

```move file=packages/samples/sources/move-basics/option.move anchor=registry_use

```

## 建立與使用 Option (Creating and Using an Option) {#creating-and-using-an-option}

建立後，可以檢查選項是否有值、讀取值，以及將其清空：

```move file=packages/samples/sources/move-basics/option.move anchor=usage

```

> `borrow` 函式會產生該值的*參考*——一種不必將值從選項中取出即可讀取它的方式。本章稍後的[參考](./references#immutable-references)章節將介紹參考。

下表列出 `std::option` 模組最常用的函式；完整清單請參閱[模組文件][option-stdlib]：

<div class="modules-table">

| 函式                   | 說明                          | 中止條件   |
| ---------------------- | ----------------------------- | ---------- |
| `is_some`              | 若選項持有值則回傳 `true`     | -          |
| `is_none`              | 若選項為空則回傳 `true`       | -          |
| `contains`             | 若選項持有指定值則回傳 `true` | -          |
| `borrow`               | 回傳值的參考                  | 選項為空   |
| `borrow_mut`           | 回傳值的可變參考              | 選項為空   |
| `fill`                 | 將值放入空選項                | 選項持有值 |
| `extract`              | 取出值，並將選項保留為空      | 選項為空   |
| `swap`                 | 取代值，並回傳舊值            | 選項為空   |
| `destroy_some`         | 銷毀選項，並回傳值            | 選項為空   |
| `destroy_none`         | 銷毀空選項                    | 選項持有值 |
| `destroy_with_default` | 銷毀選項，並回傳值或預設值    | -          |

</div>

如同 `vector`，`Option` 會從元素型別繼承其能力：非[可丟棄](./drop-ability)型別的選項不能被忽略，且必須使用上述其中一個 `destroy_*` 函式明確銷毀。

## Option 巨集 (Option Macros) {#option-macros}

如同 [vector 巨集](./vector#vector-macros)，選項巨集會以單一運算式取代常見的先檢查再取出序列：

```move file=packages/samples/sources/move-basics/option.move anchor=macros

```

其他常用巨集包括 `map!`、`filter!`、`extract_or!` 與 `do_ref!`——完整清單可見於[模組文件][option-stdlib]，而一般巨集則會在本章稍後的[巨集函式](./macros)章節中介紹。

## 底層實作 (Under the Hood) {#under-the-hood}

`Option` 被定義為具有單一欄位的結構：一個 `Element` 的 `vector`，它一定為空（`None`）或恰好持有一個值（`Some`）：

```move
module std::option;

/// 對可能存在或不存在之值的抽象。
public struct Option<Element> has copy, drop, store {
    vec: vector<Element>
}
```

> 你可能會驚訝於 `Option` 是包含 `vector` 的結構，而不是 [enum][enum-reference]。這是歷史因素：在該語言支援 enum 之前，`Option` 就已加入 Move。在其型別起源的 Rust 中，`Option`*是*具有 `Some` 與 `None`*變體*的 enum——Move 保留了這個術語。

此表示法屬於實作細節：上述函式與巨集涵蓋了一般用法，而 `vec` 欄位絕不會被直接存取。

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::option][option-stdlib] 模組文件。

[enum-reference]: ./../../reference/enums
[option-stdlib]: https://docs.sui.io/references/framework/std/option
