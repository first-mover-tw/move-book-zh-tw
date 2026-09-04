---
description: Move 中的 BCS (Binary Canonical Serialization)：為鏈上儲存與跨平台通訊編碼及解碼結構化資料。
title: 二進位標準序列化 (Binary Canonical Serialization)
keywords:
  - Move
  - Sui
  - Move tutorial
  - binary
  - canonical
  - serialization
  - BCS
questions:
  - What is Binary Canonical Serialization in Move?
  - How do I use Binary Canonical Serialization in Move?
  - What is Format in Move?
  - What is Using BCS in Move?
answer: 'BCS (Binary Canonical Serialization) in Move: encode and decode structured data for onchain storage and cross-platform communication.'
goal:
  description: 'Reader understands bCS (Binary Canonical Serialization) in Move: encode and decode structured data for onchain storage and cross-platform communication'
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

# 二進位標準序列化 (Binary Canonical Serialization) {#binary-canonical-serialization}

二進位標準序列化（BCS）是一種用於結構化資料的二進位編碼格式。它最初於 Diem
設計，後來成為 Move 的標準序列化格式。BCS 簡單、高效、具決定性，且易於以任何程式語言實作。

雖然序列化聽起來可能是進階主題，但 BCS 在 Sui 中無所不在：交易的引數會以 BCS 編碼、物件和事件會以 BCS 位元組形式
儲存，並可在鏈下讀取；而在智慧合約中簽署及驗證的訊息通常是經 BCS 序列化的結構。大多數時候編碼會由系統代為處理，
但應用程式遲早需要手動進行：解碼已簽署的承載資料、剖析作為 `vector<u8>` 引數傳入的原始位元組，或產生與鏈下用戶端
建立結果相符的位元組。

> 完整的格式規格可在
> [BCS repository](https://github.com/zefchain/bcs) 取得。

## 格式 (Format) {#format}

BCS 是一種二進位格式，支援最大 256 位元的無號整數、選項、布林值、單位
（空值）、固定與可變長度序列，以及映射。此格式設計為具決定性，表示相同資料
將一律序列化為相同位元組。

> 「BCS 並非自我描述格式。因此，若要反序列化訊息，必須預先知道
> 訊息的型別及配置。」摘自 [README](https://github.com/zefchain/bcs)

核心規則如下：

- 整數以小端序位元組順序儲存；
- 序列（例如[向量](./../move-basics/vector)）會加上長度前綴，其使用
  ULEB128 編碼——一種精簡的可變長度整數編碼；
- [列舉](./../move-basics/enum-and-match)會儲存為變體的索引，後接該變體的
  欄位；
- 映射會儲存為依序排列的鍵值配對序列；
- 結構會被視為欄位序列：欄位會依其在結構中的定義順序逐一序列化，中間不含名稱、
  型別或分隔符號。

為使此概念更具體，以下是 `User` 值逐位元組的配置方式：

```move file=packages/samples/sources/programmability/bcs.move anchor=user_def

```

| 欄位               | 值      | 編碼位元組                     |
| ------------------ | ------- | ------------------------------ |
| `age: u8`          | `42`    | `2A`                           |
| `is_active: bool`  | `true`  | `01`                           |
| `name: String`     | `"Bob"` | `03 42 6F 62`（長度 + 位元組） |
| `User`（以上全部） |         | `2A 01 03 42 6F 62`            |

## 使用 BCS (Using BCS) {#using-bcs}

有兩個模組在 Move 中實作 BCS：[標準函式庫](./../move-basics/standard-library)
提供含有單一原生編碼函式 `to_bytes` 的 `std::bcs`，而
[Sui 框架](./sui-framework)則以此為基礎建立 [`sui::bcs`][sui-bcs] 模組，
其重新匯出 `to_bytes`，並新增以 Move 實作的解碼函式。在 Sui 原始碼中，只要匯入
`sui::bcs` 即可同時進行編碼與解碼。

## 編碼 (Encoding) {#encoding}

若要編碼資料，請使用 `bcs::to_bytes` 函式；此函式會將資料參考轉換為位元組
向量。此函式支援編碼任何型別，包括結構與列舉。

```move
module std::bcs;

/// 以 BCS（二進位標準
/// 序列化）格式回傳 `v` 的二進位表示。
public native fun to_bytes<MoveValue>(v: &MoveValue): vector<u8>;
```

以下範例顯示基本值的編碼：

```move file=packages/samples/sources/programmability/bcs.move anchor=encode

```

### 結構編碼 (Encoding a Struct) {#encoding-a-struct}

結構的編碼僅由其欄位逐一組成。以下範例會編碼[格式](#format)章節中的 `User`
值、檢查表格中的確切位元組，接著直接示範「欄位序列」規則——串接各自編碼的
欄位會得到相同結果：

```move file=packages/samples/sources/programmability/bcs.move anchor=encode_struct

```

## 解碼 (Decoding) {#decoding}

由於 BCS 並非自我描述格式，解碼時必須預先知道資料型別。這不只是形式上的要求——
相同位元組在不同解讀下都可能完全有效，且解碼器無法偵測不相符的情況。上述已編碼
`User` 的 6 個位元組同樣可以讀取為一個 `u16`，後接一個 `vector<u8>`：

```move file=packages/samples/sources/programmability/bcs.move anchor=not_self_describing

```

[`sui::bcs`][sui-bcs] 模組提供輔助解碼的函式：基本值可使用 `peel_bool`、
`peel_u8` 至 `peel_u256` 及 `peel_address`，常見容器可使用 `peel_vec_*` 函式家族
與 `peel_option_*` 函式家族，其他所有情況則使用巨集。若解碼器用盡位元組——或位元組
未構成有效值，例如布林位元組不是 `0` 或 `1`——呼叫就會中止。

### 包裝器 API (Wrapper API) {#wrapper-api}

解碼器是位元組的包裝器：`bcs::new` 函式會依值接收位元組，然後呼叫端透過呼叫
`peel_*` 函式，從前至後逐一*剝離*值。尚未解碼的內容會保留在包裝器內，並可透過
`into_remainder_bytes` 函式再次取出。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode

```

解碼期間常見的做法是在單一 `let` 陳述式中使用多個變數。這能讓原始碼更易讀，
並有助於避免不必要的資料複製。

```move file=packages/samples/sources/programmability/bcs.move anchor=chain_decode

```

### 向量解碼 (Decoding Vectors) {#decoding-vectors}

雖然大多數基本型別都有專用的解碼函式，向量需要特殊處理，且取決於元素的型別。
其底層結構始終相同：先解碼向量長度，再於迴圈中解碼每個元素。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_vector

```

對於日常使用，函式庫提供 `peel_vec!` 巨集，它會在內部執行迴圈，並針對每個元素呼叫
給定函式一次；此外，也為基本型別的向量提供現成的 `peel_vec_*` 函式：

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_vector_macro

```

### 選項解碼 (Decoding Option) {#decoding-option}

[Option](./../move-basics/option) 會編碼為單一位元組——`0` 表示 _none_、`1` 表示
_some_——若存在值，後面會接續該值。`peel_option!` 巨集會讀取此位元組，且只有在值存在時
才評估給定函式；基本型別也有現成的 `peel_option_*` 函式。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_option

```

### 結構解碼 (Decoding Structs) {#decoding-structs}

沒有方法可以自動將位元組解碼為 Move 結構——[結構](../move-basics/struct)
只能由其模組封裝，而且位元組不帶有其所代表內容的資訊。若要將位元組剖析為結構，
請剝離每個欄位並封裝該型別。以下範例完成完整往返：它編碼一個 `User` 值，從位元組
解碼回來，並檢查結果與原始值完全相同。

```move file=packages/samples/sources/programmability/bcs.move anchor=round_trip

```

> 位元組不含欄位名稱或型別標籤，因此能使解碼正確的唯一條件，就是以完全相同的順序
> 剝離與編碼時完全相同的型別。順序錯誤不一定會中止——它可能會悄悄產生錯誤值，如
> [上述範例](#decoding)所示。

### 列舉解碼 (Decoding Enums) {#decoding-enums}

[列舉](./../move-basics/enum-and-match)值會編碼為其變體的索引，後接該變體的
欄位。解碼與此對應：`peel_enum_tag` 函式會讀取變體索引，而針對它的 `match` 運算式
則會解碼對應欄位：

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_enum

```

## 總結 (Summary) {#summary}

- BCS 是 Move 的標準二進位序列化格式：具決定性——相同值一律產生相同位元組。
- 此格式並非自我描述：位元組不帶有名稱或型別，讀取端必須預先知道配置。
- 結構與列舉會依宣告順序將其欄位編碼；解碼時必須以相同順序剝離相同型別。
- 編碼使用 `bcs::to_bytes`；解碼使用 `bcs::new` 包裝器，以及 `peel_*` 函式與巨集
  家族；它們會在輸入格式不正確或遭截斷時中止。

## 延伸閱讀 (Further Reading) {#further-reading}

- [BCS specification](https://github.com/zefchain/bcs) - 完整格式說明。
- [std::bcs](https://docs.sui.io/references/framework/std/bcs) 與 [sui::bcs][sui-bcs] 模組
  文件。

[sui-bcs]: https://docs.sui.io/references/framework/sui/bcs
