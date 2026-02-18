---

description: "UID and ID in Sui Move: unique object identifiers, how they are created, used for dynamic fields, and guaranteed to be unique."
---

# UID 與 ID (UID and ID)

Sui 校驗器要求在所有具有 [`key`](./key-ability.md) 能力的類型上使用 `UID` 類型。在這裡，我們將深入探討 `UID` 及其用法。

## 定義

`UID` 類型定義在 `sui::object` 模組中，它是 `ID` 的封裝器，而 `ID` 則進一步封裝了 `address` 類型。Sui 上的 UID 保證是唯一的，並且在物件被刪除後不能重複使用。

```move
module sui::object;

/// UID 是物件的唯一識別碼
public struct UID has store {
    id: ID
}

/// ID 是地址的封裝器
public struct ID has store, drop {
    bytes: address
}
```

## 新 UID 的產生 (Fresh UID Generation)

- `UID` 是從 `tx_hash` 和為每個新 UID 遞增的 `index` 中「衍生 (derived)」出來的。
- `derive_id` 函式在 `sui::tx_context` 模組中實作，這就是為什麼產生 `UID` 需要 [交易上下文 (TxContext)](./../programmability/transaction-context.md)。
- Sui 校驗器不允許使用不是在同一個函式中建立的 UID。這防止了 UID 被預先產生或在物件拆包後重複使用。

使用 `object::new` 函式建立新的 UID。它接收一個對 `TxContext` 的可變參考，並傳回一個新的 `UID`。

```move
public fun uid(ctx: &mut TxContext) {
  let id = object::new(ctx); // 從 TxContext 建立一個新的 UID。
  id.delete(); // 刪除此 UID。
}
```

`UID` 充當物件的代表，並允許定義物件的行為和功能。其中一個關鍵功能 —— [動態欄位 (Dynamic Fields)](./../programmability/dynamic-fields) —— 之所以可行，是因為 `UID` 類型是顯式的。此外，它允許接收發送到其他物件的物件。此功能稱為 [轉移至物件 (Transfer to Object, TTO)](./transfer-to-object.md)，我們稍後將在本章中解釋。

## UID 衍生 (UID Derivation) {#uid-derivation}

Sui 允許使用「衍生金鑰 (derivation keys)」從其他 UID 衍生出 UID。此功能在 [`sui::derived_object`][derived-object] 模組中實作，允許產生可預測且確定性的 `UIDs`，以便於鏈下發現。每一對「父項 (parent) + 金鑰 (key)」的 UID 只能產生一次！

```move
use sui::derived_object;

/// 某個核心應用程式物件。
public struct Base has key { id: UID }

/// 衍生物件。
public struct Derived has key { id: UID }

/// 使用 `address` 作為 `key` 建立並共享一個新的 `Derived` 物件。
public fun derive(base: &mut Base, key: address) {
    let id = derived_object::claim(&mut base.id, key);
    transfer::share_object(Derived { id })
}
```

衍生地址降低了鏈下索引器 (indexers) 的負載，因為只需存儲父物件的 ID，並使用衍生函式即可獲取衍生 ID。ID 衍生函式是大多數 SDK 的一部分，也存在於 Move 中：

```move
module sui::derived_object;

/// 檢查 UID 是否是使用 `key` 在 `parent` 處衍生出來的。
public fun exists<K: copy + drop + store>(parent: &UID, key: K): bool;

/// 不管是否已建立，衍生 UID 的內部 `address`。
public fun derive_address<K: copy + drop + store>(parent: ID, key: K): address;
```

同樣的衍生功能也被用於為 [動態欄位 (dynamic fields)](./../programmability/dynamic-fields.md) 產生 UID。

## UID 的生命週期

`UID` 類型使用 `object::new` 函式建立，並使用 `object::delete` 函式刪除。`object::delete` 「按值 (by value)」消耗 UID，因此只有在物件 [被拆包 (unpacked)](./../move-basics/struct.md#unpacking-a-struct) 之後才能刪除物件的 UID。

```move
public struct Character has key { id: UID }

public fun character(ctx: &mut TxContext) {
    // 實例化 `Character` 物件。
    let char = Character { id: object::new(ctx) };

    // 拆包物件以獲取其 UID。
    let Character { id } = char;

    // 刪除此 UID。
    id.delete();
}
```

## 保留 UID

UID 在物件結構被拆包後不需要立即刪除。有時它可能帶有 [動態欄位](./../programmability/dynamic-fields) 或透過 [轉移至物件](./transfer-to-object.md) 轉移給它的物件。在這種情況下，UID 可能會保留並存儲在另一個物件中。

## 刪除證明 (Proof of Deletion)

返回物件 UID 的能力可以用於一種稱為「刪除證明 (proof of deletion)」的模式。這是一種很少使用的技術，但在某些情況下可能很有用，例如，創作者或應用程式可以透過將已刪除的 ID 更換為某些獎勵來激勵物件的刪除。

在框架開發中，此方法可以用於忽略/繞過對「獲取 (taking)」物件的某些限制。如果有一個像 Kiosk 那樣對轉移強制執行某些邏輯的容器，則可能存在透過提供刪除證明來跳過檢查的特殊場景。

這是目前仍在探索和研究的開放主題之一，可以以多種方式使用。

## ID

在討論 `UID` 時，我們也應該提到 `ID` 類型。它是對 `address` 類型的封裝，用於代表一個地址指標。通常，`ID` 用於指向一個物件，然而，這沒有任何限制，也不保證 `ID` 指向一個現有的物件。

> ID 可以作為 [交易區塊 (Transaction Block)](./../concepts/what-is-a-transaction) 中的交易參數接收。或者，可以使用 `to_id()` 函式從 `address` 數值建立 ID。

```move
public fun conversion_methods(ctx: &mut TxContext) {
    let uid: UID = object::new(ctx);
    let id: ID = uid.to_inner();

    let addr_from_uid: address = uid.to_address();
    let addr_from_id: address = id.to_address();

    uid.delete();
}
```

此範例展示了不同的轉換方法：`UID.to_inner` 建立了底層 `ID` 的副本，而 `UID.to_address` 返回內部地址。另一個非常有用的方法 `ID.to_address` 會從 `ID` 類型中複製內部數值。

## 新物件地址 (Fresh Object Address)

[`TxContext`](./../programmability/transaction-context.md) 提供了 `fresh_object_address` 函式，可用於建立唯一的地址和 `ID` —— 這在某些為使用者動作分配唯一識別碼（例如：市場中的 order_id）的應用程式中非常有用。

## 相關連結

- [`sui::object`][object] 模組文件
- [`sui::derived_object`][derived-object] 模組文件
- Sui 文件中的 [衍生物件 (Derived Objects)](https://docs.sui.io/concepts/sui-move-concepts/derived-objects)

[object]: https://docs.sui.io/references/framework/sui_sui/object
[derived-object]: https://docs.sui.io/references/framework/sui_sui/derived_object
