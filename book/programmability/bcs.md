---
description: BCS（二進位規範序列化，Binary Canonical Serialization）in Move：對結構化資料進行編碼與解碼，用於鏈上儲存與跨平台通訊。
---

# Binary Canonical Serialization 二進位標準序列化 (Binary Canonical Serialization) {#binary-canonical-serialization}

Binary Canonical Serialization（BCS）是一種用於結構化資料的二進位編碼格式。它最初是在 Diem 中設計的，後來成為 Move 的標準序列化格式。BCS 簡單、高效、具確定性，且容易用任何程式語言實作。

雖然序列化聽起來像是進階主題，但 BCS 在 Sui 上無所不在：交易的參數是以 BCS 編碼的，物件與事件是以 BCS bytes 的形式儲存 — 也是以此形式在鏈下讀取的，而智慧合約中簽署與驗證的訊息通常也是以 BCS 序列化的 struct。大多數時候編碼是自動幫你處理好的，但遲早會有應用需要手動處理：解碼已簽署的 payload、解析以 `vector<u8>` 參數傳入的原始 bytes，或產生與鏈下客戶端建構結果相符的 bytes。

> 完整的格式規範可在
> [BCS repository](https://github.com/zefchain/bcs) 中取得。

## 格式 (Format) {#format}

BCS 是一種二進位格式，支援最多 256 位元的無號整數、option、boolean、unit（空值）、固定與變動長度的序列，以及 map。此格式的設計具有確定性，意即相同的資料永遠會序列化為相同的 bytes。

> 「BCS 並非自我描述格式。因此，要反序列化一則訊息，必須事先知道該訊息的型別與版面配置」——引自 [README](https://github.com/zefchain/bcs)

核心規則如下：

- 整數以小端序（little-endian）位元組順序儲存；
- 序列（如 [vector](./../move-basics/vector)）會以其長度作為前綴，並以 ULEB128 編碼 — 一種緊湊、可變長度的整數編碼方式；
- [enum](./../move-basics/enum-and-match) 會以變體（variant）的索引儲存，後面接著該變體的欄位；
- map 會以有序的鍵值對序列儲存；
- struct 會被視為欄位的序列：各欄位依照在 struct 中定義的順序依序序列化，中間不含名稱、型別或分隔符。

以下具體展示 `User` 值是如何逐位元組排列的：

```move file=packages/samples/sources/programmability/bcs.move anchor=user_def

```

| 欄位               | 值      | 編碼後的 bytes                |
| ------------------ | ------- | ----------------------------- |
| `age: u8`          | `42`    | `2A`                          |
| `is_active: bool`  | `true`  | `01`                          |
| `name: String`     | `"Bob"` | `03 42 6F 62`（長度 + bytes） |
| `User`（以上全部） |         | `2A 01 03 42 6F 62`           |

## 使用 BCS (Using BCS) {#using-bcs}

Move 中有兩個模組實作了 BCS：[Standard Library](./../move-basics/standard-library) 提供 `std::bcs`，其中只有單一原生編碼函式 `to_bytes`；而 [Sui Framework](./sui-framework) 在此基礎上建立了 [`sui::bcs`][sui-bcs] 模組，該模組重新匯出了 `to_bytes`，並新增了以 Move 實作的解碼函式。在 Sui 程式碼中，只要匯入 `sui::bcs` 即可同時進行編碼與解碼。

## 編碼 (Encoding) {#encoding}

要編碼資料，可使用 `bcs::to_bytes` 函式，它會將資料參考轉換為 byte vector。此函式支援對任何型別進行編碼，包括 struct 與 enum。

```move
module std::bcs;

/// 回傳 `v` 以 BCS（Binary Canonical
/// Serialization）格式的二進位表示。
public native fun to_bytes<MoveValue>(v: &MoveValue): vector<u8>;
```

以下範例展示了基本型別的編碼：

```move file=packages/samples/sources/programmability/bcs.move anchor=encode

```

### 編碼 Struct (Encoding a Struct) {#encoding-a-struct}

struct 的編碼不過就是其欄位依序排列而已。以下範例編碼了 [格式 (Format)](#format) 小節中的 `User` 值，核對了表格中的確切 bytes，接著直接展示「欄位序列」規則 — 將各別編碼的欄位串接起來，會得到相同的結果：

```move file=packages/samples/sources/programmability/bcs.move anchor=encode_struct

```

## 解碼 (Decoding) {#decoding}

由於 BCS 並非自我描述格式，解碼需要事先知道資料型別。這不只是形式上的要求 — 同一組 bytes 在不同解讀方式下都完全有效，而解碼器無法偵測不匹配的情況。上面編碼後的 `User` 的 6 個 bytes，同樣可以被解讀為一個 `u16` 後面接一個 `vector<u8>`：

```move file=packages/samples/sources/programmability/bcs.move anchor=not_self_describing

```

[`sui::bcs`][sui-bcs] 模組提供了輔助解碼的函式：針對基本型別有 `peel_bool`、`peel_u8` 到 `peel_u256`，以及 `peel_address`；針對常見容器則有 `peel_vec_*` 系列與 `peel_option_*` 系列；其餘情況則有巨集可用。若解碼器的 bytes 用盡 — 或這些 bytes 無法構成有效的值，例如 boolean byte 不是 `0` 或 `1` — 該次呼叫就會中止（abort）。

### 包裝器 API (Wrapper API) {#wrapper-api}

解碼器是包裝這些 bytes 的一個包裝器：`bcs::new` 函式以傳值方式接收 bytes，接著呼叫端透過呼叫 `peel_*` 函式，由前到後逐一 _剝離_ 出各個值。尚未被解碼的部分會留在包裝器中，並可透過 `into_remainder_bytes` 函式取出。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode

```

在解碼過程中，有個常見做法是在單一 `let` 陳述式中使用多個變數。這讓程式碼稍微更易讀，也有助於避免不必要的資料複製。

```move file=packages/samples/sources/programmability/bcs.move anchor=chain_decode

```

### 解碼 Vector (Decoding Vectors) {#decoding-vectors}

雖然大多數基本型別都有專屬的解碼函式，但 vector 需要特殊處理，處理方式取決於元素的型別。其底層結構永遠相同：先解碼出 vector 的長度，接著在迴圈中逐一解碼每個元素。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_vector

```

在日常使用中，函式庫提供了 `peel_vec!` 巨集，它會在內部執行該迴圈，並針對每個元素呼叫一次給定的函式；此外也針對基本型別的 vector 提供了現成的 `peel_vec_*` 函式：

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_vector_macro

```

### 解碼 Option (Decoding Option) {#decoding-option}

[Option](./../move-basics/option) 是以單一 byte 編碼的 — `0` 代表 _none_，`1` 代表 _some_ — 後面接著該值（若存在的話）。`peel_option!` 巨集會讀取該 byte，只有在值存在時才會執行給定的函式；基本型別也有現成的 `peel_option_*` 函式可用。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_option

```

### 解碼 Struct (Decoding Structs) {#decoding-structs}

沒有辦法自動將 bytes 解碼為 Move 的 struct — [struct](../move-basics/struct) 只能由其所屬模組打包（pack），而這些 bytes 本身不帶有任何關於它們所代表內容的資訊。要將 bytes 解析為 struct，必須逐一剝離每個欄位，再打包成該型別。以下範例走完整趟流程：編碼一個 `User` 值、從 bytes 將其解碼回來，並確認結果與原始值完全相同。

```move file=packages/samples/sources/programmability/bcs.move anchor=round_trip

```

> 這些 bytes 不含任何欄位名稱或型別標籤，因此讓解碼正確的唯一關鍵，就是以與編碼時完全相同的順序、剝離出完全相同的型別。順序錯誤未必會導致中止（abort） — 它可能會悄悄產生錯誤的值，就如同[上面的範例](#decoding)所示。

### 解碼 Enum (Decoding Enums) {#decoding-enums}

[enum](./../move-basics/enum-and-match) 值的編碼方式是以其變體（variant）的索引，後面接著該變體的欄位。解碼的方式與此對應：`peel_enum_tag` 函式會讀取變體索引，接著針對該索引使用 `match` 運算式來解碼對應的欄位：

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_enum

```

## 總結 (Summary) {#summary}

- BCS 是 Move 的標準二進位序列化格式：具確定性 — 相同的值永遠會產生相同的 bytes。
- 此格式並非自我描述的：這些 bytes 不帶有名稱或型別，讀取端必須事先知道版面配置。
- struct 與 enum 是依照宣告順序將其欄位編碼；解碼時也必須以相同順序剝離相同的型別。
- 編碼使用 `bcs::to_bytes` 完成；解碼則使用 `bcs::new` 包裝器與 `peel_*` 系列的函式與巨集，遇到格式錯誤或截斷的輸入時會中止（abort）。

## 延伸閱讀 (Further Reading) {#further-reading}

- [BCS specification](https://github.com/zefchain/bcs) - 完整的格式說明。
- [std::bcs](https://docs.sui.io/references/framework/std/bcs) 與 [sui::bcs][sui-bcs] 模組
  文件。

[sui-bcs]: https://docs.sui.io/references/framework/sui/bcs
