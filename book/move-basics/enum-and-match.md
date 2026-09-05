---
description: Move 中的列舉 (Enums) 與模式比對 (pattern matching)：定義變體型別 (variant types)、使用 match 運算式 (match expressions)，並在智慧合約 (smart contracts) 中處理多種情況。
title: 列舉 (Enums) 與模式比對 (Match)
keywords:
  - Move
  - Sui
  - Move tutorial
  - enums
  - match
questions:
  - What is Enums and Match in Move?
  - How do I use Enums and Match in Move?
  - What is Definition in Move?
  - What is Instantiating in Move?
answer: 'Enums and pattern matching in Move: define variant types, use match expressions, and handle multiple cases in smart contracts.'
goal:
  description: 'Reader understands enums and pattern matching in Move: define variant types, use match expressions, and handle multiple cases in smart contracts'
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

# 列舉與比對 (Enums and Match) {#enums-and-match}

列舉是一種使用者自訂的資料結構；不同於 [struct](./struct)，它可以表示多個
變體。每個變體可以包含原始型別、結構或其他列舉。不過，不允許遞迴列舉
定義——這與遞迴結構定義相似。

## 定義 (Definition) {#definition}

列舉使用 `enum` 關鍵字定義，後方接著可選的能力與一個變體定義區塊。每個變體都有
標籤名稱，並可選擇性地包含位置值或具名欄位。列舉至少必須有一個變體；每個變體的形狀
會在定義時固定，變體總數可以相當多——最多 100 個。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=definition

```

在上方的原始碼範例中，我們定義了一個公開的 `Segment` 列舉，它具有 `drop` 與 `copy`
能力，以及 3 個變體：

- `Empty`，不含任何欄位。
- `String`，包含一個型別為 `String` 的位置欄位。
- `Special`，使用具名欄位：型別為 `vector<u8>` 的 `content` 與型別為 `u8` 的 `encoding`。

## 建立執行個體 (Instantiating) {#instantiating}

列舉對定義它們的模組而言是 _內部_ 的。這表示列舉只能在同一個模組內
建立、讀取與解構。

[如同結構](./struct#creating-an-instance)，列舉會透過指定型別、變體及該變體所定義
欄位的值來建立執行個體。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=constructors

```

視使用案例而定，你可能會想提供公開建構子，或將列舉作為應用程式邏輯的一部分在內部
建立執行個體。

## 在型別定義中使用 (Using in Type Definitions) {#using-in-type-definitions}

使用列舉最大的優點，是能在單一型別下表示不同的資料結構。為了展示這點，讓我們定義
一個包含 `Segment` 值向量的結構：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=struct

```

Segment 列舉的所有變體共用相同型別——`Segment`——這讓我們可以建立一個包含不同變體
執行個體的同質向量。結構無法達成這種彈性，因為每個結構只定義單一固定形狀。

> `Segments` 是一個包裝單一 `vector<Segment>` 欄位的
> [位置結構](./struct#positional-structs)；請注意其能力是在括號後方宣告。

## 模式比對 (Pattern Matching) {#pattern-matching}

不同於結構，列舉在存取內部值或檢查變體時需要特殊處理。我們無法單純使用 `.`
（點）語法讀取列舉的內部欄位，因為必須確認嘗試存取的值正確。Move 為此提供了
_模式比對_ 語法。

> 本章無意涵蓋 Move 中模式比對的所有功能。請參閱 Move 參考文件中的
> [模式比對](./../../reference/control-flow/pattern-matching)章節。

模式比對可根據值的 _模式_ 設定邏輯條件。它使用 `match` 運算式執行，後方接著以括號
包住的比對值，以及一組 _比對分支_ 區塊；該區塊定義模式及模式正確時要執行的運算式。

讓我們擴充範例，加入一組類似 `is_variant` 的函式，讓外部套件能檢查變體，先從
`is_empty` 開始：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty

```

`match` 關鍵字開始此運算式，`s` 是正在測試的值。每個比對分支會檢查 `Segment` 列舉的
特定變體。若 `s` 符合 `Segment::Empty`，函式會回傳 `true`；否則會回傳 `false`。

對於含有欄位的變體，我們需要將內部結構繫結至區域變數（即使不使用它們，也要以 `_`
標記未使用的值，避免編譯器警告）。

### 技巧 #1 - _任意_ 條件 (Trick #1 - _any_ Condition) {#trick-1---_any_-condition}

Move 編譯器會推斷 `match` 運算式中所使用值的型別，並確保 _比對分支_ 是完整的——
也就是必須涵蓋所有可能的變體或值。

不過，某些情況下，例如比對原始值或像向量這樣的集合時，無法列出所有可能案例。針對
這些情況，match 支援萬用字元模式（`_`），它會作為預設分支。當沒有其他模式符合時，
便會執行此分支。

我們可以簡化 `is_empty` 函式，並以萬用字元取代非 `Empty` 變體來展示這點：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty_2
public fun is_empty(s: &Segment): bool {

```

同樣地，我們也可以使用相同方法定義 `is_special` 與 `is_string`：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=accessors

```

### 技巧 #2 - `try_into` 輔助函式 (Trick #2 - `try_into` Helpers) {#trick-2---try_into-helpers}

加入 `is_variant` 函式後，我們讓外部模組能檢查列舉執行個體表示哪一個變體。不過，這
通常還不夠——由於列舉對其模組而言是內部的，外部原始碼仍無法存取變體的內部值。

處理此問題的常見模式是定義 `try_into` 函式。這些函式會比對值，並在 `match` 成功時
回傳包含內部內容的 `Option`。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=try_into_inner_string

```

此模式可安全地以受控方式公開內部資料，且不會有中止的風險。

### 技巧 #3 - 比對原始值 (Trick #3 - Matching on Primitive Values) {#trick-3---matching-on-primitive-values}

Move 的 `match` 運算式可用於任何型別的值——列舉、結構或原始型別。為了展示這點，
讓我們實作一個 `to_string` 函式，從 `Segment` 建立新的 `String`。對於 `Special`
變體，我們將比對 `encoding` 欄位以決定如何解讀內容：`0` 代表 UTF-8，而 `1` 代表
更嚴格的 ASCII 編碼。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=to_string

```

此函式展示幾項重點：

- 巢狀 `match` 運算式可用於更深層的邏輯分支。
- 萬用字元對於涵蓋 `u8` 等原始型別的所有可能值至關重要。
- 此函式以參考方式接收 `s`，但比對分支會 _以值方式_ 繫結內部值。`*s`
  運算式使此作法可行：[解參考運算子](./references#dereferencing) `*`
  會複製參考後方的值；由於 `Segment` 具有 `copy`
  能力，因此允許這樣做。
- 萬用字元分支使用不含中止碼的 `abort` 來拒絕未知編碼——這是一種 _乾淨的
  中止_，內容涵蓋於[中止執行](./assert-and-abort)章節。

## 最終測試 (The Final Test) {#the-final-test}

現在，我們可以使用已加入的功能完成先前開始的測試。讓我們建立一個將列舉建置為向量
的情境。

```move file=packages/samples/sources/move-basics/enum-and-match-2.move anchor=enum_test

```

此測試展示完整的列舉工作流程：建立不同變體的執行個體、使用公開存取子，以及透過模式
比對執行邏輯。這應該足以讓你開始使用！

若要深入瞭解列舉與模式比對，請參閱[延伸閱讀](#further-reading)章節中列出的資源。

## 總結 (Summary) {#summary}

- 列舉是使用者自訂型別，可在單一型別下表示多個變體。
- 每個變體可包含不同型別的資料（原始型別、結構或其他列舉）。
- 列舉對其定義模組而言是內部的，且需透過模式比對進行存取。
- 模式比對使用 `match` 運算式完成，其：
  - 可搭配列舉、結構及原始值使用；
  - 必須處理所有可能案例（必須完整）；
  - 支援用於其餘案例的 `_` 萬用字元模式；
  - 可以回傳值並用於運算式；
- 列舉的常見模式包括 `is_variant` 檢查與 `try_into` 輔助函式。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Enums](./../../reference/enums)
- Move 參考文件中的 [Pattern Matching](./../../reference/control-flow/pattern-matching)
