---
description: Vectors 向量 (Vectors) in Move：建立動態集合、讀取、新增與移除元素、用向量巨集走訪，以及銷毀不可丟棄型別的向量。
---

# Vector 向量 (Vector) {#vector}

`vector` 是 Move 內建的集合元素儲存方式。它是一種有序、可增長的集合，類似於其他程式語言中的陣列或串列，並且是其他型別的建構區塊：後續章節介紹的 [`Option`](./option) 和 [`String`](./string) 型別都是以 vector 為底層實作。本節將介紹 `vector` 型別、其操作方式，以及讓操作它更方便的巨集。

## Vector 語法 (Vector Syntax) {#vector-syntax}

`vector` 型別的寫法是使用 `vector` 關鍵字，後面接上角括號中元素的型別。元素的型別可以是任何有效的 Move 型別，包括其他 vector。

Move 也有 vector 字面值語法，讓你可以使用 `vector` 關鍵字後面接上包含元素的方括號（空 vector 則不含元素）來建立 vector。

```move file=packages/samples/sources/move-basics/vector.move anchor=literal

```

`vector` 型別是 Move 中的內建型別，不需要從模組匯入。vector 操作是定義在[標準函式庫](./standard-library)的 `std::vector` 模組中，該模組會被隱式匯入，因此可以直接使用而不需要明確的 `use` 陳述式。

> 在本節中，我們使用點語法呼叫 vector 函式，例如使用 `v.length()` 而非 `vector::length(&v)`。這是所謂的**接收者語法（receiver syntax）**，標準函式庫型別開箱即用即可使用此語法；我們會在[結構方法](./struct-methods)一節中說明其運作原理。

## 讀取元素 (Reading Elements) {#reading-elements}

對集合最基本的操作就是詢問它的大小與元素。`length` 函式會回傳元素的數量，`is_empty` 會告訴你集合是否為空，索引語法 `v[i]` 則可以存取單一元素。索引從零開始，存取超出範圍的索引會導致執行中止：

```move file=packages/samples/sources/move-basics/vector.move anchor=access

```

> `v[i]` 語法是呼叫 `borrow` 函式的簡寫——它產生的是該元素的[參考](./references)，而不是元素本身。對於像上面整數這類可複製的型別，這個差異並不明顯；而對於無法複製的型別，要將元素**取出** vector 之外，就需要使用下面說明的 `pop_back`、`remove` 或 `swap_remove`。此語法的細節說明於 Move 參考手冊中的[索引語法](./../../reference/index-syntax)。

## 新增與移除元素 (Adding and Removing Elements) {#adding-and-removing-elements}

可變的 vector 可以增長也可以縮減。最有效率的操作是作用在 vector 的**尾端**——也就是 `push_back` 和 `pop_back`——而 `insert` 和 `remove` 則作用在任意索引位置，並會位移其後所有的元素：

```move file=packages/samples/sources/move-basics/vector.move anchor=methods

```

下表列出 `std::vector` 模組中最常用的函式；完整清單請參閱[模組文件][vector-stdlib]：

<div class="modules-table">

| 函式            | 說明                                   | 何時中止         |
| --------------- | -------------------------------------- | ---------------- |
| `length`        | 回傳元素的數量                         | -                |
| `is_empty`      | vector 沒有元素時回傳 `true`           | -                |
| `push_back`     | 在尾端新增一個元素                     | -                |
| `pop_back`      | 移除並回傳最後一個元素                 | vector 為空      |
| `insert`        | 在該索引處插入一個元素，並位移其餘元素 | 索引超出範圍     |
| `remove`        | 移除並回傳該索引處的元素               | 索引超出範圍     |
| `swap_remove`   | 將該元素與最後一個元素交換後移除       | 索引超出範圍     |
| `swap`          | 交換兩個索引處的元素                   | 某個索引超出範圍 |
| `contains`      | vector 包含該元素時回傳 `true`         | -                |
| `index_of`      | 找到元素時回傳 `(true, index)`         | -                |
| `append`        | 將另一個 vector 的所有元素移動到尾端   | -                |
| `reverse`       | 反轉元素的順序                         | -                |
| `destroy_empty` | 銷毀一個空的 vector                    | vector 不是空的  |

</div>

> 請注意，`remove` 會位移被移除元素之後的每一個元素，因此 vector 越長，成本就越高。如果元素的順序不重要，`swap_remove` 可以在常數時間內完成相同的工作。

## Vector 巨集 (Vector Macros) {#vector-macros}

讀取、轉換或彙總 vector 中的每一個元素是非常常見的任務，因此標準函式庫為此提供了一組**巨集**。巨集的名稱以 `!` 結尾，並接受一個**匿名函式（lambda）**（以 `|argument| expression` 形式撰寫的行內函式），巨集會將其套用到每個元素上。在底層，巨集會在編譯時展開為一般的迴圈，因此使用巨集在執行期不會產生額外成本：

```move file=packages/samples/sources/move-basics/vector.move anchor=macros

```

其他常用的巨集還包括 `filter!`、`any!`、`all!`、`find_index!` 和 `tabulate!`——它們每一個都能用一行富有表達力的程式碼取代手寫的迴圈。完整清單可在[模組文件][vector-stdlib]中找到，而巨集的一般性介紹則在本章稍後的[巨集函式](./macros)一節中說明。

## 銷毀不具備 Drop 能力型別的 Vector (Destroying a Vector of Non-Droppable Types) {#destroying-a-vector-of-non-droppable-types}

`vector` 型別會從其元素繼承[能力](./abilities-introduction)：只有當 `T` 具備 [drop 能力](./drop-ability)時，`vector<T>` 才能被丟棄。不具備 `drop` 能力型別的 vector 無法被忽略，即使它是空的，編譯器也會要求明確呼叫 `destroy_empty` 函式：

```move file=packages/samples/sources/move-basics/vector.move anchor=no_drop

```

如果你對非空的 vector 呼叫 `destroy_empty` 函式，該呼叫會在執行期失敗。這正是資源模型運作的方式：如果 vector 的元素代表資產，那麼無論是資產本身還是承載它們的 vector，都不能悄悄地消失——在 vector 本身被銷毀之前，每一個元素都必須被取出並妥善處理。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[Vector](./../../reference/primitive-types/vector)。
- Move 參考手冊中的[索引語法](./../../reference/index-syntax)。
- Move 參考手冊中的[巨集函式](./../../reference/functions/macros)。
- [std::vector][vector-stdlib] 模組文件。

[vector-stdlib]: https://docs.sui.io/references/framework/std/vector
