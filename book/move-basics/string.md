---
description: Move 中的字串（Strings in Move）：字串字面值 (string literals)、UTF-8 和 ASCII 字串型別
  (String types)、常見操作，以及在 Sui 智能合約中兩者之間的轉換。
---

# 字串 (String) {#string}

雖然 Move 沒有內建型別來表示字串，但它在[標準函式庫](./standard-library)中確實有兩種字串的標準實作。`std::string` 模組定義了 `String` 型別及處理 UTF-8 編碼字串的方法，第二個模組 `std::ascii` 則提供了 ASCII `String` 型別及其方法。

> 兩種型別都叫做 `String`，一開始可能會讓人搞混。當需要區分時，我們會用模組名稱來稱呼它們：`string::String` 和 `ascii::String`。在大多數應用程式碼中，UTF-8 的 `string::String` 才是該使用的型別。

## 字串就是位元組 (Strings Are Bytes) {#strings-are-bytes}

無論你使用哪種型別的字串，重要的是要知道字串其實就是位元組。`string` 和 `ascii` 模組提供的封裝就只是封裝：它們提供了安全性檢查與處理字串的方法，但歸根究柢，它們都只是位元組向量。

```move file=packages/samples/sources/move-basics/string.move anchor=custom

```

兩種標準字串型別都遵循這個確切的模式——一個持有 `vector<u8>` 的結構。讓它們與純粹的位元組向量不同，也讓彼此不同的，是它們對內容所承諾的_保證_：

- `ascii::String` 保證每個位元組都是合法的 ASCII 字元。ASCII 是最古老也最簡單的字元編碼：它定義了 128 個字元——拉丁字母、數字與標點符號——每個字元恰好佔一個位元組。
- `string::String` 保證位元組是合法的 UTF-8。UTF-8 是現代標準編碼：它可以用每個字元一到四個位元組來表示任何 Unicode 字元——字母、象形文字、表情符號。

UTF-8 向後相容 ASCII：每個 ASCII 字串同時也是合法的 UTF-8 字串，但反過來則不然。

## 字串字面值 (String Literals) {#string-literals}

[字面值](./expression#literals)是直接寫在原始碼中的值。Move 提供兩種寫字串的語法：字串字面值 `"..."` 與位元組字串字面值 `b"..."`。位元組字串永遠產生 `vector<u8>`，而字串字面值的型別則是根據上下文_推斷_而來——它會變成編譯器在該處所預期的三種承載位元組的型別之一（`vector<u8>`、`string::String` 或 `ascii::String`）：

```move file=packages/samples/sources/move-basics/string.move anchor=literals

```

編譯器也會在編譯期將字面值的內容與預期型別進行核對。若一個字串字面值被用作 `ascii::String`，就必須只包含 ASCII 字元，以下程式碼將無法編譯：

```move
let s: std::ascii::String = "héllo";
//                          ^ 錯誤!'é' 不是有效的 ASCII 字元
```

如果編譯器無法從上下文判斷型別，字面值會預設為 `vector<u8>`，並發出警告。這也是為什麼無法直接在裸字面值上呼叫方法——`"Hello".to_string()` 無法編譯，因為編譯器在解析方法之前無法推斷字面值的型別。`vector<u8>` 還不是字串——兩個字串模組都提供了在執行期將位元組轉換為字串的函式，我們會在下方展示。

### 跳脫序列 (Escape Sequences) {#escape-sequences}

有些字元無法直接輸入到字面值中：換行、定位字元，或是會結束字面值本身的 `"` 字元。和大多數語言一樣，Move 使用反斜線 `\` 來_跳脫_特殊字元。任意位元組也可以寫成 `\x` 後接兩個十六進位數字。

```move file=packages/samples/sources/move-basics/string.move anchor=escapes

```

## 處理 UTF-8 字串 (Working with UTF-8 Strings) {#working-with-utf-8-strings}

雖然標準函式庫中有兩種字串型別，但 `string` 模組應被視為預設選擇。它有許多常見操作的原生實作，利用了經過最佳化的底層執行期程式碼，帶來更優異的效能。相較之下，`ascii` 模組完全以 Move 實作，依賴較高層的抽象，使其較不適合對效能要求嚴苛的任務。

### 定義 (Definition) {#definition}

`std::string` 模組中的 `String` 型別定義如下：

```move
module std::string;

/// `String` 保存一個位元組序列,並保證是 utf8 格式。
public struct String has copy, drop, store {
    bytes: vector<u8>,
}
```

_完整文件請見 [std::string][string-stdlib] 模組。_

### 建立字串 (Creating a String) {#creating-a-string}

如上所示，字串字面值是建立 `String` 最常見的方式。此外，也可以在執行期用 `string::utf8` 函式，或其在 `vector<u8>` 型別上的便利別名 `.to_string()`，將既有的 `vector<u8>` 轉換為 `String`。如果位元組不是合法的 UTF-8，兩者都會中止執行。

```move file=packages/samples/sources/move-basics/string.move anchor=utf8

```

> Sui 執行環境會在交易輸入中自動將位元組向量轉換為 `String`。因此在許多情況下，不需要在[交易](./../concepts/what-is-a-transaction)中直接建構 `String`。

### 常見操作 (Common Operations) {#common-operations}

UTF-8 `String` 提供了許多處理字串的方法。字串上最常見的操作有：串接、切片、搜尋，以及取得長度。此外，若要進行自訂的字串操作，可以使用 `as_bytes()` 方法取得底層的位元組向量。

```move file=packages/samples/sources/move-basics/string.move anchor=common_ops

```

注意 `index_of` 在找不到符合項時的行為：它不會中止執行或回傳 `Option`，而是回傳字串的長度——也就是最後一個位元組之後的索引。也要注意清單上_沒有_的東西：Move 沒有字串插值或格式化功能，也沒有依分隔符號切割字串的方法。智慧型合約中的字串通常是用來儲存與顯示，而不是用來解析的。

> 較舊的程式碼可能會使用 `sub_string` 與 `bytes` 函式——它們是 `substring` 與 `as_bytes` 已棄用的別名。

### 將數字轉換為字串 (Converting Numbers to Strings) {#converting-numbers-to-strings}

一個常見的實務需求是用數字組出字串——用於名稱、標籤，或錯誤訊息。每種無號整數型別都有一個 `to_string` 方法，可將數字轉換為其十進位表示法。

```move file=packages/samples/sources/move-basics/string.move anchor=number_to_string

```

### 安全的 UTF-8 操作 (Safe UTF-8 Operations) {#safe-utf-8-operations}

預設的 `utf8` 方法在傳入的位元組不是合法 UTF-8 時可能會中止執行。如果你不確定傳入的位元組是否合法，應改用 `try_utf8` 方法。它會回傳 `Option<String>`，若位元組不是合法 UTF-8 則不含任何值，否則就是一個字串。

> 提示：名稱以 `try_*` 開頭的函式通常會回傳 `Option`。如果操作成功，結果會被包在 `Some` 中；如果失敗，函式會回傳 `None`。這個在 Move 中常見的命名慣例，靈感來自 Rust。

```move file=packages/samples/sources/move-basics/string.move anchor=safe_utf8

```

### UTF-8 的限制 (UTF-8 Limitations) {#utf-8-limitations}

`string` 模組並未提供存取字串中個別字元的方法。這是因為 UTF-8 是一種可變長度編碼，一個字元的長度可以是 1 到 4 個位元組不等。同樣地，`length()` 方法回傳的是字串中的位元組數，而不是字元數。

```move file=packages/samples/sources/move-basics/string.move anchor=limitations

```

位元組位置對於接受索引的方法（例如 `substring` 與 `insert`）而言相當重要。這些方法會驗證字元邊界，若指定的索引落在某個字元的中間，就會中止執行：

```move file=packages/samples/sources/move-basics/string.move anchor=substring_abort

```

> 「字串就是位元組」還有另一個後果：兩個在畫面上看起來一模一樣的字串，可能有不同的位元組表示法。例如「é」可以被編碼成單一字元，也可以編碼成「e」後接一個組合重音符號——兩者顯示起來相同，但因為 `==` 比較的是位元組而不是讀者看到的內容，所以比較結果會不同。

## ASCII 字串 (ASCII Strings) {#ascii-strings}

`ascii::String` 型別很適合用於已知只包含純拉丁字母、數字與標點符號的值：代碼、符號、識別碼或 URL。舉例來說，[Sui Framework](./../programmability/sui-framework) 就將 `ascii::String` 用於 `CoinMetadata` 型別的 `symbol` 欄位。

ASCII 編碼在表達力上有所欠缺，但在簡潔性上獲得了彌補：每個字元恰好佔一個位元組。這解除了 UTF-8 字串的限制——`ascii::String` 允許對個別字元（以 `ascii::Char` 型別表示）進行操作，並提供了對 UTF-8 而言會有歧義的方法，例如改變字串的大小寫。

建立 ASCII 字串的方式與建立 UTF-8 字串相同：使用字串字面值，或在執行期轉換 `vector<u8>`——這次是用 `ascii::string` 函式，或是 `vector<u8>` 上的 `.to_ascii_string()` 別名。同樣也有依循上述 `try_*` 慣例的 `try_string` 對應版本。

這兩種字串型別可以互相轉換。由於每個 ASCII 字串同時也是合法的 UTF-8，`ascii::String` 上的 `to_string()` 永遠會成功；反向轉換——`to_ascii()`——則會在字串包含非 ASCII 字元時中止執行。

```move file=packages/samples/sources/move-basics/string.move anchor=ascii

```

_完整文件請見 [std::ascii][ascii-stdlib] 模組。_

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::string][string-stdlib] 模組文件。
- [std::ascii][ascii-stdlib] 模組文件。

[string-stdlib]: https://docs.sui.io/references/framework/std/string
[ascii-stdlib]: https://docs.sui.io/references/framework/std/ascii
