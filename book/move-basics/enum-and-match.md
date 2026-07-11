---
description: 枚舉 (Enum) 與模式比對 (Pattern Matching)
---

# Enum 與 Match (Enums and Match) {#enums-and-match}

`enum`（列舉）是使用者自訂的資料結構，與 [struct](./struct) 不同的是，它可以表示多種變體（variant）。每個變體可以包含基本型別、struct，或其他 enum。不過，遞迴的 enum 定義——類似遞迴 struct 定義——是不被允許的。

## 定義 (Definition) {#definition}

enum 使用 `enum` 關鍵字定義，後面接可選的能力（ability）以及一個變體定義的區塊。每個變體都有一個標籤名稱，並可選擇性地包含位置值（positional values）或具名欄位。一個 enum 必須至少有一個變體；每個變體的形狀在定義時就固定了，變體總數可以相對較大——最多可到 100 個。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=definition

```

在上面的程式碼範例中，我們定義了一個公開的 `Segment` enum，它具有 `drop` 和 `copy` 能力，並有 3 個變體：

- `Empty`，沒有欄位。
- `String`，包含一個型別為 `String` 的位置欄位。
- `Special`，使用具名欄位：型別為 `vector<u8>` 的 `content` 以及型別為 `u8` 的 `encoding`。

## 實例化 (Instantiating) {#instantiating}

enum 是*內部*於定義它的模組。這表示 enum 只能在同一個模組內被建構、讀取與拆解。

[與 struct 類似](./struct#creating-an-instance)，enum 的實例化方式是指定型別、變體，以及該變體所定義欄位的值。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=constructors

```

依照使用情境，你可能想提供公開的建構函式（constructor），或是在應用邏輯內部實例化 enum。

## 在型別定義中使用 (Using in Type Definitions) {#using-in-type-definitions}

使用 enum 的最大好處，是能夠用單一型別來表示多種不同的資料結構。為了展示這一點，讓我們定義一個包含 `Segment` 值向量的 struct：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=struct

```

Segment enum 的所有變體都共用同一個型別——`Segment`——這讓我們能夠建立一個包含不同變體實例的同質向量（homogeneous vector）。這種靈活性是 struct 無法達成的，因為每個 struct 只定義單一、固定的形狀。

> `Segments` 是一個[位置 struct](./struct#positional-structs)，包裝了單一 `vector<Segment>` 欄位；注意它的能力是宣告在括號之後。

## 模式比對 (Pattern Matching) {#pattern-matching}

與 struct 不同，enum 在存取內部值或檢查變體時需要特殊處理。我們無法使用 `.`（點）語法讀取 enum 的內部欄位，因為我們需要確保正在嘗試存取的值是正確的那一個。為此，Move 提供了*模式比對*語法。

> 本章並不打算涵蓋 Move 中模式比對的所有功能。請參閱 Move 參考手冊中的[模式比對](./../../reference/control-flow/pattern-matching)章節。

模式比對讓我們可以根據值的*模式*來決定邏輯走向。它是透過 `match` 運算式來執行，後面接括號中被比對的值，以及一個*匹配分支（match arm）*的區塊，定義模式以及當模式符合時要執行的運算式。

讓我們擴充範例，新增一組類似 `is_variant` 的函式，讓外部套件可以檢查變體，先從 `is_empty` 開始：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty

```

`match` 關鍵字開始這個運算式，`s` 是被測試的值。每個匹配分支都會檢查 `Segment` enum 的特定變體。如果 `s` 符合 `Segment::Empty`，函式會回傳 `true`；否則回傳 `false`。

對於帶有欄位的變體，我們需要把內部結構繫結到區域變數（即使我們不使用它們，也要用 `_` 標記未使用的值以避免編譯器警告）。

### 技巧 #1 - _any_ 條件 (Trick #1 - _any_ Condition) {#trick-1---_any_-condition}

Move 編譯器會推斷 `match` 運算式中所用值的型別，並確保*匹配分支*是窮盡的（exhaustive）——也就是說，所有可能的變體或值都必須被涵蓋。

不過，在某些情況下，例如比對基本型別的值或像向量這樣的集合，列出每種可能的情況並不實際。針對這種情況，match 支援萬用字元模式（`_`），它扮演預設分支的角色。當沒有其他模式符合時，這個分支就會被執行。

我們可以透過簡化 `is_empty` 函式，並把非 `Empty` 的變體替換成萬用字元來展示這一點：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty_2
public fun is_empty(s: &Segment): bool {

```

同樣地，我們可以用相同的方式定義 `is_special` 和 `is_string`：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=accessors

```

### 技巧 #2 - `try_into` 輔助函式 (Trick #2 - `try_into` Helpers) {#trick-2---try_into-helpers}

新增 `is_variant` 函式後，我們讓外部模組可以檢查 enum 實例代表哪個變體。不過，這通常還不夠——由於 enum 是內部於其模組，外部程式碼仍然無法存取變體的內部值。

處理這個問題的常見模式是定義 `try_into` 函式。這些函式會比對值，如果 `match` 成功，就回傳一個包含內部內容的 `Option`。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=try_into_inner_string

```

這種模式以受控的方式安全地暴露內部資料，不會有中止（abort）的風險。

### 技巧 #3 - 比對基本值 (Trick #3 - Matching on Primitive Values) {#trick-3---matching-on-primitive-values}

Move 中的 `match` 運算式可以用於任何型別的值——enum、struct 或基本型別。為了展示這一點，讓我們實作一個 `to_string` 函式，從 `Segment` 建立一個新的 `String`。在 `Special` 變體的情況下，我們會比對 `encoding` 欄位來決定如何解讀 `content`：`0` 代表 UTF-8，`1` 代表較嚴格的 ASCII 編碼。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=to_string

```

這個函式展示了幾個重點：

- 巢狀 `match` 運算式可以用於更深層的邏輯分支。
- 萬用字元對於涵蓋像 `u8` 這種基本型別的所有可能值是不可或缺的。
- 這個函式以參考方式接收 `s`，但匹配分支是*依值*繫結內部值的。`*s` 運算式讓這件事成為可能：[解參考運算子](./references#dereferencing) `*` 會複製參考背後的值，這之所以被允許，是因為 `Segment` 具有 `copy` 能力。
- 萬用字元分支使用不帶中止碼的 `abort` 來拒絕未知的編碼——這是一種*乾淨中止*，在[中止執行](./assert-and-abort)章節中有介紹。

## 最終測試 (The Final Test) {#the-final-test}

現在我們可以使用已新增的功能，完成之前開始的測試。讓我們建立一個場景，把 enum 建構到一個向量中。

```move file=packages/samples/sources/move-basics/enum-and-match-2.move anchor=enum_test

```

這個測試展示了完整的 enum 工作流程：實例化不同的變體、使用公開的存取函式（accessor），並透過模式比對執行邏輯。這應該足以讓你上手了！

想進一步了解 enum 與模式比對，請參閱[延伸閱讀](#further-reading)章節中列出的資源。

## 總結 (Summary) {#summary}

- enum 是使用者自訂的型別，可以用單一型別表示多種變體。
- 每個變體可以包含不同型別的資料（基本型別、struct 或其他 enum）。
- enum 內部於定義它的模組，存取時需要模式比對。
- 模式比對使用 `match` 運算式完成，它：
  - 可用於 enum、struct 和基本值；
  - 必須處理所有可能的情況（窮盡）；
  - 支援 `_` 萬用字元模式來處理剩餘的情況；
  - 可以回傳值，並用於運算式中；
- enum 的常見模式包括 `is_variant` 檢查與 `try_into` 輔助函式。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的 [Enums](./../../reference/enums)
- Move 參考手冊中的[模式比對](./../../reference/control-flow/pattern-matching)
