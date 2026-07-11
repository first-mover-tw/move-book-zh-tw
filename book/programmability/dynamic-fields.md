---
description: 'Dynamic fields in Sui: attach heterogeneous key-value data to objects at runtime, bypassing object size limits.'
---

# 動態欄位 (Dynamic Fields)

物件 [欄位](./../move-basics/struct.md#struct) 被定義在 Move 結構中，且一旦發表模組後就是固定的。雖然這提供了一種非常強大且靜態的方法來定義物件的佈局，但有時應用程式需要更多的靈活性，這就是動態欄位的用武之地。動態欄位是可以在執行期間動態添加、移除和存取的物件欄位。這使得開發者可以建立更複雜且可擴展的應用程式邏輯。

## 定義

動態欄位定義在 [Sui 框架](./sui-framework) 的 `sui::dynamic_field` 模組中。它們透過一個「名稱 (name)」附加到物件的 `UID`，並可以使用該名稱存取。一個物件上只能附加一個具有給定名稱的欄位。

```move
module sui::dynamic_field;

/// 用於存儲欄位和數值的內部物件
public struct Field<Name: copy + drop + store, Value: store> has key {
    /// 由物件 ID、欄位名稱值及其類型的雜湊決定，
    /// 即 hash(parent.id || name || Name)
    id: UID,
    /// 此欄位的名稱數值
    name: Name,
    /// 綁定到此欄位的數值
    value: Value,
}
```

如定義所示，動態欄位存儲在內部的 `Field` 物件中，其 `UID` 是基於物件 ID、欄位名稱和欄位類型以確定性的方式產生的。`Field` 物件包含欄位名稱和與其綁定的數值。`Name` 和 `Value` 類型參數的約束定義了鍵和值必須具備的能力。

## 用法

動態欄位可用的方法非常簡單：可以使用 `add` 添加欄位，使用 `remove` 移除欄位，並使用 `borrow` 和 `borrow_mut` 讀取。此外，可以使用 `exists_` 方法檢查欄位是否存在（對於需要類型匹配的嚴格檢查，還有 `exists_with_type` 方法）。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=usage

```

在上述範例中，我們定義了一個 `Character` 物件和兩種類型的配件，它們永遠無法放在同一個向量 (vector) 中。然而，動態欄位允許我們將它們一起存儲在單個物件中。這兩個物件都透過 `vector<u8>`（位元組字串字面量）名稱附加到 `Character`，並可以使用它們各自的名稱存取。

如您所見，當我們將配件附加到 Character 時，我們是「按值 (by value)」傳遞它們的。換句話說，兩個數值都被移動到了新的作用域，且其所有權被轉移到了 `Character` 物件。如果我們更改了 `Character` 物件的所有權，配件也會隨之移動。

我們應該強調的最後一個關於動態欄位的重要屬性是：它們是「透過其父項存取 (accessed through their parent)」的。這意味著 `Hat` 和 `Mustache` 物件無法直接存取，必須遵循與父物件相同的規則。

## 使用外部類型作為動態欄位

動態欄位允許物件攜帶任何類型的資料，包括在其他模組中定義的類型。這歸功於它們的泛型性質以及對類型參數相對寬鬆的約束。讓我們透過將幾個不同的數值附加到 `Character` 物件來說明這一點。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=foreign_types

```

在此範例中，我們展示了不同的類型如何被用作動態欄位的「名稱 (name)」和「數值 (value)」。字串 `String` 透過 `vector<u8>` 名稱附加，`u64` 透過 `u32` 名稱附加，而 `bool` 則透過 `bool` 名稱附加。使用動態欄位，一切皆有可能！

## 孤立動態欄位 (Orphaned Dynamic Fields)

> 為了防止產生孤立動態欄位，請使用 [動態集合類型](./dynamic-collections)（例如 `Bag`），因為它們會追蹤動態欄位，且在還有附加欄位的情況下不充許拆包。

用於刪除 UID 的 `object::delete()` 函式不會追蹤動態欄位，因此無法防止動態欄位變得孤立。一旦父項 UID 被刪除，動態欄位不會自動刪除，它們會變得孤立。這意味著動態欄位仍然存儲在區塊鏈中，但再也無法被存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=orphan_fields

```

孤立物件不適用於存儲退還 (storage rebate)，且存儲費用將無法收回。在拆包物件時避免孤立動態欄位的一種方法是傳回 `UID` 並將其暫時存儲在某處，直到動態欄位被正確移除和處理。

## 使用自定義類型作為欄位名稱

在前面的範例中，我們使用原始類型作為欄位名稱，因為它們具備所需的能力集。但當我們使用自定義類型作為欄位名稱時，動態欄位會變得更加有趣。這允許以更結構化的方式存儲資料，同時也允許保護欄位名稱不被其他模組存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type

```

我們上面定義的兩個欄位名稱是 `AccessoryKey` 和 `MetadataKey`。`AccessoryKey` 內部有一個 `String` 欄位，因此它可以使用不同的 `name` 數值被多次使用。`MetadataKey` 是一個空金鑰，只能附加一次。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type_usage

```

如您所見，自定義類型確實可以作為欄位名稱，但前提是它們可以被該模組「構造 (constructed)」—— 換句話說，如果它們對於該模組來說是「內部的 (internal)」且定義在其中。這種對結構封裝的限制可以在應用程式設計中開闢新的思路。

這種方法被用在物件能力 (Object Capability)<!--[]](./object-capability)--> 模式中，應用程式可以授權外部物件在其內部執行操作，同時不將該能力公開給其他模組。

## 暴露 UID (Exposing UID)

<div class="warning">

對 `UID` 的可變存取是一項安全風險。將您類型的 `UID` 作為可變參考暴露出來，可能會導致物件動態欄位被意外修改或移除。此外，這也會影響「轉移至物件」<!--[](./../storage/transfer-to-object)--> 以及 [動態物件欄位](./dynamic-object-fields)。在將 `UID` 作為可變參考暴露之前，請務必了解其影響。

</div>

由於動態欄位是附加在 `UID` 上的，它們在其他模組中的用法取決於 `UID` 是否可以被存取。預設情況下，結構的可見性會保護 `id` 欄位，不讓其他模組直接存取。然而，如果有一個公開的存取方法傳回對 `UID` 的參考，則動態欄位可以在其他模組中被讀取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid

```

在上述範例中，我們展示了如何暴露 `Character` 物件的 `UID`。此解決方案可能適用於某些應用程式，但重要的是要記住，暴露的 `UID` 允許讀取附加在該物件上的「任何」動態欄位。

如果您僅需在套件 (package) 內部暴露 `UID`，請使用限制性的可見性，例如 `public(package)`，或者更好的做法是使用更具體的存取方法，僅允許讀取特定的欄位。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid_measures

```

## 動態欄位 vs 欄位

動態欄位比常規欄位昂貴，因為存取它們需要額外的存儲和成本。它們的靈活性是有代價的，在決定使用動態欄位還是常規欄位時，了解其中的影響非常重要。

## 限制

動態欄位不受 [物件大小限制](./../guides/building-against-limits) 的約束，可用於存儲大量資料。然而，它們仍受限於 [動態欄位建立限制](./../guides/building-against-limits)，目前設定為單筆交易 1000 個欄位。

## 應用程式

動態欄位在任何複雜程度的應用程式中都能發揮關鍵作用。它們開闢了多種不同的使用場景，從存儲異質資料到將物件作為應用程式邏輯的一部分。基於稍後再定義定義並更改欄位類型的能力，它們還允許某些 [可升級性實踐](./../guides/upgradeability-practices)。

## 下一步

在下一節中，我們將介紹 [動態物件欄位](./dynamic-object-fields)，並解釋它們與動態欄位的區別，以及使用它們的影響。
