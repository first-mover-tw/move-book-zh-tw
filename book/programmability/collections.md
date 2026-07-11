---
description:
  Vector 型集合 (Vector-based Collections) 在 Sui Framework 中：VecSet 和 VecMap，其操作與限制，以及何時該改用動態集合
  (Dynamic Collections)。
---

# 集合 (Collections) {#collections}

儲存一組值的能力是程式中最常見的需求之一。Move Basics 章節介紹的 [`vector`](./../move-basics/vector) 型別是實現這個需求的基礎建構區塊，而 [Sui Framework](./sui-framework) 在此之上擴充了兩種集合型別，加上額外的結構：`VecSet` 讓元素保持唯一，而 `VecMap` 則將鍵與值關聯起來。在本節中，我們將以這三者最常見的角色——作為物件的欄位——進行介紹，並展示各自的操作方式與限制。

## Vector 向量 (Vector) {#vector}

雖然[向量章節](./../move-basics/vector)將 `vector` 型別呈現為一個獨立的值，但在實際應用中，它通常存在於物件內部。一個擁有書籍清單的商店，就是把 vector 放在欄位裡：

```move file=packages/samples/sources/programmability/collections.move anchor=vector

```

向量章節中的一切在這裡都同樣適用；下面介紹的集合型別也遵循相同的模式——它們是可以放進欄位、傳遞的純粹 struct 值，並且不同於本章稍後介紹的[動態欄位](./dynamic-fields)，它們完全由持有它們的物件的型別所描述。

## VecSet 唯一集合 (VecSet) {#vecset}

`VecSet` 是一種儲存*唯一*項目的集合。插入一個已存在的值會中止，因此這種集合非常適合用於不能有重複項目的集合，例如 ID 或地址的清單。

```move file=packages/samples/sources/programmability/collections-2.move anchor=vec_set

```

`contains` 函式可以回答成員資格的問題，而集合內容可以透過引用以 `keys` 讀回，或是透過 `into_keys` 取出成一個純粹的 `vector`——例如，可以用[向量巨集](./../move-basics/vector#vector-macros)對其進行走訪。

> `VecSet` 的元素型別必須具備 [`copy`](./../move-basics/copy-ability) 與 [`drop`](./../move-basics/drop-ability) 能力。這對原生型別與簡單的資料 struct 來說是成立的，但排除了在集合中儲存資產的可能性。

## VecMap 鍵值映射 (VecMap) {#vecmap}

`VecMap` 是一種鍵值對的集合，其中每個鍵都是唯一的，並對應到單一一個值。讀回一個值是映射的日常操作，有兩種方式可以做到：索引語法 `map[&key]` 會借用一個值，若鍵不存在則中止；而 `try_get` 則會回傳一個 [`Option`](./../move-basics/option)，且永遠不會中止。

```move file=packages/samples/sources/programmability/collections-3.move anchor=vec_map

```

和 `VecSet` 一樣，`VecMap` 在嘗試 `insert` 一個已存在的鍵時會中止——它*不會*悄悄地覆寫舊值。要取代一個值，需要透過可變引用（如上面的範例所示），或是先移除舊的項目。`VecMap` 的鍵必須具備 [`copy`](./../move-basics/copy-ability) 能力，而值則可以是任何型別。

## 限制 (Limitations) {#limitations}

以向量為基礎的集合是嚴格型別化的：`VecSet<address>` 只會存放地址，不會存放其他東西，這在大多數情況下正是你想要的，但也使得它們不適合用於異質資料。它們同時也是儲存在物件內部的純粹值，因此會計入 [Building Against Limits](./../guides/building-against-limits) 指南中所描述的 256KB 物件大小限制。

在實務上，另一個限制會更早發揮作用：每一個操作——`insert`、`contains`、`get`——都會逐一元素地掃描底層的 vector，因此每次存取的成本會隨著集合大小而增加。當元素數量很小且有限——幾十個或幾百個項目時，以向量為基礎的集合表現得很好。對於大型或無上限的集合，Sui Framework 提供了 `Table`、`Bag` 及其他以物件為基礎的型別，我們將在本章稍後的[動態集合](./dynamic-collections)章節中介紹。

最後，以向量為基礎的集合並不支援一般預期的相等性比較。`VecSet` 與 `VecMap` 會按插入順序保留其內容，而 `==` 運算子則是逐一元素地比較底層的 vector。因此，兩個包含相同元素、但插入順序不同的集合，兩者並*不*相等。

> 這種行為會被 linter 抓到並發出警告：_Comparing collections of type 'sui::vec_set::VecSet' may yield unexpected result_

```move file=packages/samples/sources/programmability/collections-4.move anchor=vec_set_comparison

```

在上面的範例中，兩個集合都包含相同的元素——`1` 與 `2`——但它們的插入順序不同。由於比較是對順序敏感的，`set1 == set2` 的結果會是 `false`，斷言因此會中止。除非你能保證元素是以相同的順序插入，否則不要依賴 `==` 來比較以向量為基礎的集合。

## 總結 (Summary) {#summary}

- Vector 是一種原生型別，可以儲存一串項目清單；在物件內部，它會以一般欄位的形式出現。
- VecSet 是建構在 vector 之上，儲存唯一的項目；插入重複項目會中止。
- VecMap 儲存具有唯一鍵的鍵值對；插入已存在的鍵會中止，而值可以透過索引語法或 `try_get` 讀取。
- 以向量為基礎的集合是嚴格型別化的，每次操作都會線性掃描其內容，最適合用於小型、有限的集合與清單；更大的集合則需要使用[動態集合](./dynamic-collections)。

## 下一步 (Next Steps) {#next-steps}

在下一節中，我們將介紹[包裝型別模式](./wrapper-type-pattern)——一種常與集合型別搭配使用、用來擴充或限制其行為的設計模式。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::vec_set][vec-set-framework] 模組文件。
- [sui::vec_map][vec-map-framework] 模組文件。

[vec-set-framework]: https://docs.sui.io/references/framework/sui/vec_set
[vec-map-framework]: https://docs.sui.io/references/framework/sui/vec_map
