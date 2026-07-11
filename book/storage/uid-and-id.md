---
description: Sui Move 中的 UID 與 ID (UID and ID in Sui Move)：唯一物件識別符 (unique object
  identifiers) 的建立方式、如何用於動態欄位 (dynamic fields)，以及唯一性的保證。
---

# UID 與 ID (UID and ID) {#uid-and-id}

在所有具備 [`key`](./key-ability) 能力的型別上，Sui Verifier 都要求使用 `UID` 型別。這裡我們深入探討 `UID` 及其用法。

## 定義 (Definition) {#definition}

`UID` 型別定義於 `sui::object` 模組中，是對 `ID` 的一層包裝，而 `ID` 本身則是對 `address` 型別的包裝。Sui 上的 UID 保證是唯一的，且物件被刪除後不能再被重複使用。

```move
module sui::object;

/// UID 是一個物件的唯一識別碼。
public struct UID has store {
    id: ID
}

/// ID 是對 address 的包裝；可自由複製。
public struct ID has copy, drop, store {
    bytes: address
}
```

注意兩者能力上的差異：`ID` 是單純、可複製的資料——一個能指向任何物件（甚至是不存在的物件）的指標，不需要任何特殊權限。而 `UID` 既不能複製也不能捨棄：它是物件的身分識別，其建立與銷毀都必須是明確、受控的操作。

## 產生全新的 UID (Fresh UID Generation) {#fresh-uid-generation}

使用 `object::new(ctx)` 函式可以建立一個新的 `UID`：

- `UID` 是從交易摘要（transaction digest）以及該交易中目前為止已建立的 ID 計數器*衍生*而來，每建立一個新的 UID 該計數器就會遞增。
- 這個計數器存在於交易上下文中，這也是為什麼 UID 的產生需要 [TxContext](./../programmability/transaction-context) 的可變參考。
- 一個新建立物件的 `id` 欄位必須是*全新*的 UID——也就是在同一筆交易中由 `object::new` 產生的 UID。Sui Verifier 會拒絕使用來自另一個已拆解物件的 UID 來封裝物件——因此一個身分識別絕不能被重複使用，即使是擁有該身分識別的模組本身也不行。

`UID` 作為物件的表徵，使得依附於物件身分識別的功能得以實現。其中最關鍵的功能之一——[動態欄位](./../programmability/dynamic-fields)——之所以可行，正是因為 `UID` 是明確存在的。另一個功能——[轉移至物件](./transfer-to-object)（於本章末介紹）——則允許一個物件接收送往其 ID 的其他物件。

## UID 的生命週期 (UID Lifecycle) {#uid-lifecycle}

`UID` 透過 `object::new` 建立，並透過 `object::delete` 函式刪除。`delete` 函式*依值*消耗 UID，因此只能在物件被[拆解](./../move-basics/struct#unpacking-a-struct)之後呼叫——而只有定義該物件的模組才能執行拆解：

```move file=packages/samples/sources/storage/uid-and-id.move anchor=lifecycle

```

### 保留 UID (Keeping the UID) {#keeping-the-uid}

物件被拆解後，`UID` 不一定要立即刪除。它可能承載著[動態欄位](./../programmability/dynamic-fields)，或持有透過[轉移至物件](./transfer-to-object)方式送達的物件——若此時刪除 UID，將使這些內容無法再被存取。針對這類情況，可以保留該 UID：將其以一般 `UID` 欄位（而非 `id`！）的形式，儲存在另一個結構體中，直到相關資料處理完畢，UID 才能被安全地刪除。

> 在物件消失後仍保留其 UID 的能力，可實現一種小眾技巧，稱為*刪除證明*（proof of deletion）：回傳的 UID 即為該物件已被銷毀的證據，應用程式可用它來兌換獎勵，或繞過原本作用於該存活物件上的限制。

## UID 衍生 (UID Derivation) {#uid-derivation}

Sui 允許使用*衍生金鑰*（derivation keys）從既有的 UID 衍生出新的 UID。此功能實作於 [`sui::derived_object`][derived-object] 模組中，能產生可預測、確定性的 ID，方便鏈下探索。每一組 parent + key 組合所對應的 UID，只能被領取一次：

```move file=packages/samples/sources/storage/uid-and-id.move anchor=derived

```

衍生位址能降低鏈下索引器的負擔：只要知道父物件的 ID，衍生物件的 ID 就可以透過衍生函式計算得出——這類函式存在於大多數 SDK 中，Move 本身也有提供：

```move
module sui::derived_object;

/// 檢查某個 UID 是否是用 `key` 在 `parent` 下衍生出來的。
public fun exists<K: copy + drop + store>(parent: &UID, key: K): bool;

/// 衍生出 UID 內部的 `address`，無論它是否已被 claim。
public fun derive_address<K: copy + drop + store>(parent: ID, key: K): address;
```

相同的衍生機制也在內部被用來為[動態欄位](./../programmability/dynamic-fields)產生 ID。

## ID {#id}

談到 `UID` 時，也應該一併提及 `ID` 型別。它是對 `address` 的一層可自由複製包裝，用來*指向*某個物件。通常 `ID` 會指向某個實際存在的物件，但這並非強制限制——也沒有任何保證該 ID 一定指向一個存在的物件。

> ID 可以作為交易參數，在[交易區塊](./../concepts/what-is-a-transaction)中被接收。另外，也可以使用 `to_id()` 函式，從 `address` 值建立出一個 ID。

```move file=packages/samples/sources/storage/uid-and-id.move anchor=conversions

```

## 全新物件位址 (Fresh Object Address) {#fresh-object-address}

[`TxContext`](./../programmability/transaction-context) 提供了 `fresh_object_address` 函式，該函式使用與 `object::new` 相同的衍生方式產生一個唯一位址——但不會建立 `UID`。這對於需要為鏈下實體提供唯一識別碼的應用程式相當有用——例如市場應用中的 `order_id`。

## 總結 (Summary) {#summary}

- `UID` 是物件不可複製、不可捨棄的身分識別；`ID` 則是可自由複製的指標。
- 全新的 UID 來自 `object::new(ctx)`，且絕不能被重複用於新物件。
- UID 在拆解物件後會透過 `object::delete` 刪除——若仍有資料依附其上，則可以保留。
- 衍生 UID（`sui::derived_object`）讓物件 ID 具備可預測性，並可在鏈下被探索。

## 延伸閱讀 (Further Reading) {#further-reading}

- [`sui::object`][object] 模組文件。
- [`sui::derived_object`][derived-object] 模組文件。
- Sui 官方文件中的[衍生物件](https://docs.sui.io/guides/developer/objects/derived-objects)。

[object]: https://docs.sui.io/references/framework/sui/object
[derived-object]: https://docs.sui.io/references/framework/sui/derived_object
