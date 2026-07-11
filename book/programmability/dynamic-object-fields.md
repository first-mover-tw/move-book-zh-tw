---
description:
  Sui 中的動態物件欄位 (dynamic object fields)：把物件掛載為欄位，並保持可透過 ID 存取，與一般動態欄位 (dynamic
  fields) 有所不同。
---

# 動態物件欄位 (Dynamic Object Fields) {#dynamic-object-fields}

> 本節是對 [動態欄位](./dynamic-fields) 的延伸說明。請先閱讀該節以理解動態欄位的基礎概念。

動態欄位還有另一種變體，稱為 _動態物件欄位 (dynamic object fields)_，它與一般動態欄位有若干差異。本節將說明動態物件欄位的細節，並解釋它與一般動態欄位有何不同。

> 一般建議是避免使用動態物件欄位，優先使用（單純的）動態欄位，尤其是在不需要透過 ID 直接發現的情況下。動態物件欄位所帶來的額外成本，可能無法用它提供的好處來證明其合理性。

## 定義 (Definition) {#definition}

動態物件欄位定義在 [Sui Framework](./sui-framework) 中的 `sui::dynamic_object_field` 模組。它在許多方面與動態欄位相似，但不同於動態欄位，動態物件欄位對 `Value` 型別有額外的限制。`Value` 必須同時具備 `key` 與 `store` 能力，而不僅是動態欄位所要求的 `store`。

該模組的定義比動態欄位的定義更精簡——只有欄位的 _name_ 會被包裝成一個 wrapper 型別，而值則是原樣儲存：

```move
module sui::dynamic_object_field;

/// 用於儲存欄位與其對應值的名稱之內部物件。使用獨立的型別
/// 是為了避免與直接使用 dynamic_field 時的 key 發生衝突
public struct Wrapper<Name> has copy, drop, store {
    name: Name,
}
```

不同於 [動態欄位](./dynamic-fields#definition) 一節中的 `Field` 型別，`Wrapper` 型別只儲存欄位的名稱。值本身就是物件，並 _不會被包裝_。

_完整文件請參閱 [sui::dynamic_object_field][dynamic-object-field-framework] 模組。_

`Value` 型別的限制會體現在動態物件欄位可用的方法中。以下是 `add` 函式的簽章：

```move
/// 在指定的 `object: &mut UID` 上，依照 `name: Name` 新增一個動態物件欄位。
/// 若該物件已存在同名欄位，則會以 `EFieldAlreadyExists` 中止。
public fun add<Name: copy + drop + store, Value: key + store>(
    // 我們在多處使用 &mut UID 來進行存取控制
    object: &mut UID,
    name: Name,
    value: Value,
) { /* 省略實作 */ }
```

其餘方法與 [動態欄位](./dynamic-fields#usage) 一節中的方法相同，並帶有相同的 `Value` 型別限制。以下列出供參考：

- `add` - 為物件新增一個動態物件欄位
- `remove` - 從物件移除一個動態物件欄位
- `borrow` - 借用物件的一個動態物件欄位
- `borrow_mut` - 借用物件的一個動態物件欄位的可變參照
- `exists_` - 檢查動態物件欄位是否存在
- `exists_with_type` - 檢查動態物件欄位是否以特定型別存在

此外，還有一個 `id` 方法，可回傳 `Value` 物件的 `ID`，而不需要指定其型別。

## 用法與動態欄位的差異 (Usage and Differences with Dynamic Fields) {#usage-and-differences-with-dynamic-fields}

動態欄位與動態物件欄位之間的主要差異在於，後者只允許儲存 _物件_ 作為值。這意味著你無法儲存像 `u64` 或 `bool` 這樣的基本型別。作為這個限制的交換，被附加的物件 _不會被包裝_ 成另一個物件：它保留了自己的 ID，並對鏈下工具維持可見。

> 這是在兩者之間選擇時要權衡的特性：以一般動態欄位附加的值會被包裝成一個 `Field` 物件，並從以 ID 為基礎的查詢中消失；而以動態物件欄位附加的值，則會在錢包與區塊鏈瀏覽器中，透過其 ID 保持可被發現。

```move file=packages/samples/sources/programmability/dynamic-object-fields.move anchor=usage

```

在上述範例中，`Accessory` 同時具備 `key` 與 `store`，因此可以作為動態物件欄位附加。而 `Metadata` 只有 `store`，因此只能作為一般動態欄位附加。這兩種欄位可以共存於同一個 `UID` 上——即便使用相似的名稱——因為內部的 `Wrapper` 型別可防止兩個模組之間的 key 衝突。最後，此範例也示範了 `id` 函式，該函式可回傳被附加物件的 `ID`，而不需要其型別——這是唯有物件保留自身識別性才可能做到的事。

## 計價差異 (Pricing Differences) {#pricing-differences}

動態物件欄位比動態欄位稍微貴一些。由於其內部結構，單一動態物件欄位會以兩個物件的形式儲存：一個儲存名稱的內部欄位，以及值物件本身。因此，新增與存取動態物件欄位的成本（相較於動態欄位載入 1 個物件，這裡要載入 2 個物件）會較高。

## 總結 (Summary) {#summary}

- 動態物件欄位要求值必須是一個物件（`key` + `store`），且不同於一般動態欄位，會讓被附加的物件在錢包與區塊鏈瀏覽器中，透過其 ID 保持可被發現。
- 其方法與動態欄位的方法相對應，並多了一個 `id` 函式，可回傳被附加物件的 `ID`，而不需要指定其型別。
- 動態物件欄位比動態欄位更昂貴，因此除非需要以 ID 為基礎的發現能力，否則應優先使用後者。

## 下一步 (Next Steps) {#next-steps}

動態欄位與動態物件欄位都是強大的功能，能在應用程式中實現創新的解決方案。然而，它們相對底層，需要謹慎處理以避免產生孤兒欄位。在下一節中，我們將介紹一個更高層次的抽象——[動態集合 (Dynamic Collections)](./dynamic-collections)——它有助於更有效地管理動態欄位與物件。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::dynamic_object_field][dynamic-object-field-framework] 模組文件。

[dynamic-object-field-framework]: https://docs.sui.io/references/framework/sui/dynamic_object_field
