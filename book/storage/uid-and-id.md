---
description: Sui Move 中的 UID 與 ID：唯一物件識別碼、其建立方式、用於動態欄位，以及如何保證其唯一性。
title: 使用者識別碼 (UID) 與識別碼 (ID)
keywords:
  - Move
  - Sui
  - Move tutorial
  - uid
questions:
  - What is UID and ID in Move?
  - How do I use UID and ID in Move?
  - What is Definition in Move?
  - What is Fresh UID Generation in Move?
answer: 'UID and ID in Sui Move: unique object identifiers, how they are created, used for dynamic fields, and guaranteed to be unique.'
goal:
  description: 'Reader understands uID and ID in Sui Move: unique object identifiers, how they are created, used for dynamic fields, and guaranteed to be unique'
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

# UID 與 ID (UID and ID) {#uid-and-id}

所有具有 [`key`](./key-ability) 能力的型別，都必須依照 Sui 驗證器的要求使用 `UID` 型別。以下將更深入探討 `UID` 及其用法。

## 定義 (Definition) {#definition}

`UID` 型別定義於 `sui::object` 模組中，是對 `ID` 的包裝；而 `ID` 又包裝了 `address` 型別。Sui 上的 UID 保證唯一，且物件刪除後無法重複使用。

```move
module sui::object;

/// UID 是物件的唯一識別碼。
public struct UID has store {
    id: ID
}

/// ID 是對地址的包裝；可自由複製。
public struct ID has copy, drop, store {
    bytes: address
}
```

請注意能力之間的差異：`ID` 是一般、可複製的資料，亦即能夠命名任何物件（甚至不存在的物件）的指標，且不需要任何特殊權限。`UID` 無法複製或丟棄：它是物件的身分識別，其建立與銷毀都是明確且受控的操作。

## 產生新的 UID (Fresh UID Generation) {#fresh-uid-generation}

新的 `UID` 會以 `object::new(ctx)` 函式建立：

- `UID` 是從交易摘要與該交易目前已建立的 ID 計數器所*衍生*；每建立一個新的 UID，計數器就會遞增。
- 計數器存在於交易情境中，因此產生 UID 時需要 [TxContext](./../programmability/transaction-context) 的可變參考。
- 新建立物件的 `id` 欄位必須是*全新*的 UID，也就是在同一筆交易中由 `object::new` 產生的 UID。Sui 驗證器會拒絕封裝使用另一個已解構物件所取得 UID 的物件，因此身分識別永遠無法重複使用，即使是擁有它的模組也一樣。

`UID` 是物件的表示方式，並啟用附加於物件身分識別的功能。其中一項關鍵功能是 [動態欄位](./../programmability/dynamic-fields)，因為 `UID` 明確存在才得以實現。另一項是在本章結尾介紹的[轉移至物件](./transfer-to-object)，它讓物件能接收傳送至其 ID 的其他物件。

## UID 生命週期 (UID Lifecycle) {#uid-lifecycle}

`UID` 透過 `object::new` 建立，並透過 `object::delete` 函式刪除。`delete` 函式會以*值*的方式消耗 UID，因此只能在物件被[解構](./../move-basics/struct#unpacking-a-struct)後呼叫；而這項操作只有定義該物件的模組能執行：

```move file=packages/samples/sources/storage/uid-and-id.move anchor=lifecycle

```

### 保留 UID (Keeping the UID) {#keeping-the-uid}

物件解構後，不必立即刪除 `UID`。它可能帶有[動態欄位](./../programmability/dynamic-fields)，或持有透過[轉移至物件](./transfer-to-object)傳送給它的物件；刪除 UID 會使這些內容無法存取。對於這類情況，可以保留 UID：將它作為另一個結構中的一般 `UID` 欄位（不是 `id`！）儲存，直到處理完相關資料並能安全刪除 UID 為止。

> 物件消失後仍可保留 UID 的能力，實現了一種稱為*刪除證明*的特殊技巧：回傳的 UID 是物件已銷毀的證據，應用程式可將其兌換為獎勵，或用來略過套用於存活物件的限制。

## UID 衍生 (UID Derivation) {#uid-derivation}

Sui 可使用*衍生金鑰*從其他 UID 衍生 UID。此功能實作於 [`sui::derived_object`][derived-object] 模組中，能產生可預測且具決定性的 ID，方便鏈下探索。每個父物件與金鑰配對的 UID 只能宣告一次：

```move file=packages/samples/sources/storage/uid-and-id.move anchor=derived

```

衍生地址可減輕鏈下索引器的負擔：只要知道父物件的 ID，就能透過衍生函式計算衍生物件的 ID；多數 SDK 與 Move 本身都提供此函式：

```move
module sui::derived_object;

/// 檢查 UID 是否以 `key` 在 `parent` 處衍生。
public fun exists<K: copy + drop + store>(parent: &UID, key: K): bool;

/// 衍生 UID 內部的 `address`，無論其是否已被宣告。
public fun derive_address<K: copy + drop + store>(parent: ID, key: K): address;
```

相同的衍生機制也在內部用於產生[動態欄位](./../programmability/dynamic-fields)的 ID。

## ID 型別 (ID) {#id}

談到 `UID` 時，也應提及 `ID` 型別。它是可自由複製的 `address` 包裝，用來*指向*物件。通常 `ID` 會參考某個物件，但沒有任何限制或保證要求該 ID 必須指向現有物件。

> ID 可以作為交易引數，在[交易區塊](./../concepts/what-is-a-transaction)中接收。或者，也可以使用 `to_id()` 函式從 `address` 值建立 ID。

```move file=packages/samples/sources/storage/uid-and-id.move anchor=conversions

```

## 全新物件地址 (Fresh Object Address) {#fresh-object-address}

[`TxContext`](./../programmability/transaction-context) 提供 `fresh_object_address` 函式，該函式使用與 `object::new` 相同的衍生方式產生唯一地址，但不會建立 `UID`。這對需要為鏈下實體提供唯一識別碼的應用程式很有用，例如市集中的 `order_id`。

## 總結 (Summary) {#summary}

- `UID` 是物件不可複製、不可丟棄的身分識別；`ID` 則是可自由複製的指標。
- 全新的 UID 由 `object::new(ctx)` 產生，且永遠無法重複用於新的物件。
- UID 會在解構後透過 `object::delete` 刪除；若仍附加資料，則可保留。
- 衍生 UID（`sui::derived_object`）讓物件 ID 在鏈下可預測且容易探索。

## 延伸閱讀 (Further Reading) {#further-reading}

- [`sui::object`][object] 模組文件。
- [`sui::derived_object`][derived-object] 模組文件。
- Sui 文件中的 [衍生物件](https://docs.sui.io/guides/developer/objects/derived-objects)。

[object]: https://docs.sui.io/references/framework/sui/object
[derived-object]: https://docs.sui.io/references/framework/sui/derived_object
