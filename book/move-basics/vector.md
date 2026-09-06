---
description: Move 中的向量 (Vectors)：建立動態集合、讀取、新增及移除元素、使用向量巨集 (vector macros) 進行迭代，以及銷毀不可丟棄型別 (non-droppable types) 的向量。
title: 向量 (Vector)
keywords:
  - Move
  - Sui
  - Move tutorial
  - vector
  - collections
questions:
  - What is Vector in Move?
  - How do I use Vector in Move?
  - What is Vector Syntax in Move?
  - What is Reading Elements in Move?
answer: 'Vectors in Move: create dynamic collections, read, add and remove elements, iterate with vector macros, and destroy vectors of non-droppable types.'
goal:
  description: 'Reader understands vectors in Move: create dynamic collections, read, add and remove elements, iterate with vector macros, and destroy vectors of non-droppable types'
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

# 向量 (Vector) {#vector}

`vector` 是 Move 中用來儲存元素集合的內建方式。它是有序、可擴增的
集合，類似其他程式語言中的陣列或串列，也是其他型別的建構基礎：後續章節中介紹的
[`Option`](./option) 與 [`String`](./string) 型別皆以向量為基礎。本節將介紹 `vector`
型別、其操作，以及讓使用更便利的巨集。

## 向量語法 (Vector Syntax) {#vector-syntax}

`vector` 型別使用 `vector` 關鍵字，後接以角括號包圍的元素型別來表示。元素型別可以是
任何有效的 Move 型別，包括其他向量。

Move 也提供向量字面值語法，讓你能使用 `vector` 關鍵字，後接包含元素的方括號來建立
向量（若要建立空向量，方括號中不放任何元素）。

```move file=packages/samples/sources/move-basics/vector.move anchor=literal

```

`vector` 型別是 Move 的內建型別，不需要從模組匯入。向量操作定義於
[標準函式庫](./standard-library)的 `std::vector` 模組中；該模組會隱式匯入，因此可直接
使用，無須明確的 `use` 陳述式。

> 本節使用點語法呼叫向量函式，例如使用 `v.length()`，而非
> `vector::length(&v)`。這是 _接收者語法_，標準函式庫型別預設即可使用；我們會在
> [結構方法](./struct-methods)章節說明其運作方式。

## 讀取元素 (Reading Elements) {#reading-elements}

對集合最基本的查詢是其大小與元素。`length` 函式會回傳元素數量，`is_empty` 用來判斷
是否沒有元素，而索引語法 `v[i]` 可存取單一元素。索引從零開始，存取超出範圍的索引會
中止執行：

```move file=packages/samples/sources/move-basics/vector.move anchor=access

```

> `v[i]` 語法是呼叫 `borrow` 函式的簡寫——它產生元素的
> [參考](./references)，而非元素本身。對於可複製的型別，例如上方的整數，差異並不明顯；
> 對於無法複製的型別，若要將元素從向量中 _取出_，必須使用下方說明的 `pop_back`、`remove`
> 或 `swap_remove`。此語法的詳細內容請參閱 Move 參考文件中的
> [索引語法](./../../reference/index-syntax)。

## 新增與移除元素 (Adding and Removing Elements) {#adding-and-removing-elements}

可變向量可以擴增與縮減。最有效率的操作作用於向量的 _末端_——`push_back` 與
`pop_back`——而 `insert` 與 `remove` 則作用於任意索引，並會位移其後的所有元素：

```move file=packages/samples/sources/move-basics/vector.move anchor=methods

```

下表列出 `std::vector` 模組最常使用的函式；完整清單請參閱
[模組文件][vector-stdlib]：

<div class="modules-table">

| 函式            | 說明                             | 中止條件         |
| --------------- | -------------------------------- | ---------------- |
| `length`        | 回傳元素數量                     | -                |
| `is_empty`      | 若向量沒有元素則回傳 `true`      | -                |
| `push_back`     | 將元素新增至末端                 | -                |
| `pop_back`      | 移除並回傳最後一個元素           | 向量為空         |
| `insert`        | 在索引處插入元素，並位移其餘元素 | 索引超出範圍     |
| `remove`        | 移除並回傳索引處的元素           | 索引超出範圍     |
| `swap_remove`   | 將元素與最後一個元素交換後移除   | 索引超出範圍     |
| `swap`          | 交換兩個索引處的元素             | 任一索引超出範圍 |
| `contains`      | 若向量包含該元素則回傳 `true`    | -                |
| `index_of`      | 若找到元素則回傳 `(true, index)` | -                |
| `append`        | 將另一個向量的所有元素移至末端   | -                |
| `reverse`       | 反轉元素順序                     | -                |
| `destroy_empty` | 銷毀空向量                       | 向量不為空       |

</div>

> 請注意，`remove` 會位移被移除元素之後的每個元素，因此向量越長，其成本越高。若元素順序
> 不重要，`swap_remove` 可在固定時間內完成相同工作。

## 向量巨集 (Vector Macros) {#vector-macros}

讀取、轉換或彙總向量中的每個元素是很常見的工作，因此標準函式庫為此提供了一組 _巨集_。
巨集名稱以 `!` 結尾，並接受一個 _lambda_（寫成 `|argument| expression` 的內嵌函式），
巨集會將其套用至元素。在底層，巨集會在編譯時展開為一般迴圈，因此在執行階段不會產生
額外成本：

```move file=packages/samples/sources/move-basics/vector.move anchor=macros

```

其他常用巨集包括 `filter!`、`any!`、`all!`、`find_index!` 與 `tabulate!`——它們各自能以
一行具表達力的程式碼取代手寫迴圈。完整清單可見於[模組文件][vector-stdlib]；本章稍後的
[巨集函式](./macros)章節也會介紹巨集的一般用法。

## 銷毀包含不可丟棄型別的向量 (Destroying a Vector of Non-Droppable Types) {#destroying-a-vector-of-non-droppable-types}

`vector` 型別會從其元素繼承[能力](./abilities-introduction)：僅當 `T` 可以
[丟棄](./drop-ability)時，`vector<T>` 才能被丟棄。即使向量為空，不具 `drop` 能力的型別
所組成的向量也不能被忽略；編譯器要求明確呼叫 `destroy_empty` 函式：

```move file=packages/samples/sources/move-basics/vector.move anchor=no_drop

```

若你對非空向量呼叫 `destroy_empty` 函式，它會在執行階段失敗。這正是資源模型的運作方式：
若向量元素代表資產，資產本身與持有它們的向量都不能悄然消失——必須先取出並處理每個元素，
才能銷毀向量本身。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [向量](./../../reference/primitive-types/vector)。
- Move 參考文件中的 [索引語法](./../../reference/index-syntax)。
- Move 參考文件中的 [巨集函式](./../../reference/functions/macros)。
- [std::vector][vector-stdlib] 模組文件。

[vector-stdlib]: https://docs.sui.io/references/framework/std/vector
