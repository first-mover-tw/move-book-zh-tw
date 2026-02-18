# 字串 (String)

雖然 Move 沒有內建的類型來表示字串，但在 [標準庫](./standard-library) 中有兩種字串的標準實作。`std::string` 模組定義了 `String` 類型以及適用於 UTF-8 編碼字串的方法；第二個模組 `std::ascii` 則提供了 ASCII `String` 類型及其方法。

> Sui 執行環境會在交易輸入中自動將位元組向量 (bytevector) 轉換為 `String`。因此，在許多情況下，沒有必要直接在 [交易區塊 (Transaction Block)](./../concepts/what-is-a-transaction) 中建構 String。

## 字串即位元組

無論您使用哪種類型的字串，重要的是要知道字串本質上就是位元組。`string` 和 `ascii` 模組提供的封裝器僅僅是：封裝器。它們確實提供了安全檢查和處理字串的方法，但歸根結底，它們就是位元組向量。

```move file=packages/samples/sources/move-basics/string.move anchor=custom

```

## 使用 UTF-8 字串

雖然標準庫中有兩種類型的字串（`string` 和 `ascii`），但應將 `string` 模組視為預設。它對許多常見操作具有原生實作，利用低階、優化的執行時期程式碼來獲得卓越的效能。相比之下，`ascii` 模組完全由 Move 實作，依賴於高階抽象，這使其不太適合效能關鍵型的任務。

### 定義

`std::string` 模組中的 `String` 類型定義如下：

```move
module std::string;

/// `String` 持有一系列保證為 utf8 格式的位元組。
public struct String has copy, drop, store {
    bytes: vector<u8>,
}
```

_參閱 [std::string 模組完整文件][string-stdlib]。_

### 建立字串

要建立新的 UTF-8 `String` 實例，您可以使用 `string::utf8` 方法。[標準庫](./standard-library) 為 `vector<u8>` 提供了一個別名 `.to_string()` 以方便使用。

```move file=packages/samples/sources/move-basics/string.move anchor=utf8

```

### 常見操作

UTF-8 字串提供了許多處理字串的方法。最常見的操作包括：串接 (concatenation)、切片 (slicing) 和獲取長度。此外，對於自定義字串操作，可以使用 `bytes()` 方法來獲取底層的位元組向量。

```move
let mut str = b"Hello,".to_string();
let another = b" World!".to_string();

// append(String) 將內容添加到字串末尾
str.append(another);

// `sub_string(start, end)` 複製字串的切片
str.sub_string(0, 5); // "Hello"

// `length()` 傳回字串中的位元組數
str.length(); // 12 (位元組)

// 方法也可以連寫！獲取子字串的長度
str.sub_string(0, 5).length(); // 5 (位元組)

// 字串是否為空
str.is_empty(); // false

// 獲取底層位元組向量以進行自定義操作
let bytes: &vector<u8> = str.bytes();
```

### 安全的 UTF-8 操作

如果傳入的位元組不是有效的 UTF-8，則預設的 `utf8` 方法可能會中斷。如果您不確定所傳遞的位元組是否有效，則應改用 `try_utf8` 方法。它會傳回一個 `Option<String>`，如果位元組不是有效的 UTF-8，則不包含任何值 (None)，否則傳回字串。

> 提示：名稱以 `try_*` 開頭的函式通常傳回 `Option`。如果操作成功，結果將封裝在 `Some` 中。如果失敗，函式將傳回 `None`。這種命名約定在 Move 中很常見，其靈感源自 Rust。

```move file=packages/samples/sources/move-basics/string.move anchor=safe_utf8

```

### UTF-8 的限制

`string` 模組不提供存取字串中單個字元的方法。這是因為 UTF-8 是一種變長編碼，一個字元的長度可以在 1 到 4 個位元組之間。同樣地，`length()` 方法傳回的是字串中的位元組數，而不是字元數。

然而，諸如 `sub_string` 和 `insert` 之類的方法會驗證字元邊界，如果指定的索引落在字元中間，則會中斷執行。

## ASCII 字串 {#ascii-strings}

此部分即將推出！

## 延伸閱讀

- [`std::string`][string-stdlib] 模組文件。
- [`std::ascii`][ascii-stdlib] 模組文件。

[enum-reference]: /reference/enums.html
[string-stdlib]: https://docs.sui.io/references/framework/std/string
[ascii-stdlib]: https://docs.sui.io/references/framework/std/ascii
