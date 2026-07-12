---
description: 動態欄位 (Dynamic Fields) 在 Sui 中：於執行時將異質鍵值資料附加到物件上，突破物件大小限制。
---

# 動態欄位 (Dynamic Fields) {#dynamic-fields}

Sui Object Model 允許在執行期以*動態欄位*的形式為物件附加額外資料。其行為類似於其他程式語言中 `Map` 的運作方式。然而，與 Move 中嚴格型別化的 `Map`（我們已在 [Collections](./collections) 章節介紹過）不同，動態欄位允許附加任何型別的值。從前端開發的世界來看，類似的做法是 JavaScript 的 Object 型別，允許動態儲存任何型別的資料。

> 附加到一個物件上的動態欄位數量沒有上限。因此，動態欄位可以用來儲存大量不符合物件大小限制的資料。

動態欄位允許廣泛的應用範圍，從將資料拆分成較小的部分以避免超出[物件大小限制](./../guides/building-against-limits)，到將物件附加為應用程式邏輯的一部分。

## 定義 (Definition) {#definition}

動態欄位定義於 [Sui Framework](./sui-framework) 的 `sui::dynamic_field` 模組中。它們透過一個*名稱 (name)* 附加到物件的 `UID` 上，並可透過該名稱存取。一個物件上，同一個名稱只能附加一個欄位。

```move
module sui::dynamic_field;

/// 用來儲存欄位與值的內部物件
public struct Field<Name: copy + drop + store, Value: store> has key {
    /// 由物件 ID、欄位名稱的雜湊值決定
    /// 值及其型別，即 hash(parent.id || name || Name)
    id: UID,
    /// 此欄位名稱的值
    name: Name,
    /// 綁定到此欄位的值
    value: Value,
}
```

如上述定義所示，動態欄位儲存在一個內部的 `Field` 物件中，該物件的 `UID` 是根據物件 ID、欄位名稱以及欄位型別，以確定性的方式產生的。`Field` 物件包含欄位名稱以及與其綁定的值。`Name` 和 `Value` 型別參數上的限制條件，定義了鍵與值必須具備的能力 (abilities)。

_完整文件請參閱 [sui::dynamic_field][dynamic-field-framework] 模組。_

## 用法 (Usage) {#usage}

動態欄位可用的方法相當直觀：可以用 `add` 新增欄位、用 `remove` 移除欄位、用 `borrow` 與 `borrow_mut` 讀取欄位。此外，`exists_` 方法可用來檢查欄位是否存在（若需要更嚴格的型別檢查，則有 `exists_with_type` 方法），而 `remove_if_exists` 會在欄位存在時將其移除，並回傳一個包含該值的 [`Option`](./../move-basics/option)。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=usage

```

在上述範例中，我們定義了一個 `Character` 物件，以及兩種不同型別的配件，這兩種型別絕對無法放進同一個 vector 中。然而，動態欄位讓我們可以將它們一起儲存在同一個物件裡。這兩個物件都是透過 `vector<u8>`（一個位元組字串字面值）附加到 `Character` 上，並可透過各自的名稱存取。

如你所見，當我們將配件附加到 Character 時，是以*傳值*的方式傳遞。換句話說，這兩個值都被移動到一個新的作用域中，其所有權也轉移給了 `Character` 物件。如果我們改變了 `Character` 物件的所有權，這些配件也會隨之一起移動。

我們應該強調的動態欄位最後一個重要特性，是它們是*透過其父物件存取*的。這表示 `Hat` 和 `Mustache` 物件無法被直接存取，而是遵循與父物件相同的規則。

## 外部型別作為動態欄位 (Foreign Types as Dynamic Fields) {#foreign-types-as-dynamic-fields}

動態欄位允許物件攜帶任何型別的資料，包含在其他模組中定義的型別。這之所以可行，是因為它們具有泛型的特性，且對型別參數的限制相對寬鬆。讓我們透過將幾個不同的值附加到 `Character` 物件上來說明這一點。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=foreign_types

```

在這個範例中，我們展示了動態欄位的*名稱*與*值*可以使用不同的型別。`String` 是透過 `vector<u8>` 名稱附加的，`u64` 是透過 `u32` 名稱附加的，而 `bool` 則是透過 `bool` 名稱附加的。使用動態欄位，任何事情都是可能的！

## 自訂型別作為欄位名稱 (Custom Type as a Field Name) {#custom-type-as-a-field-name}

在上述範例中，我們使用基本型別作為欄位名稱，因為它們具備所需的能力集合。但當我們使用自訂型別作為欄位名稱時，動態欄位會變得更加有趣。這讓資料的儲存方式更加結構化，也能保護欄位名稱不被其他模組存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type

```

我們在上面定義的兩個欄位名稱是 `AccessoryKey` 和 `MetadataKey`。`AccessoryKey` 內含一個 `String` 欄位，因此可以搭配不同的 `name` 值多次使用。`MetadataKey` 則是一個空的鍵，只能附加一次。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type_usage

```

如你所見，自訂型別可以作為欄位名稱使用，前提是它們能被該模組*建構 (constructed)*——換句話說，如果它們是該模組*內部*的，且定義於該模組中。這種對 struct 打包 (packing) 的限制，可以為應用程式的設計開啟新的可能性。

這種方法被用於[物件能力 (Object Capability)](./object-capability) 模式中，應用程式可以授權一個外部物件在其中執行操作，同時不將該能力暴露給其他模組。

## 暴露 UID (Exposing UID) {#exposing-uid}

<div class="warning">

可變存取 `UID` 存在安全風險。將你的型別的 `UID` 以可變參考的形式暴露出去，可能導致物件的動態欄位遭到非預期的修改或移除。此外，這也會影響[轉移至物件 (Transfer to Object)](./../storage/transfer-to-object)以及[動態物件欄位 (Dynamic Object Fields)](./dynamic-object-fields)。在將 `UID` 以可變參考的形式暴露之前，請務必了解其影響。

</div>

由於動態欄位是附加在 `UID` 上的，它們在其他模組中的可用性取決於該 `UID` 是否可被存取。預設情況下，struct 的可見性 (visibility) 會保護 `id` 欄位，不讓其他模組直接存取它。然而，如果存在一個公開的存取方法，會回傳 `UID` 的參考，那麼動態欄位就可以在其他模組中被讀取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid

```

在上述範例中，我們展示了如何暴露 `Character` 物件的 `UID`。這個解法可能適用於某些應用程式，然而，重要的是要記住，暴露出去的 `UID` 允許讀取附加在該物件上的*任何*動態欄位。

如果你只需要在套件內部暴露 `UID`，請使用限制性較強的可見性，例如 `public(package)`，或者更好的做法是——使用更具體的存取方法，只允許讀取特定的欄位。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid_measures

```

## 孤立的動態欄位 (Orphaned Dynamic Fields) {#orphaned-dynamic-fields}

> 為了避免產生孤立的動態欄位，請使用[動態集合型別 (Dynamic Collection Types)](./dynamic-collections)，例如 `Bag`，因為它們會追蹤動態欄位，若仍有已附加的欄位，就不允許解包 (unpacking)。

用於刪除 UID 的 `object::delete()` 函式並不會追蹤動態欄位，也無法防止動態欄位變成孤立狀態。一旦父 UID 被刪除，動態欄位並不會自動被刪除，而是會變成孤立的。這表示這些動態欄位仍然儲存在區塊鏈上，但將永遠無法再被存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=orphan_fields

```

孤立的物件不適用儲存回饋 (storage rebate)，其儲存費用將永遠無法被領回。在解包物件時，避免產生孤立動態欄位的其中一種方法，是回傳該 `UID` 並將其暫時儲存在某處，直到動態欄位被適當地移除並處理完畢。

## 動態欄位與一般欄位 (Dynamic Fields vs Fields) {#dynamic-fields-vs-fields}

動態欄位比一般欄位更昂貴，因為存取它們需要額外的儲存空間與成本。它們的靈活性是有代價的，在決定使用動態欄位還是一般欄位時，理解其影響是很重要的。

## 限制 (Limits) {#limits}

動態欄位不受[物件大小限制](./../guides/building-against-limits)的約束，可以用來儲存大量資料。然而，它們仍然受到[動態欄位建立數量限制](./../guides/building-against-limits)的約束，該限制設定為每筆交易 1000 個欄位。

## 應用場景 (Applications) {#applications}

動態欄位在任何複雜度的應用程式中都能扮演至關重要的角色。它們開啟了各式各樣不同的使用情境，從儲存異質資料，到將物件附加為應用程式邏輯的一部分。它們也支援某些[可升級性實踐做法](./../guides/upgradeability-practices)，這些做法依賴於能夠*事後*定義欄位並改變欄位型別的能力。

## 總結 (Summary) {#summary}

- 動態欄位以一個*名稱*為單位，將值附加到物件的 `UID` 上；名稱與值幾乎可以是任何型別，包含在其他模組中定義的型別。
- 已附加的值歸父物件所有，且只能透過父物件存取。
- 用作欄位名稱的自訂型別，只能由定義該型別的模組建構，藉此保護欄位不被外部存取。
- 刪除父 `UID` 並不會移除其動態欄位——遺留下來的欄位會變成無法存取的*孤兒*。

## 下一步 (Next Steps) {#next-steps}

在下一節中，我們將介紹[動態物件欄位 (Dynamic Object Fields)](./dynamic-object-fields)，並說明它們與動態欄位有何不同，以及使用它們會帶來哪些影響。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::dynamic_field][dynamic-field-framework] 模組文件。

[dynamic-field-framework]: https://docs.sui.io/references/framework/sui/dynamic_field
