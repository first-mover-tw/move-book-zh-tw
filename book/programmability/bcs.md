---

description: "BCS (Binary Canonical Serialization) in Move: encode and decode structured data for on-chain storage and cross-platform communication."
---

# 二進位規範序列化 (Binary Canonical Serialization, BCS)

二進位規範序列化 (BCS) 是一種用於結構化資料的二進位編碼格式。它最初是為 Diem 設計的，後來成為 Move 的標準序列化格式。BCS 簡單、高效、具有確定性，且易於在任何程式語言中實作。

> 完整的格式規範可在 [BCS 儲存庫](https://github.com/zefchain/bcs) 中找到。

## 格式

BCS 是一種支援高達 256 位元的無符號整數、選項 (options)、布林值、單元 (unit，空值)、固定和可變長度序列以及映射 (maps) 的二進位格式。該格式旨在具有確定性，這意味著相同的資料將始終被序列化為相同的位元組。

> 「BCS 不是一種自帶描述 (self-describing) 的格式。因此，為了反序列化訊息，必須提前知道訊息類型和佈局。」 —— 摘自 [README](https://github.com/zefchain/bcs) 

整數以小端 (little-endian) 格式存儲，可變長度整數使用可變長度編碼方案進行編碼。序列會以 ULEB128 編碼的長度作為前綴，列舉 (enumerations) 存儲為變體的索引後接資料，而映射則存儲為鍵值對的有序序列。

結構 (Structs) 被視為欄位序列，欄位按其在結構中定義的順序進行序列化。欄位使用與頂層資料相同的規則進行序列化。

## 使用 BCS

[Sui 框架](./sui-framework) 包含用於編碼和解碼資料的 [`sui::bcs`][sui-bcs] 模組。編碼函式在 VM 中原生實作，解碼函式則是在 Move 中實作。

## 編碼 (Encoding)

若要編碼資料，請使用 `bcs::to_bytes` 函式，它將資料參考轉換為位元組向量。此函式支援編碼任何類型，包括結構。

```move
module std::bcs;

public native fun to_bytes<T>(t: &T): vector<u8>;
```

以下範例展示了如何使用 BCS 編碼結構。`to_bytes` 函式可以接收任何數值並將其編碼為位元組向量。

```move file=packages/samples/sources/programmability/bcs.move anchor=encode

```

### 編碼結構

結構的編碼方式與簡單類型相似。以下是如何使用 BCS 編碼結構：

```move file=packages/samples/sources/programmability/bcs.move anchor=encode_struct

```

## 解碼 (Decoding)

由於 BCS 不是自帶描述的格式，解碼需要預先知道資料類型。[`sui::bcs`][sui-bcs] 模組提供了多種函式來協助此過程。

### 封裝 API (Wrapper API)

BCS 在 Move 中是以封裝器 (wrapper) 的形式實作的。解碼器按值接收位元組，然後允許呼叫者透過呼叫以 `peel_*` 為前綴的不同解碼函式來「剝離 (peel off)」資料。資料從位元組中提取，剩餘的位元組保留在封裝器中，直到呼叫 `into_remainder_bytes` 函式。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode

```

一種常見的實作是在解碼過程中的單個 `let` 語句中使用多個變數。這使得程式碼更具可讀性，並有助於避免不必要的資料複製。

```move file=packages/samples/sources/programmability/bcs.move anchor=chain_decode

```

### 解碼向量 (Decoding Vectors)

雖然大多數原始類型都有專用的解碼函式，但向量需要特殊處理，這取決於元素的類型。對於向量，首先需要解碼向量的長度，然後在迴圈中解碼每個元素。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_vector

```

此功能由函式庫提供，表現為巨集 `peel_vec!`。它根據向量長度重複呼叫內部表達式，並將結果匯總到單個向量中。

```move
let u64_vec = bcs.peel_vec!(|bcs| bcs.peel_u64());
let address_vec = bcs.peel_vec!(|bcs| bcs.peel_address());

// 注意：僅當 `MyStruct` 定義在目前模組中時才可行！
let my_struct = bcs.peel_vec!(|bcs| MyStruct {
    user_addr: bcs.peel_address(),
    age: bcs.peel_u8(),
});
```

### 解碼選項 (Decoding Option)

Move 中的 [Option](./../move-basics/option) 被表示為具有 0 或 1 個元素的向量。要讀取選項，您可以像處理向量一樣處理它，並檢查其長度（第一個位元組 —— 不是 1 就是 0）。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_option

```

與 [向量](#decoding-vectors) 類似，這裡也有一個封裝巨集 `peel_option!`，它會檢查變體索引，並在底層數值為 _some_ 時評估表達式。

```move
let u8_opt = bcs.peel_option!(|bcs| bcs.peel_u8());
let bool_opt = bcs.peel_option!(|bcs| bcs.peel_bool());
```

### 解碼結構

結構是逐個欄位解碼的，目前沒有自動將位元組解碼為 Move 結構的方法。要將位元組解析為結構，您需要解碼每個欄位並實例化該類型。

```move file=packages/samples/sources/programmability/bcs.move anchor=decode_struct

```

## 總結

二進位規範序列化是一種高效的結構化資料二進位格式，確保了跨平台的一致序列化。Sui 框架提供了全面的工具來處理 BCS，透過內建函式實作廣泛的功能。

[sui-bcs]: https://docs.sui.io/references/framework/sui_sui/bcs
