---
description: Sui 中的動態欄位 (Dynamic fields)：在執行階段將異質鍵值資料附加至物件，以略過物件大小限制。
title: 動態欄位 (Dynamic Fields)
keywords:
  - Move
  - Sui
  - Move tutorial
  - dynamic
  - fields
  - dynamic fields
questions:
  - What is Dynamic Fields in Move?
  - How do I use Dynamic Fields in Move?
  - What is Definition in Move?
  - What is Usage in Move?
answer: 'Dynamic fields in Sui: attach heterogeneous key-value data to objects at runtime, bypassing object size limits.'
goal:
  description: 'Reader understands dynamic fields in Sui: attach heterogeneous key-value data to objects at runtime, bypassing object size limits'
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

# 動態欄位 (Dynamic Fields) {#dynamic-fields}

Sui 物件模型允許在執行階段將額外資料作為*動態欄位*附加至物件。其行為類似於其他程式語言中的 `Map`。不過，與在 Move 中會受到嚴格型別限制的 `Map` 不同（我們已在[集合](./collections)章節介紹過），動態欄位允許附加任何型別的值。前端開發領域中相似的做法是 JavaScript 的 Object 型別，可動態儲存任何型別的資料。

> 可附加至物件的動態欄位數量沒有限制。因此，動態欄位可用於儲存大量不符合物件大小限制的資料。

動態欄位支援廣泛的應用情境，從將資料拆分為較小部分以避免[物件大小限制](./../guides/building-against-limits)，到將物件作為應用程式邏輯的一部分附加至其他物件。

## 定義 (Definition) {#definition}

動態欄位定義於 [Sui Framework](./sui-framework) 的 `sui::dynamic_field` 模組中。它們會透過一個*名稱*附加至物件的 `UID`，並可使用該名稱存取。每個物件只能附加一個具有指定名稱的欄位。

```move
module sui::dynamic_field;

/// 用於儲存欄位和值的內部物件
public struct Field<Name: copy + drop + store, Value: store> has key {
    /// 由物件 ID、欄位名稱值及其型別的雜湊值決定，
    /// 即 hash(parent.id || name || Name)
    id: UID,
    /// 此欄位名稱的值
    name: Name,
    /// 繫結至此欄位的值
    value: Value,
}
```

如定義所示，動態欄位儲存在內部 `Field` 物件中；其 `UID` 會依據物件 ID、欄位名稱及欄位型別，以確定性的方式產生。`Field` 物件包含欄位名稱及繫結至該名稱的值。`Name` 與 `Value` 型別參數的限制，定義了鍵和值必須具備的能力。

_請參閱 [sui::dynamic_field][dynamic-field-framework] 模組的完整文件。_

## 使用方式 (Usage) {#usage}

動態欄位提供的方法很直接：可透過 `add` 新增欄位、透過 `remove` 移除欄位，以及透過 `borrow` 和 `borrow_mut` 讀取欄位。此外，可使用 `exists_` 方法檢查欄位是否存在（若需使用型別進行更嚴格的檢查，則可使用 `exists_with_type` 方法），而 `remove_if_exists` 會在欄位存在時將其移除，並回傳含有該值的 [`Option`](./../move-basics/option)。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=usage

```

在上述範例中，我們定義了一個 `Character` 物件，以及兩種永遠無法放在同一個向量中的不同配件型別。不過，動態欄位允許我們將它們一併儲存在單一物件中。兩個物件皆透過 `vector<u8>`（位元組字串常值）附加至 `Character`，並可使用各自的名稱存取。

如你所見，當我們將配件附加至 Character 時，是以*值*傳遞它們。換言之，兩個值都被移至新的範圍，其擁有權也轉移至 `Character` 物件。若我們變更 `Character` 物件的擁有權，配件也會隨之移動。

動態欄位最後一項值得突顯的重要特性是，它們會*透過父物件存取*。這表示 `Hat` 與 `Mustache` 物件無法直接存取，並遵循與父物件相同的規則。

## 作為動態欄位的外部型別 (Foreign Types as Dynamic Fields) {#foreign-types-as-dynamic-fields}

動態欄位允許物件攜帶任何型別的資料，包括其他模組中定義的型別。這是由於其泛型特性及型別參數相對寬鬆的限制所致。讓我們藉由將幾個不同值附加至 `Character` 物件來說明這點。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=foreign_types

```

在此範例中，我們展示了不同型別如何同時作為動態欄位的*名稱*和*值*使用。`String` 會透過 `vector<u8>` 名稱附加，`u64` 會透過 `u32` 名稱附加，而 `bool` 會透過 `bool` 名稱附加。使用動態欄位時，任何事都有可能！

## 作為欄位名稱的自訂型別 (Custom Type as a Field Name) {#custom-type-as-a-field-name}

在上述範例中，我們使用基本型別作為欄位名稱，因為它們具有必要的能力集合。然而，使用自訂型別作為欄位名稱時，動態欄位會變得更加有趣。這可提供更具結構化的資料儲存方式，並保護欄位名稱不被其他模組存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type

```

我們在上述定義的兩個欄位名稱為 `AccessoryKey` 和 `MetadataKey`。`AccessoryKey` 內含 `String` 欄位，因此可搭配不同的 `name` 值多次使用。`MetadataKey` 是空白鍵，只能附加一次。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=custom_type_usage

```

如你所見，只要自訂型別可以由模組*建構*，就可作為欄位名稱使用；換言之，這些型別必須是模組的*內部*型別，且於該模組中定義。對結構打包的這項限制，可為應用程式設計開啟新的方式。

此方法用於 [Object Capability](./object-capability) 模式；應用程式可授權外部物件在其中執行操作，同時不向其他模組公開能力。

## 公開 UID (Exposing UID) {#exposing-uid}

<div class="warning">

對 `UID` 進行可變存取具有安全風險。將你的型別的 `UID` 公開為可變參考，可能導致物件動態欄位遭到非預期的修改或移除。此外，這也會影響[轉移至物件](./../storage/transfer-to-object)及[動態物件欄位](./dynamic-object-fields)。在將 `UID` 公開為可變參考之前，請務必了解其影響。

</div>

由於動態欄位會附加至 `UID`，其他模組中對它們的使用取決於是否可存取 `UID`。預設的結構可見性會保護 `id` 欄位，且不允許其他模組直接存取它。不過，若存在會回傳 `UID` 參考的公開存取子方法，便可在其他模組中讀取動態欄位。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid

```

在上述範例中，我們展示如何公開 `Character` 物件的 `UID`。此解決方案可能適用於某些應用程式，但請務必記得，公開的 `UID` 可讀取附加至物件的*任何*動態欄位。

若你只需在套件內公開 `UID`，請使用限制性可見性，例如 `public(package)`；或者更好的做法是，使用更具體的存取子方法，僅允許讀取特定欄位。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=exposed_uid_measures

```

## 孤立動態欄位 (Orphaned Dynamic Fields) {#orphaned-dynamic-fields}

> 為防止產生孤立動態欄位，請使用會追蹤動態欄位、且在仍有附加欄位時不允許解構的 [Dynamic Collection Types](./dynamic-collections)，例如 `Bag`。

用於刪除 UID 的 `object::delete()` 函式不會追蹤動態欄位，因此無法防止動態欄位成為孤立欄位。父 UID 一旦遭刪除，動態欄位不會自動刪除，而會成為孤立欄位。這表示動態欄位仍儲存在區塊鏈中，但之後再也無法存取。

```move file=packages/samples/sources/programmability/dynamic-fields.move anchor=orphan_fields

```

孤立物件不適用於儲存回饋，且儲存費用將維持未領取狀態。避免在解構物件時產生孤立動態欄位的一種方式，是回傳 `UID` 並暫時將其儲存在某處，直到動態欄位被移除並妥善處理為止。

## 動態欄位與一般欄位 (Dynamic Fields vs Fields) {#dynamic-fields-vs-fields}

動態欄位比一般欄位更昂貴，因為它們需要額外的儲存空間及存取成本。其彈性伴隨代價，因此在決定使用動態欄位或一般欄位時，了解其影響十分重要。

## 限制 (Limits) {#limits}

動態欄位不受[物件大小限制](./../guides/building-against-limits)約束，因此可用於儲存大量資料。不過，它們仍受[建立動態欄位限制](./../guides/building-against-limits)約束，每筆交易上限為 1000 個欄位。

## 應用情境 (Applications) {#applications}

動態欄位可在任何複雜度的應用程式中扮演關鍵角色。它們開啟了各種不同的使用案例，從儲存異質資料到將物件作為應用程式邏輯的一部分附加。它們也支援某些基於可在*稍後*定義欄位並變更其型別之能力的[可升級性實務](./../guides/upgradeability-practices)。

## 總結 (Summary) {#summary}

- 動態欄位會將值以*名稱*附加至物件的 `UID`；名稱和值幾乎都可以是任何型別，包括其他模組中定義的型別。
- 附加的值由父物件擁有，且只能透過父物件存取。
- 作為欄位名稱使用的自訂型別只能由定義它們的模組建構，這可保護欄位免於遭到外部存取。
- 刪除父 `UID` 不會移除其動態欄位；遺留的欄位會成為無法存取的*孤立欄位*。

## 後續步驟 (Next Steps) {#next-steps}

下一節將介紹[動態物件欄位](./dynamic-object-fields)，並說明它們與動態欄位的差異，以及使用它們所帶來的影響。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::dynamic_field][dynamic-field-framework] 模組文件。

[dynamic-field-framework]: https://docs.sui.io/references/framework/sui/dynamic_field
