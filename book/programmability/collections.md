---

description: "Collection types in Sui Move: VecSet, VecMap, and other vector-based data structures from the Sui Framework."
---

# 集合 (Collections)

集合類型是任何程式語言的基本組成部分。它們用於儲存一組數據。我們已經在[向量 (Vector)](./../move-basics/vector) 部分介紹過 `vector` 類型，本章我們將介紹 [Sui 框架](./sui-framework) 提供的基於向量的集合類型。

## Vector (向量)

雖然之前介紹過 `vector`，但在物件的上下文中值得再次回顧。它常用於物件內部儲存簡單列表。

## VecSet

`VecSet` 是一種儲存唯一項 (unique items) 的集合。它與 `vector` 類似，但不允許重複項。這對於儲存唯一 ID 或地址列表非常有用。如果嘗試插入已存在的項，操作將失敗。

## VecMap

`VecMap` 是一種儲存鍵值對 (key-value pairs) 的集合。它類似於映射 (Map)，您可以將一個值與集合中的每個項關聯。`VecMap` 中的鍵是唯一的，每個鍵只能關聯一個值。

## 限制 (Limitations)

- **類型限制**: 嚴格的類型檢查。
- **大小限制**: 受到物件大小限制 (256KB)，適用於較小規模的列表或集合。
- **比較限制**: 由於插入順序不固定，嘗試比較兩個 `VecSet` 可能會產生非預期結果（Linter 會發出警告）。

## 總結

- **Vector**: 原生類型，儲存列表。
- **VecSet**: 基於 Vector，儲存唯一項集合。
- **VecMap**: 儲存鍵值對結構。
- **基於向量的集合**: 適用於小規模、有類型的數據儲存。
