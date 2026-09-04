---
description: Sui 中的動態物件欄位 (dynamic object fields)：將物件 (objects) 作為可透過識別碼 (ID) 持續存取的欄位附加，且與一般動態欄位 (dynamic fields) 有所差異。
title: 動態物件欄位 (Dynamic Object Fields)
keywords:
  - Move
  - Sui
  - Move tutorial
  - dynamic
  - object
  - fields
  - object model
  - dynamic fields
questions:
  - What is Dynamic Object Fields in Move?
  - How do I use Dynamic Object Fields in Move?
  - What is Definition in Move?
  - What is Usage and Differences with Dynamic Fields in Move?
answer: 'Dynamic object fields in Sui: attach objects as fields that remain accessible by ID, with differences from regular dynamic fields.'
goal:
  description: 'Reader understands dynamic object fields in Sui: attach objects as fields that remain accessible by ID, with differences from regular dynamic fields'
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

# 動態物件欄位 (Dynamic Object Fields) {#dynamic-object-fields}

> 本節延伸說明[動態欄位](./dynamic-fields)。請先閱讀該節，以了解動態欄位的
> 基礎概念。

動態欄位的另一種變體是*動態物件欄位*，其與一般動態欄位存在一些差異。本節將介紹動態物件欄位的細節，並說明它們與一般動態欄位的不同之處。

> 一般建議使用（單純的）動態欄位，而避免使用動態物件欄位，
> 特別是在不需要透過 ID 直接探索時。動態物件欄位的額外成本，
> 可能無法由其提供的優點合理化。

## 定義 (Definition) {#definition}

動態物件欄位定義於 [Sui Framework](./sui-framework) 的
`sui::dynamic_object_field` 模組中。它們在許多方面與動態欄位相似，但與動態欄位不同的是，
動態物件欄位對 `Value` 型別有額外限制。`Value` 必須同時具備 `key` 與 `store`，
而不像動態欄位僅需具備 `store`。

此模組的定義比動態欄位更精簡——只有欄位*名稱*使用包裝型別，而值會照原樣儲存：

```move
module sui::dynamic_object_field;

/// 用於儲存欄位及其與值關聯名稱的內部物件。
/// 必須使用獨立型別，以避免與直接使用
/// dynamic_field 時發生鍵值衝突。
public struct Wrapper<Name> has copy, drop, store {
    name: Name,
}
```

與[動態欄位](./dynamic-fields#definition)章節中的 `Field` 型別不同，`Wrapper` 型別
只儲存欄位名稱。值就是物件本身，且*不會被包裝*。

_請參閱 [sui::dynamic_object_field][dynamic-object-field-framework] 模組的完整文件。_

`Value` 型別的限制可從動態物件欄位提供的方法中看出。以下是 `add` 函式的簽章：

```move
/// 將動態物件欄位新增至物件 `object: &mut UID`，其欄位由
/// `name: Name` 指定。若物件已具有同名欄位，則以 `EFieldAlreadyExists` 中止。
public fun add<Name: copy + drop + store, Value: key + store>(
    // 我們在多個位置使用 &mut UID 進行存取控制
    object: &mut UID,
    name: Name,
    value: Value,
) { /* 省略實作 */ }
```

其餘方法與[動態欄位](./dynamic-fields#usage)章節中的方法相同，並對 `Value`
型別具有相同限制。以下列出供參考：

- `add` - 將動態物件欄位新增至物件
- `remove` - 從物件移除動態物件欄位
- `borrow` - 從物件借用動態物件欄位
- `borrow_mut` - 從物件借用動態物件欄位的可變參考
- `exists_` - 檢查動態物件欄位是否存在
- `exists_with_type` - 檢查特定型別的動態物件欄位是否存在

此外，還有 `id` 方法，可在不指定型別的情況下回傳 `Value` 物件的 `ID`。

## 使用方式與動態欄位的差異 (Usage and Differences with Dynamic Fields) {#usage-and-differences-with-dynamic-fields}

動態欄位與動態物件欄位之間的主要差異在於，後者只允許將*物件*儲存為值。這表示你無法儲存
`u64` 或 `bool` 等原始型別。作為此限制的交換，附加的物件*不會被包裝*成獨立物件：
它會保留其 ID，並持續可供鏈下工具使用。

> 這是選擇兩者時需要權衡的特性：作為一般動態欄位附加的值，
> 會被包裝為 `Field` 物件，並從以 ID 為基礎的查詢中消失；而作為
> 動態物件欄位附加的值，則能在錢包與瀏覽器中透過其 ID 探索。

```move file=packages/samples/sources/programmability/dynamic-object-fields.move anchor=usage

```

在上述範例中，`Accessory` 同時具備 `key` 與 `store`，因此可作為動態物件欄位附加。
不過，`Metadata` 僅具備 `store`，因此只能作為一般動態欄位附加。兩種欄位可共存於同一個
`UID` 上——即使名稱相近也是如此——因為內部 `Wrapper` 型別可避免兩個模組之間發生鍵值衝突。
最後，範例展示了 `id` 函式；此函式可在不要求物件型別的情況下回傳附加物件的 `ID`——這之所以可行，
正是因為物件保留了自身識別身分。

## 定價差異 (Pricing Differences) {#pricing-differences}

動態物件欄位比動態欄位稍微昂貴。由於其內部結構，單一動態物件欄位會以兩個物件儲存：
一個儲存名稱的內部欄位，以及值物件本身。因此，新增與存取動態物件欄位的成本
（相較於動態欄位載入 1 個物件，需要載入 2 個物件）更高。

## 總結 (Summary) {#summary}

- 動態物件欄位要求值必須是物件（`key` + `store`）；與一般動態欄位不同，
  附加物件可在錢包與瀏覽器中透過其 ID 探索。
- 方法與動態欄位的方法相對應，另提供 `id` 函式，可在不指定型別的情況下回傳
  附加物件的 `ID`。
- 動態物件欄位比動態欄位昂貴，因此除非需要以 ID 為基礎的探索，
  否則應優先使用後者。

## 後續步驟 (Next Steps) {#next-steps}

動態欄位與動態物件欄位都是強大的功能，可在應用程式中實現創新的解決方案。然而，它們的層級相對較低，
必須謹慎處理，以避免產生孤立欄位。在下一節中，我們將介紹更高階的抽象概念——
[動態集合](./dynamic-collections)——它可協助你更有效地管理動態欄位與物件。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::dynamic_object_field][dynamic-object-field-framework] 模組文件。

[dynamic-object-field-framework]: https://docs.sui.io/references/framework/sui/dynamic_object_field
