---
description: Move 中的字串 (Strings)：Sui 智慧合約中的字串常值、UTF-8 與 ASCII 字串 (String) 型別、常見操作，以及它們之間的轉換。
title: 字串 (String)
keywords:
  - Move
  - Sui
  - Move tutorial
  - string
questions:
  - What is String in Move?
  - How do I use String in Move?
  - What is Strings Are Bytes in Move?
  - What is String Literals in Move?
answer: 'Strings in Move: string literals, the UTF-8 and ASCII String types, common operations, and conversions between them in Sui smart contracts.'
goal:
  description: 'Reader understands strings in Move: string literals, the UTF-8 and ASCII String types, common operations, and conversions between them in Sui smart contracts'
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

# 字串 (String) {#string}

雖然 Move 沒有內建型別可表示字串，但其在 [標準函式庫](./standard-library)中提供了兩種標準字串實作。`std::string` 模組定義了 `String` 型別及 UTF-8 編碼字串的方法；另一個模組 `std::ascii` 則提供 ASCII `String` 型別及其方法。

> 兩種型別都名為 `String`，一開始可能令人困惑。當區別很重要時，我們會以其模組來稱呼：`string::String` 與 `ascii::String`。在大多數應用程式原始碼中，應使用 UTF-8 的 `string::String` 型別。

## 字串是位元組 (Strings Are Bytes) {#strings-are-bytes}

無論你使用哪一種字串型別，重要的是要知道字串只是位元組。`string` 與 `ascii` 模組提供的只是包裝器：包裝器確實提供安全檢查與操作字串的方法，但歸根究柢，它們只是位元組向量。

```move file=packages/samples/sources/move-basics/string.move anchor=custom

```

兩種標準字串型別都遵循完全相同的模式：持有 `vector<u8>` 的結構。它們與一般位元組向量，以及彼此之間的差異，在於它們對內容所提供的*保證*：

- `ascii::String` 保證每個位元組都是有效的 ASCII 字元。ASCII 是最早且最簡單的字元編碼：它定義了 128 個字元——拉丁字母、數字和標點符號——且每個字元恰好佔用一個位元組。
- `string::String` 保證位元組為有效的 UTF-8。UTF-8 是現代的標準編碼：它可使用每個字元一至四個位元組表示任何 Unicode 字元——字母、象形文字、表情符號。

UTF-8 向後相容於 ASCII：每個 ASCII 字串也都是有效的 UTF-8 字串，但反之則不然。

## 字串常值 (String Literals) {#string-literals}

[常值](./expression#literals)是直接寫在原始碼中的值。Move 提供兩種撰寫字串的語法：字串常值 `"..."` 與位元組字串常值 `b"..."`。位元組字串一律產生 `vector<u8>`，而字串常值的型別則會根據上下文*推斷*——它會成為編譯器在該位置預期的三種攜帶位元組型別之一（`vector<u8>`、`string::String` 或 `ascii::String`）：

```move file=packages/samples/sources/move-basics/string.move anchor=literals

```

編譯器也會在編譯時檢查常值內容是否符合預期型別。作為 `ascii::String` 使用的字串常值只能包含 ASCII 字元，以下原始碼無法編譯：

```move
let s: std::ascii::String = "héllo";
//                          ^ 錯誤！'é' 不是有效的 ASCII 字元
```

若編譯器無法從上下文判斷型別，常值預設為 `vector<u8>`，並會發出警告。這也是無法直接在裸常值上呼叫方法的原因——`"Hello".to_string()` 無法編譯，因為編譯器在解析方法前，無法推斷常值的型別。`vector<u8>` 尚不是字串——兩個字串模組都提供函式，可在執行時將位元組轉換為字串，如下所示。

### 跳脫序列 (Escape Sequences) {#escape-sequences}

某些字元無法直接輸入至常值中：換行、定位字元，或會結束常值的 `"` 字元本身。如同多數語言，Move 使用反斜線 `\` 來*跳脫*特殊字元。任意位元組也可寫成後接兩個十六進位數字的 `\x`。

```move file=packages/samples/sources/move-basics/string.move anchor=escapes

```

## 操作 UTF-8 字串 (Working with UTF-8 Strings) {#working-with-utf-8-strings}

雖然標準函式庫中有兩種字串型別，`string` 模組應視為預設選擇。它原生實作了許多常見操作，運用低階且經過最佳化的執行時期原始碼，以獲得更優異的效能。相較之下，`ascii` 模組完全以 Move 實作，依賴較高階的抽象機制，因此較不適合效能關鍵的工作。

### 定義 (Definition) {#definition}

`std::string` 模組中的 `String` 型別定義如下：

```move
module std::string;

/// `String` 持有一連串保證為 utf8 格式的位元組。
public struct String has copy, drop, store {
    bytes: vector<u8>,
}
```

_請參閱 [std::string][string-stdlib] 模組的完整文件。_

### 建立字串 (Creating a String) {#creating-a-string}

如上所示，字串常值是建立 `String` 最常見的方式。或者，既有的 `vector<u8>` 可在執行時透過 `string::utf8` 函式，或 `vector<u8>` 型別上方便的別名 `.to_string()`，轉換為 `String`。若位元組不是有效的 UTF-8，兩者皆會中止。

```move file=packages/samples/sources/move-basics/string.move anchor=utf8

```

> Sui 執行環境會自動將交易輸入中的位元組向量轉換為 `String`。因此，在許多情況下，直接於[交易](./../concepts/what-is-a-transaction)內建立 `String` 並非必要。

### 常見操作 (Common Operations) {#common-operations}

UTF-8 `String` 提供多種操作字串的方法。最常見的字串操作包括：串接、切片、搜尋與取得長度。此外，針對自訂字串操作，可使用 `as_bytes()` 方法取得底層位元組向量。

```move file=packages/samples/sources/move-basics/string.move anchor=common_ops

```

請注意沒有出現項目時 `index_of` 的行為：它不會中止或回傳 `Option`，而是回傳字串長度——即最後一個位元組之後的索引。也請注意清單中*沒有*的項目：Move 沒有字串插值或格式化功能，也無法依分隔符號分割字串。智慧合約中的字串通常用於儲存與顯示，而非剖析。

> 較舊的原始碼可能使用 `sub_string` 與 `bytes` 函式——它們是 `substring` 與 `as_bytes` 的已淘汰別名。

### 將數字轉換為字串 (Converting Numbers to Strings) {#converting-numbers-to-strings}

常見的實務工作是依數字建立字串——用於名稱、標籤或錯誤訊息。每種無號整數型別都有 `to_string` 方法，可將數字轉換為其十進位表示法。

```move file=packages/samples/sources/move-basics/string.move anchor=number_to_string

```

### 安全的 UTF-8 操作 (Safe UTF-8 Operations) {#safe-utf-8-operations}

預設的 `utf8` 方法若傳入的位元組不是有效 UTF-8，可能會中止。若你不確定傳入的位元組是否有效，應改用 `try_utf8` 方法。它會回傳 `Option<String>`；若位元組不是有效 UTF-8，該值不包含任何內容，否則包含字串。

> 提示：名稱以 `try_*` 開頭的函式通常會回傳 `Option`。若操作成功，結果會包裝於 `Some` 中；若失敗，函式會回傳 `None`。Move 中常見的這項命名慣例受到 Rust 啟發。

```move file=packages/samples/sources/move-basics/string.move anchor=safe_utf8

```

### UTF-8 限制 (UTF-8 Limitations) {#utf-8-limitations}

`string` 模組不提供存取字串中個別字元的方式。這是因為 UTF-8 是可變長度編碼，字元長度可介於 1 至 4 個位元組之間。同樣地，`length()` 方法回傳的是字串中的位元組數量，而非字元數量。

```move file=packages/samples/sources/move-basics/string.move anchor=limitations

```

位元組位置對於接受索引的方法很重要，例如 `substring` 與 `insert`。這些方法會驗證字元邊界，若指定的索引落在字元中間，便會中止：

```move file=packages/samples/sources/move-basics/string.move anchor=substring_abort

```

> 「字串是位元組」還有另一項結果：兩個在螢幕上看起來相同的字串，可能有不同的位元組表示法。例如，「é」可編碼為單一字元，也可編碼為「e」後接組合重音符號——它們顯示相同，但比較時不同，因為 `==` 比較的是位元組，而不是讀者所見的內容。

## ASCII 字串 (ASCII Strings) {#ascii-strings}

`ascii::String` 型別適合已知為純拉丁字母、數字與標點符號的值：代號、符號、識別字或 URL。例如，[Sui Framework](./../programmability/sui-framework) 對 `CoinMetadata` 型別的 `symbol` 欄位使用 `ascii::String`。

ASCII 編碼以表達能力換取簡潔性：每個字元恰好是一個位元組。這解除 UTF-8 字串的限制——`ascii::String` 可操作個別字元（以 `ascii::Char` 型別表示），並提供對 UTF-8 而言會有歧義的方法，例如變更字串的大小寫。

建立 ASCII 字串的方式與 UTF-8 字串一樣：使用字串常值，或在執行時轉換 `vector<u8>`——這次使用 `ascii::string` 函式或 `vector<u8>` 上的 `.to_ascii_string()` 別名。它也有對應的 `try_string`，遵循上文所述相同的 `try_*` 慣例。

兩種字串型別可互相轉換。由於每個 ASCII 字串也都是有效的 UTF-8，對 `ascii::String` 呼叫 `to_string()` 一律成功；反向轉換 `to_ascii()` 則會在字串包含非 ASCII 字元時中止。

```move file=packages/samples/sources/move-basics/string.move anchor=ascii

```

_請參閱 [std::ascii][ascii-stdlib] 模組的完整文件。_

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::string][string-stdlib] 模組文件。
- [std::ascii][ascii-stdlib] 模組文件。

[string-stdlib]: https://docs.sui.io/references/framework/std/string
[ascii-stdlib]: https://docs.sui.io/references/framework/std/ascii
