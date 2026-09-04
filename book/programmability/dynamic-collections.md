---
description: Sui 中的動態集合 (dynamic collections)：以動態欄位 (dynamic fields) 為基礎建置的袋 (Bag)、表格 (Table)、物件袋 (ObjectBag)、物件表格 (ObjectTable) 與連結表格 (LinkedTable)，可提供彈性儲存 (flexible storage)。
title: 動態集合 (Dynamic Collections)
keywords:
  - Move
  - Sui
  - Move tutorial
  - dynamic
  - collections
  - dynamic fields
questions:
  - What is Dynamic Collections in Move?
  - How do I use Dynamic Collections in Move?
  - What is Common Concepts in Move?
  - What is ObjectBag in Move?
answer: 'Dynamic collections in Sui: Bag, Table, ObjectBag, ObjectTable, and LinkedTable built on dynamic fields for flexible storage.'
goal:
  description: 'Reader understands dynamic collections in Sui: Bag, Table, ObjectBag, ObjectTable, and LinkedTable built on dynamic fields for flexible storage'
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

# 動態集合 (Dynamic Collections) {#dynamic-collections}

[Sui Framework](./sui-framework) 提供多種集合型別，建構於
[動態欄位](./dynamic-fields)與[動態物件欄位](./dynamic-object-fields)的概念之上。
這些集合旨在提供更安全且更容易理解的方式，以儲存及管理動態
欄位與物件。

我們會針對每種集合型別，說明其使用的基元，以及所提供的特定功能。

> 與在 UID 上運作的動態（物件）欄位不同，集合型別具有自己的型別，
> 並允許呼叫[關聯函式](./../move-basics/struct-methods)。

## 通用概念 (Common Concepts) {#common-concepts}

所有五種集合都遵循相同的結構：具有 `key` 與 `store` 能力的結構體，持有
自己的 `UID` 與 `size` 計數器。項目會以動態欄位附加至該 `UID`。這也是為什麼
建立集合需要可變參考至 [交易情境](./transaction-context)——必須從中衍生出新的
`UID`——以及為什麼集合通常會儲存為另一個物件的欄位，如下方範例所示。

所有集合型別共用同一組核心方法：

- `new` - 建立新的空集合
- `add` - 將欄位加入集合（[LinkedTable](#linkedtable) 則改用 `push_front` 與
  `push_back`）
- `remove` - 從集合移除欄位並回傳其值
- `borrow` - 從集合借用欄位
- `borrow_mut` - 從集合借用欄位的可變參考
- `contains` - 檢查集合中是否存在欄位
- `length` - 回傳集合中的欄位數量
- `is_empty` - 檢查 `length` 是否為 0
- `destroy_empty` - 銷毀集合；若其中仍包含欄位則中止

最後一個方法使集合比原始動態欄位更安全：由於集合會追蹤其大小，因此在非空時
無法被銷毀，從而避免出現[孤立欄位](./dynamic-fields#orphaned-dynamic-fields)。這項保護的
另一面是：若集合的值無法被丟棄，則必須在銷毀前逐一清空項目；而由於每筆交易可
存取的動態欄位數量受到[限制](./../guides/building-against-limits)，拆解大型集合可能需要
超過一筆交易。

另一項繼承自動態欄位的特性是，金鑰無法在鏈上被發現：若要存取某個項目，程式碼
必須知道其金鑰。鏈下工具仍可列出所有項目，因為它們會以動態欄位儲存在集合的
`UID` 上。唯一能在鏈上走訪的集合是 [LinkedTable](#linkedtable)。

所有集合型別的 `borrow` 與 `borrow_mut` 方法都支援索引語法。若你在範例中看到中括號，
它們會被轉譯為對 `borrow` 與 `borrow_mut` 的呼叫。

```move
let hat: &Hat = &bag[b"key"];
let hat_mut: &mut Hat = &mut bag[b"key"];

// 等同於
let hat: &Hat = bag.borrow(b"key");
let hat_mut: &mut Hat = bag.borrow_mut(b"key");
```

範例不會著重於這些函式，而會聚焦於集合型別之間的差異。

## Bag 通用容器 (Bag) {#bag}

顧名思義，Bag 是異質值的「袋子」。它是建構於 [dynamic fields](./dynamic-fields) 之上的簡單非泛型
型別，可儲存任何資料。當單一容器必須容納不同型別的值時，Bag 是正確的
選擇——例如，攜帶各種類型物品的遊戲角色，或並排儲存無關設定的使用者設定檔。

```move
module sui::bag;

public struct Bag has key, store {
    /// 此 bag 的 ID
    id: UID,
    /// bag 中鍵值配對的數量
    size: u64,
}
```

_請參閱 [sui::bag][bag-framework] 模組的完整文件。_

由於 Bag 可儲存任何型別的值，因此它提供一個額外的方法：

- `contains_with_type` - 檢查是否存在具有特定型別的欄位

作為結構體欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=bag_struct

```

使用 Bag：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=bag_usage

```

## ObjectBag 物件容器 (ObjectBag) {#objectbag}

定義於 `sui::object_bag` 模組中。與 [Bag](#bag) 相同，但內部使用
[動態物件欄位](./dynamic-object-fields)。只能將物件儲存為值，作為交換，這些物件可透過其 ID 在鏈下工具中被發現。當儲存的值是應持續顯示於錢包與區塊鏈瀏覽器中的資產時，可在與 Bag 相同的異質情境中使用它——例如不同型別 NFT 的庫存清單。

與動態物件欄位相同，ObjectBag 提供 `value_id` 函式，可在不指定型別的情況下回傳已儲存物件的 `ID`。

_請參閱 [sui::object_bag][object-bag-framework] 模組的完整文件。_

## 表格 (Table) {#table}

表格是一種具型別的動態集合，其鍵和值具有固定型別。它建置於
[動態欄位](./dynamic-fields)之上，並定義於 `sui::table` 模組中。表格是大型統一登錄資料的首選
集合：使用者記錄、餘額，或以地址或名稱作為鍵的組態項目——例如下方範例中的 `UserRegistry`。

```move
module sui::table;

public struct Table<phantom K: copy + drop + store, phantom V: store> has key, store {
    /// 此表格的 ID
    id: UID,
    /// 表格中的鍵值組數量
    size: u64,
}
```

_請參閱 [sui::table][table-framework] 模組的完整文件。_

由於值的型別固定，表格提供了一個額外方法：

- `drop` - 即使表格非空也會銷毀它；僅在值型別具有
  [drop](./../move-basics/drop-ability) 能力時可用

作為結構的欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=table_struct

```

使用表格：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=table_usage

```

## ObjectTable 物件表格 (ObjectTable) {#objecttable}

定義於 `sui::object_table` 模組。與 [Table](#table) 相同，但內部使用
[動態物件欄位](./dynamic-object-fields)。只能將物件儲存為值，作為交換，它們可透過 ID 在鏈下工具中被發現。當登錄表儲存相同型別的完整物件時使用它——例如，以擁有者地址為索引鍵的使用者個人資料物件——且每個物件都應保持可被個別發現。

如同動態物件欄位，ObjectTable 提供 `value_id` 函式，可在不指定型別的情況下回傳已儲存物件的 `ID`。

_請參閱 [sui::object_table][object-table-framework] 模組的完整文件。_

儲存物件要求值型別具備 `key` 與 `store` 能力：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=object_table_struct

```

使用 ObjectTable：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=object_table_usage

```

## LinkedTable 連結表格 (LinkedTable) {#linkedtable}

定義於 `sui::linked_table` 模組。建立於[動態欄位](./dynamic-fields)之上，與
[Table](#table) 類似，但其中的項目彼此連結，因此可在任一端插入、依序
移除，以及在鏈上進行迭代。這使其適合用於任何必須在鏈上依序列舉或處理的用途：佇列與等候清單、
排行榜，或必須列出項目的登錄表，例如下方範例中的 `AdminRegistry`。

```move
module sui::linked_table;

public struct LinkedTable<K: copy + drop + store, phantom V: store> has key, store {
    /// 此表格的 ID
    id: UID,
    /// 表格中的鍵值配對數量
    size: u64,
    /// 表格前端，也就是第一個項目的鍵
    head: Option<K>,
    /// 表格後端，也就是最後一個項目的鍵
    tail: Option<K>,
}
```

_請參閱 [sui::linked_table][linked-table-framework] 模組的完整文件。_

由於 LinkedTable 中的項目彼此連結，新增項目時必須指定其位置，
因此它不提供 `add`，而是提供：

- `push_front` - 在表格前端插入鍵值配對
- `push_back` - 在表格後端插入鍵值配對
- `pop_front` - 移除表格前端並回傳鍵和值
- `pop_back` - 移除表格後端並回傳鍵和值

此外，`front`、`back`、`prev` 與 `next` 方法會回傳相鄰
項目的鍵，讓你可以在鏈上迭代表格。如同 [Table](#table)，LinkedTable
為具有 [drop](./../move-basics/drop-ability) 能力的值型別提供 `drop` 方法。

作為結構的欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=linked_table_struct

```

使用 LinkedTable：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=linked_table_usage

```

## 定價 (Pricing) {#pricing}

集合會繼承其所建構基礎型別的定價。建立集合會將具有 `UID` 的物件加入儲存空間；每個項目會依照[動態欄位](./dynamic-fields#dynamic-fields-vs-fields)計價，或者在物件變體中，依照[動態物件欄位](./dynamic-object-fields#pricing-differences)計價，後者每個項目需要兩個物件，因此成本較高。

## 選擇集合類型 (Choosing a Collection Type) {#choosing-a-collection-type}

簡短的決策指南：

- 鍵與值的型別固定且已知——使用 [Table](#table)；若值的型別不同，
  使用 [Bag](#bag)；
- 值是應持續顯示於錢包與區塊鏈瀏覽器中的物件——採用
  [ObjectTable](#objecttable) / [ObjectBag](#objectbag) 變體；
- 集合必須能在鏈上走訪，或保留插入順序——使用
  [LinkedTable](#linkedtable)，它是五者中唯一會連結其項目的類型；
- 集合很小、有界，且需要作為一般值內嵌或比較——前一節中以向量為基礎的
  [collections](./collections) 可能比動態集合更適合。

> 還有一點要記住：動態集合的項目位於結構本身之外。序列化 `Table`（例如使用 [BCS](./bcs)）或比較兩個資料表時，只會考量 `id` 與 `size` 欄位——絕不會考量其內容。

## 總結 (Summary) {#summary}

- [Bag](#bag) - 可儲存任何型別資料的簡單集合；適合用於異質值的容器，例如庫存。
- [ObjectBag](#objectbag) - 與 Bag 相同，但只能儲存物件；適合應持續顯示於錢包與區塊鏈瀏覽器中的異質資產。
- [Table](#table) - 對鍵和值具有固定型別的型別化動態集合；適合大型一致的登錄表。
- [ObjectTable](#objecttable) - 與 Table 相同，但只能儲存物件；適合應保持可個別探索的同型別物件登錄表。
- [LinkedTable](#linkedtable) - 類似 Table，但項目彼此連結；適合佇列及任何在鏈上迭代的項目。

## 後續步驟 (Next Steps) {#next-steps}

本節結束了對動態欄位及其上建立之集合的導覽。在下一節中，我們將繼續探討設計模式，並從 [Witness](./witness-pattern) 模式開始。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::table][table-framework] 模組文件。
- [sui::object_table][object-table-framework] 模組文件。
- [sui::linked_table][linked-table-framework] 模組文件。
- [sui::bag][bag-framework] 模組文件。
- [sui::object_bag][object-bag-framework] 模組文件。

[table-framework]: https://docs.sui.io/references/framework/sui/table
[object-table-framework]: https://docs.sui.io/references/framework/sui/object_table
[linked-table-framework]: https://docs.sui.io/references/framework/sui/linked_table
[bag-framework]: https://docs.sui.io/references/framework/sui/bag
[object-bag-framework]: https://docs.sui.io/references/framework/sui/object_bag
