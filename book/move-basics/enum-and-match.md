---

description: "Enums and pattern matching in Move: define variant types, use match expressions, and handle multiple cases in smart contracts."
---

# 列舉與模式匹配 (Enums and Match)

列舉 (enum) 是一種使用者定義的資料結構，與 [結構 (struct)](./struct) 不同的是，它可以表示多個 **變體 (variants)**。每個變體可以包含原始類型、結構或其他列舉。然而，與遞迴結構定義類似，不允許定義遞迴列舉。

## 定義 (Definition)

使用 `enum` 關鍵字來定義列舉，後接選擇性的能力 (abilities) 和變體定義區塊。每個變體都有一個標籤名稱，並可選擇包含位置欄位 (positional values) 或具名欄位 (named fields)。列舉必須至少包含一個變體。每個變體的結構不具備靈活性，但變體的總數可以相對較多 — 最多可達 100 個。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=definition

```

在上面的範例中，我們定義了一個公開的 `Segment` 列舉，它具備 `drop` 和 `copy` 能力，以及 3 個變體：

- `Empty`: 沒有任何欄位。
- `String`: 包含一個 `String` 類期的位置欄位。
- `Special`: 使用具名欄位：`content` (類型為 `vector<u8>`) 和 `encoding` (類型為 `u8`)。

## 實例化 (Instantiating)

列舉對其定義所在的模組而言是 **內部 (internal)** 的。這意味著列舉僅能在同一個模組內被建構、讀取和解構。

[與結構類似](./struct#create-and-use-an-instance)，藉由指定類型、變體以及該變體所定義的欄位值，即可實例化列舉。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=constructors

```

根據使用案例的不同，您可能希望提供公開的建構函式，或在應用程式邏輯內部實例化列舉。

## 在類型定義中使用 (Using in Type Definitions)

使用列舉的最大好處是能夠在單一類型下表示多樣的資料結構。為了演示這一點，讓我們定義一個包含 `Segment` 值向量的結構：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=struct

```

`Segment` 列舉的所有變體都共享同一個類型 — `Segment` — 這使我們能夠建立一個包含不同變體實例的同質向量。這種靈活性是結構無法實現的，因為每個結構都定義了單一且固定的形狀。

## 模式匹配 (Pattern Matching)

與結構不同，列舉在存取內部值或檢查變體時需要特殊處理。我們無法直接使用 `.` (點) 語法來讀取列舉的內部欄位，因為我們需要確保正在存取的確實是正確的變體。為此，Move 提供了 **模式匹配 (pattern matching)** 語法。

> 本章並不打算涵蓋 Move 中模式匹配的所有功能。請參閱 Move 參考手冊中的 [模式匹配 (Pattern Matching)](./../../reference/control-flow/pattern-matching) 章節。

模式匹配允許根據值的 **模式 (pattern)** 來決定邏輯。它使用 `match` 表達式執行，其後括號中是要匹配的值，接著是 **匹配臂 (match arms)** 區塊，定義了模式以及當模式正確時要執行的表達式。

讓我們擴展範例，添加一組類似 `is_variant` 的函式，以便外部套件可以檢查變體。從 `is_empty` 開始：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty

```

`match` 關鍵字啟動表達式，`s` 是受測值。每個匹配臂都會檢查 `Segment` 列舉的特定變體。如果 `s` 匹配 `Segment::Empty`，函式傳回 `true`；否則，傳回 `false`。

對於具有欄位的變體，我們需要將內部結構綁定到局部變數（即使我們不使用它們，也會用 `_` 標記未使用的值，以避免編譯器警告）。

### 技巧 #1 — 「任何」(any) 條件

Move 編譯器會推斷 `match` 表達式中所用值的類型，並確保 **匹配臂** 是窮盡的 (exhaustive) — 也就是必須涵蓋所有可能的變體或值。

然而，在某些情況下（例如匹配原始類型的值或向量之類的集合），列出每一個可能的情形是不可行的。對於這些情況，`match` 支援萬用字元模式 (`_`)，它作為預設匹配臂 (default arm)。當沒有其他模式匹配時，就會執行此匹配臂。

我們可以透過簡化 `is_empty` 函式並將非 `Empty` 的變體替換為萬用字元來演示這一點：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=is_empty_2
public fun is_empty(s: &Segment): bool {

```

同樣地，我們可以使用相同的方法來定義 `is_special` 和 `is_string`：

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=accessors

```

### 技巧 #2 — `try_into` 輔助工具

透過添加 `is_variant` 函式，我們讓外部模組能夠檢查列舉實例代表哪個變體。然而，這通常還不夠 — 由於列舉對其模組而言是內部的，外部程式碼仍然無法存取變體的內部值。

解決此問題的一種常見模式是定義 `try_into` 函式。這些函式會對值進行匹配，如果 `match` 成功，則傳回一個包含內部內容的 `Option`。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=try_into_inner_string

```

這種模式以可控的方式安全地公開內部資料，並避免程式中斷。

### 技巧 #3 — 匹配原始類型值

Move 中的 `match` 表達式可以用於任何類型的值 — 列舉、結構或原始類型。為了演示這一點，讓我們實作一個 `to_string` 函式，從 `Segment` 建立一個新的 `String`。在 `Special` 變體的情況下，我們將匹配 `encoding` 欄位以決定如何解碼內容。

```move file=packages/samples/sources/move-basics/enum-and-match.move anchor=to_string

```

這個函式演示了兩個關鍵點：

- 巢狀的 `match` 表達式可用於更深層的邏輯分支。
- 萬用字元對於涵蓋 `u8` 等原始類型中所有可能的值至關重要。

## 最終測試

現在我們可以結合所添加的功能來完成之前開始的測試。讓我們建立一個將列舉建構進向量的場景。

```move file=packages/samples/sources/move-basics/enum-and-match-2.move anchor=enum_test

```

此測試演示了完整的列舉工作流程：實例化不同的變體、使用公開的存取方法，以及執行模式匹配邏輯。這應該足以讓您開始使用了！

若要進一步了解列舉和模式匹配，請參閱 [延伸閱讀](#further-reading) 部分所列的資源。

## 總結

- 列舉是使用者定義的類型，可以在單一類型下表示多個變體。
- 每個變體可以包含不同類型的資料（原始類型、結構或其他列舉）。
- 列舉對其定義所在的模組而言是內部的，需要模式匹配來存取。
- 模式匹配使用 `match` 表達式執行，該表達式：
  - 適用於列舉、結構和原始類型值；
  - 必須處理所有可能的情況（具備窮盡性）；
  - 支援使用 `_` 萬用字元模式來處理其餘情況；
  - 可以傳回值並用於表達式中。
- 列舉的常見模式包括 `is_variant` 檢查和 `try_into` 輔助函式。

## 延伸閱讀 {#further-reading}

- Move 參考手冊中的 [列舉 (Enums)](./../../reference/enums)。
- Move 參考手冊中的 [模式匹配 (Pattern Matching)](/reference/control-flow/pattern-matching)。
