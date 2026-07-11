---
description: 'Dynamic collections in Sui: Bag, Table, ObjectBag, ObjectTable, and LinkedTable built on dynamic fields for flexible storage.'
---

# 動態集合 (Dynamic Collections)

[Sui 框架](./sui-framework)基於[動態欄位](./dynamic-fields)和[動態物件欄位](./dynamic-object-fields)概念，提供了多種集合類型。這些集合被設計為一種更安全、更易於理解的方式來儲存和管理動態欄位和物件。

## 共同概念

所有的集合類型都共享以下方法：

- `add` - 向集合中新增欄位。
- `remove` - 從集合中移除欄位。
- `borrow` - 從集合中借用欄位。
- `borrow_mut` - 從集合中借用對欄位的可變引用。
- `contains` - 檢查集合中是否存在該欄位。
- `length` - 返回集合中的欄位數量。
- `is_empty` - 檢查長度是否為 0。

所有集合類型都支援 `borrow` 和 `borrow_mut` 方法的索引語法（方括號 `[]`）。

## Bag

`Bag` 就像其名稱所暗示的，作為一個異構值 (heterogeneous values) 的「袋子」。它是一種簡單、非泛型的類型，可以儲存任何數據。`Bag` 追蹤欄位數量，如果不為空則無法被銷毀，因此不會有「孤兒欄位」。

## ObjectBag

定義在 `sui::object_bag` 模組中。與 `Bag` 相同，但內部使用動態物件欄位，只能儲存物件作為值。

## Table

`Table` 是一種有類型的動態集合，具有固定的鍵 (Key) 和值 (Value) 類型。定義在 `sui::table` 模組中。

## ObjectTable

定義在 `sui::object_table` 模組中。與 `Table` 相同，但內部使用動態物件欄位，只能儲存物件作為值。

## LinkedTable

定義在 `sui::linked_table` 模組中。與 `Table` 類似，但值是鏈接在一起的，允許按順序插入和移除。

## 總結

- **Bag**: 可儲存任何類型數據的簡單集合。
- **ObjectBag**: 只能儲存物件的集合。
- **Table**: 具有固定鍵值類型的動態集合。
- **ObjectTable**: 只能儲存物件的有類型集合。
- **LinkedTable**: 具有鏈接功能且支援順序操作的 Table。
