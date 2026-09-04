---
description: Sui Framework 中以向量為基礎的集合：VecSet 與 VecMap、其操作與限制，以及何時應改用動態集合。
title: 集合 (Collections)
keywords:
  - Move
  - Sui
  - Move tutorial
  - collections
questions:
  - What is Collections in Move?
  - How do I use Collections in Move?
  - What is Vector in Move?
  - What is VecSet in Move?
answer: 'Vector-based collections in the Sui Framework: VecSet and VecMap, their operations and constraints, and when to reach for dynamic collections instead.'
goal:
  description: 'Reader understands vector-based collections in the Sui Framework: VecSet and VecMap, their operations and constraints, and when to reach for dynamic collections instead'
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

# 集合 (Collections) {#collections}

在程式中儲存一組值是最常見的需求之一。Move 基礎章節介紹的
[`vector`](./../move-basics/vector) 型別是實現此需求的基本建構區塊，而 [Sui Framework](./sui-framework)
在其上擴充了兩種集合型別：用於保持元素唯一性的 `VecSet`，以及將鍵與值建立關聯的
`VecMap`。本節將介紹這三種型別最常見的用途——作為物件的欄位——並說明各自的操作與限制。

## 向量 (Vector) {#vector}

雖然 [vector 章節](./../move-basics/vector)將 `vector` 型別介紹為獨立值，但在實際應用程式中，
它通常存在於物件內。一間擁有書籍清單的商店，會將向量作為欄位：

```move file=packages/samples/sources/programmability/collections.move anchor=vector

```

向量章節的所有內容在此都同樣適用；下列集合型別遵循相同模式——可放入欄位、傳遞使用的
一般 struct 值；與本章後續介紹的[動態欄位](./dynamic-fields)不同，這些集合型別可由持有它們
之物件的型別完整描述。

## VecSet 唯一元素集合 (VecSet) {#vecset}

`VecSet` 是儲存*唯一*項目的集合。插入已存在的值會中止，因此集合很適合不得包含重複項目的
集合，例如 ID 或地址清單。

```move file=packages/samples/sources/programmability/collections-2.move anchor=vec_set

```

`contains` 函式可判斷成員資格；你可以透過 `keys` 以參考方式讀取內容，或使用 `into_keys`
將內容取出為一般 `vector`——例如使用 [vector 巨集](./../move-basics/vector#vector-macros)
走訪其中元素。

> `VecSet` 的元素型別必須具有 [`copy`](./../move-basics/copy-ability) 與
> [`drop`](./../move-basics/drop-ability) 能力。基礎型別與簡單資料 struct 都符合此條件，
> 但這表示無法在集合中儲存資產。

## VecMap 鍵值對集合 (VecMap) {#vecmap}

`VecMap` 是鍵值對集合，其中每個鍵皆為唯一，並對應單一值。讀取值是 map 的日常操作，
而且有兩種方式：索引語法 `map[&key]` 會借用一個值，若鍵不存在則中止；`try_get` 則回傳
[`Option`](./../move-basics/option)，且永遠不會中止。

```move file=packages/samples/sources/programmability/collections-3.move anchor=vec_map

```

與 `VecSet` 相同，`VecMap` 嘗試 `insert` 已存在的鍵時會中止——它*不會*悄悄覆寫舊值。
若要取代值，必須如上述範例所示透過可變參考，或先移除舊項目。`VecMap` 的鍵必須具有
[`copy`](./../move-basics/copy-ability) 能力，而值可以是任何型別。

## 限制 (Limitations) {#limitations}

以向量為基礎的集合具有嚴格型別：`VecSet<address>` 僅可保存地址，不能保存其他內容。
這通常正是你所需，但也使其不適合異質資料。它們也是儲存在物件內的一般值，因此會計入
[依限制建置](./../guides/building-against-limits)指南所述的 256KB 物件大小限制。

實務上，另一項限制更早成為問題：每項操作——`insert`、`contains`、`get`——都會逐一掃描
底層向量元素，因此每次存取的成本會隨集合大小增加。以向量為基礎的集合適合元素數量小且
有界的情況——數十或數百個項目。對於大型或無界集合，Sui Framework 提供 `Table`、`Bag`
及其他以物件為基礎的型別，將於本章後續的[動態集合](./dynamic-collections)章節介紹。

最後，以向量為基礎的集合不支援可能符合預期的相等性比較。`VecSet` 與 `VecMap` 會依插入
順序保存內容，且 `==` 運算子會逐一比較底層向量的元素。因此，包含相同元素但以不同順序
接收元素的兩個集合*不會*相等。

> 此行為會由 linter 偵測並發出警告：_比較型別為
> 'sui::vec_set::VecSet' 的集合可能產生非預期結果_

```move file=packages/samples/sources/programmability/collections-4.move anchor=vec_set_comparison

```

在上述範例中，兩個集合都包含相同元素——`1` 與 `2`——但它們以不同順序插入。由於比較會
考量順序，`set1 == set2` 的結果為 `false`，而斷言會中止。除非你能保證元素以相同順序插入，
否則請勿依賴 `==` 比較以向量為基礎的集合。

## 總結 (Summary) {#summary}

- 向量是可儲存項目清單的原生型別；在物件內，它會作為一般欄位出現。
- VecSet 建立於向量之上並儲存唯一項目；插入重複項目會中止。
- VecMap 儲存具有唯一鍵的鍵值對；插入既有鍵會中止，而值可透過索引語法或 `try_get` 讀取。
- 以向量為基礎的集合具有嚴格型別、每次操作皆會線性掃描內容，最適合小型且有界的集合與
  清單；較大的集合則適合使用[動態集合](./dynamic-collections)。

## 後續步驟 (Next Steps) {#next-steps}

下一節將介紹[包裝器型別模式](./wrapper-type-pattern)——一種常與集合型別搭配使用，用於擴充
或限制其行為的設計模式。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::vec_set][vec-set-framework] 模組文件。
- [sui::vec_map][vec-map-framework] 模組文件。

[vec-set-framework]: https://docs.sui.io/references/framework/sui/vec_set
[vec-map-framework]: https://docs.sui.io/references/framework/sui/vec_map
