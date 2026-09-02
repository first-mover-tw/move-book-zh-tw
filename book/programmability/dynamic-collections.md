---
description: 動態集合 (Dynamic Collections)：Sui 中基於動態欄位建構的 Bag、Table、ObjectBag、ObjectTable 與 LinkedTable，提供彈性儲存空間。
---

# 動態集合 (Dynamic Collections) {#dynamic-collections}

[Sui Framework](./sui-framework) 提供了多種集合型別，它們建立在 [動態欄位](./dynamic-fields) 和 [動態物件欄位](./dynamic-object-fields) 的概念之上。這些集合的設計目的是提供更安全、更容易理解的方式來儲存和管理動態欄位與物件。

對於每種集合型別，我們會說明它們所使用的基礎型別，以及它們提供的特定功能。

> 與直接對 UID 操作的動態（物件）欄位不同，集合型別擁有自己的型別，並允許呼叫[相關聯的函式](./../move-basics/struct-methods)。

## 常見概念 (Common Concepts) {#common-concepts}

所有五種容器都遵循相同的形狀：一個具有 `key` 與 `store` 能力的 struct，持有自己的 `UID` 與一個 `size` 計數器。條目會以動態欄位的形式附加在該 `UID` 上。這也是為什麼建立容器需要一個 [transaction context](./transaction-context) 的可變參考——必須從中衍生出一個全新的 `UID`——以及為什麼容器通常會被儲存為另一個物件的欄位，如下方範例所示。

所有容器型別都共用同一組核心方法：

- `new` - 建立一個新的空容器
- `add` - 為容器新增一個欄位（[LinkedTable](#linkedtable) 則改用 `push_front` 與 `push_back`）
- `remove` - 從容器移除一個欄位並回傳該值
- `borrow` - 從容器借用一個欄位
- `borrow_mut` - 從容器借用一個欄位的可變參考
- `contains` - 檢查容器中是否存在某個欄位
- `length` - 回傳容器中的欄位數量
- `is_empty` - 檢查 `length` 是否為 0
- `destroy_empty` - 銷毀容器，若其中仍含有欄位則會 abort

最後一個方法正是容器比原生動態欄位更安全的原因：因為容器會追蹤自身大小，所以無法在非空的狀態下被銷毀，這排除了[孤兒欄位](./dynamic-fields#orphaned-dynamic-fields)的可能性。這種保護的另一面是，一個其值無法被 drop 的容器，必須逐一條目清空後才能銷毀——而且由於每筆交易能存取的動態欄位數量是[有限的](./../guides/building-against-limits)，拆解一個大型容器可能需要不只一筆交易。

另一個繼承自動態欄位的特性是：鍵在鏈上是不可探索的——要存取一個條目，程式碼必須事先知道其鍵。鏈下工具仍可列出所有條目，因為它們是以動態欄位的形式儲存在容器的 `UID` 上。唯一能在鏈上被走訪的容器是 [LinkedTable](#linkedtable)。

所有容器型別都支援 `borrow` 與 `borrow_mut` 方法的索引語法。若你在範例中看到方括號，它們會被轉譯成 `borrow` 與 `borrow_mut` 呼叫。

```move
let hat: &Hat = &bag[b"key"];
let hat_mut: &mut Hat = &mut bag[b"key"];

// 等同於
let hat: &Hat = bag.borrow(b"key");
let hat_mut: &mut Hat = bag.borrow_mut(b"key");
```

在範例中我們不會著重在這些函式上，而是聚焦於各容器型別之間的差異。

## Bag 通用容器 (Bag) {#bag}

Bag，顧名思義，是一個裝載異質數值的「袋子」。它是一個建立在[動態欄位](./dynamic-fields)之上的簡單、非泛型型別，可以儲存任何資料。當單一容器需要保存不同型別的數值時，Bag 就是正確的選擇——例如遊戲角色攜帶各種型別的物品，或使用者個人檔案並列儲存不相關的設定。

```move
module sui::bag;

public struct Bag has key, store {
    /// this bag 的 ID
    id: UID,
    /// bag 中鍵值對的數量
    size: u64,
}
```

_完整文件請參閱 [sui::bag][bag-framework] 模組。_

由於 Bag 可以儲存任何型別的數值，它提供了一個額外的方法：

- `contains_with_type` - 檢查指定型別的欄位是否存在

作為結構體欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=bag_struct

```

使用 Bag：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=bag_usage

```

## ObjectBag 物件包 (ObjectBag) {#objectbag}

定義於 `sui::object_bag` 模組。與 [Bag](#bag) 相同，但內部使用
[動態物件欄位](./dynamic-object-fields)。只能儲存物件作為值，
而作為交換，能讓這些物件透過其 ID 在鏈下工具中被發現。當儲存的值是應該在
錢包與瀏覽器中保持可見的資產時（例如不同型別 NFT 的庫存），可用它來處理與
Bag 相同的異質場景。

與動態物件欄位相同，ObjectBag 提供 `value_id` 函式，可在不指定型別的情況下
回傳所儲存物件的 `ID`。

_完整文件請參閱 [sui::object_bag][object-bag-framework] 模組。_

## 表格 (Table) {#table}

Table 是一種型別化動態集合 (Table)，其鍵與值的型別都是固定的。它建構於[動態欄位](./dynamic-fields)之上，定義在 `sui::table` 模組中。Table 是大型統一登記表的首選集合：使用者紀錄、餘額，或以地址或名稱為鍵的設定項目——就像下方範例中的 `UserRegistry`。

```move
module sui::table;

public struct Table<phantom K: copy + drop + store, phantom V: store> has key, store {
    /// 這個表格的 ID
    id: UID,
    /// 表格中鍵值對的數量
    size: u64,
}
```

_請參閱 [sui::table 完整文件][table-framework] 模組。_

由於值的型別是固定的，Table 提供了一個額外的方法：

- `drop` - 即使 table 非空也會將其銷毀；僅在值型別具有 [drop](./../move-basics/drop-ability) 能力時可用

作為結構體欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=table_struct

```

使用 Table：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=table_usage

```

## ObjectTable 物件表 (ObjectTable) {#objecttable}

定義於 `sui::object_table` 模組。與 [Table](#table) 相同，但內部使用
[dynamic object fields](./dynamic-object-fields)。只能將物件儲存為值，
換來的好處是能讓鏈下工具透過 ID 找到它們。當一個註冊表儲存同一型別的完整物件時使用它——
例如以擁有者地址為鍵的使用者個人檔案物件——且每個物件都應該能被個別發現。

如同 dynamic object fields，ObjectTable 提供 `value_id` 函式，可在不指定型別的情況下回傳所儲存物件的 `ID`。

_完整文件請見 [sui::object_table][object-table-framework] 模組。_

儲存物件要求值型別具備 `key` 與 `store` 能力：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=object_table_struct

```

使用 ObjectTable：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=object_table_usage

```

## LinkedTable 連結表 (LinkedTable) {#linkedtable}

定義於 `sui::linked_table` 模組。建立在[動態欄位](./dynamic-fields)之上，類似於
[Table](#table)，但條目彼此連結，允許在任一端插入、有序
移除，以及鏈上走訪。這使它成為
任何必須在鏈上依序列舉或處理的資料結構的首選：佇列與候補名單、
排行榜，或條目必須被列出的登記表——就像下方範例中的 `AdminRegistry`。

```move
module sui::linked_table;

public struct LinkedTable<K: copy + drop + store, phantom V: store> has key, store {
    /// this table 的 ID
    id: UID,
    /// table 中鍵值對的數量
    size: u64,
    /// table 的前端，即第一個條目的鍵
    head: Option<K>,
    /// table 的後端，即最後一個條目的鍵
    tail: Option<K>,
}
```

_完整文件請見 [sui::linked_table 模組][linked-table-framework]。_

由於 LinkedTable 中的條目彼此連結，新增條目時必須指明它要放在哪裡，
因此它沒有 `add`，取而代之的是：

- `push_front` - 在 table 前端插入一組鍵值對
- `push_back` - 在 table 後端插入一組鍵值對
- `pop_front` - 移除 table 前端，回傳鍵與值
- `pop_back` - 移除 table 後端，回傳鍵與值

此外，`front`、`back`、`prev` 和 `next` 方法會回傳相鄰
條目的鍵，使得在鏈上走訪 table 成為可能。與 [Table](#table) 一樣，LinkedTable
為具備 [drop](./../move-basics/drop-ability) 能力的值型別提供了 `drop` 方法。

作為結構欄位使用：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=linked_table_struct

```

使用 LinkedTable：

```move file=packages/samples/sources/programmability/dynamic-collections.move anchor=linked_table_usage

```

## Pricing 定價 (Pricing) {#pricing}

Collections 繼承其所依賴基本型別的定價方式。建立一個 collection 會在儲存空間中新增一個帶有 `UID` 的 object；每個項目都會被計價為一個
[動態欄位](./dynamic-fields#dynamic-fields-vs-fields)，或者在 Object 變體中，被計價為一個
[動態 object 欄位](./dynamic-object-fields#pricing-differences)，其每個項目的成本較高，為兩個 object 的花費。

## 選擇集合型別 (Choosing a Collection Type) {#choosing-a-collection-type}

簡短的決策指南：

- 鍵與值的型別是固定且已知的 - 使用 [Table](#table)；如果值的型別會變化，
  使用 [Bag](#bag)；
- 值是應該對錢包與瀏覽器保持可見的物件 - 採用
  [ObjectTable](#objecttable) / [ObjectBag](#objectbag) 變體；
- 集合必須在鏈上走訪或需要保留插入順序 - 使用
  [LinkedTable](#linkedtable)，這是五者中唯一會連結其項目的型別；
- 集合很小、有界，且需要被嵌入或以純值方式比較 - 前面章節提到的
  基於 vector 的[集合](./collections)，可能會比動態集合更適合。

> 還有一件事要記住：動態集合的項目存在於結構本身之外。序列化一個 `Table`
> （例如使用 [BCS](./bcs)）或比較兩個 table 時，只會考慮 `id` 與 `size`
> 欄位 - 絕不會考慮內容本身。

## 總結 (Summary) {#summary}

- [Bag 通用容器 (#bag)](#bag) - 一種可以儲存任何型別資料的簡單集合;適合存放異質值的容器,例如物品欄。
- [ObjectBag 物件容器 (#objectbag)](#objectbag) - 與 Bag 相同,但只能儲存物件;適合需要在錢包和瀏覽器中保持可見的異質資產。
- [Table 型別化表格 (#table)](#table) - 一種對鍵與值有固定型別的型別化動態集合;適合大型統一登錄項。
- [ObjectTable 物件表格 (#objecttable)](#objecttable) - 與 Table 相同,但只能儲存物件;適合需要個別可被探索的同型別物件登錄項。
- [LinkedTable 鏈結表格 (#linkedtable)](#linkedtable) - 與 Table 類似,但項目彼此鏈結;適合佇列與任何需要在鏈上走訪的情境。

## 下一步 (Next Steps) {#next-steps}

本節結束了對動態欄位以及基於其建構之集合的介紹。在下一節中，我們將繼續探討設計模式，從
[見證者](./witness-pattern) 模式開始。

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
