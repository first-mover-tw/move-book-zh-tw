---

description: "Vectors in Move: create, manipulate, and iterate over dynamic collections with push, pop, and destroy operations."
---

# 向量 (Vector)

向量是 Move 中儲存元素集合的一種原生方式。它們類似於其他程式語言中的陣列，但有一些不同之處。在本節中，我們將介紹 `vector` 類型及其操作。

## 向量語法 (Vector syntax)

`vector` 類型的寫法是使用 `vector` 關鍵字，後接角括號括起來的元素類型。元素類型可以是任何有效的 Move 類型，包括其他向量。

Move 有一種向量常值 (literal) 語法，允許您使用 `vector` 關鍵字，後接包含元素的方括號（如果是空向量則不包含元素）來建立向量。

```move file=packages/samples/sources/move-basics/vector.move anchor=literal

```

`vector` 類型是 Move 中的內建類型，不需要從模組匯入。向量操作定義在 `std::vector` 模組中，該模組會被隱式匯入，且無需明確的 `use` 匯入即可直接使用。

## 向量操作 (Vector operations)

標準庫提供了操作向量的方法。以下是一些最常用的操作：

- `push_back`: 在向量末尾添加一個元素。
- `pop_back`: 移除向量的最後一個元素。
- `length`: 傳回向量中的元素數量。
- `is_empty`: 如果向量為空則傳回 true。
- `remove`: 移除指定索引處的元素。

```move file=packages/samples/sources/move-basics/vector.move anchor=methods

```

## 銷毀不可丟棄類型的向量 (Destroying a Vector of non-droppable types)

不可丟棄類型的向量不能被捨棄。如果您定義了一個不具備 `drop` 能力的類型的向量，則該向量的值不能被忽略。如果向量為空，編譯器要求明確呼叫 `destroy_empty` 函式。

```move file=packages/samples/sources/move-basics/vector.move anchor=no_drop

```

如果您對非空向量呼叫 `destroy_empty` 函式，它將在執行時期失敗。

## 延伸閱讀

- Move 參考手冊中的 [向量 (Vector)](./../../reference/primitive-types/vector)。
- [`std::vector`](https://docs.sui.io/references/framework/std/vector) 模組文件。
