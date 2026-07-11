---
title: 向量 (Vector) | 參考手冊
description:
  向量型別參考手冊 (Vector Type Reference)：說明如何建立、存取、push、pop、銷毀向量 (vector)，並提供含完整
  API 文件的向量字面值 (vector literal) 用法。
---

# 向量 (Vector)

`vector<T>` 是 Move 提供的唯一原生集合類型。`vector<T>` 是由 `T` 型別組成的同質 (homogeneous) 集合，可以透過在「末端」推入/彈出數值來增長或縮減。

`vector<T>` 可以使用任何類型 `T` 進行實例化。例如，`vector<u64>`、`vector<address>`、`vector<0x42::my_module::MyData>` 和 `vector<vector<u8>>` 都是有效的向量類型。

## 常值 (Literals)

### 通用 `vector` 常值

可以使用 `vector` 常值建立任何類型的向量。

| 語法                  | 類型                                                                       | 描述                                |
| --------------------- | -------------------------------------------------------------------------- | ----------------------------------- |
| `vector[]`            | `vector[]: vector<T>`，其中 `T` 是任何單一非引用類型                       | 空向量                              |
| `vector[e1, ..., en]` | `vector[e1, ..., en]: vector<T>`，其中 `e_i: T` 且 `0 < i <= n` 且 `n > 0` | 具有 `n` 個元素的向量（長度為 `n`） |

在這些情況下，`vector` 的類型是推斷出來的，要麼從元素類型推斷，要麼從向量的使用方式推斷。如果無法推斷類型，或者僅為了增加清晰度，可以明確指定類型：

```move
vector<T>[]: vector<T>
vector<T>[e1, ..., en]: vector<T>
```

#### 向量常值範例

```move
(vector[]: vector<bool>);
(vector[0u8, 1u8, 2u8]: vector<u8>);
(vector<u128>[]: vector<u128>);
(vector<address>[@0x42, @0x100]: vector<address>);
```

### `vector<u8>` 常值

Move 中向量的一個常見用法是表示「位元組陣列 (byte arrays)」，以 `vector<u8>` 表示。這些數值通常用於加密目的，例如公鑰或雜湊結果。這些數值非常常見，因此提供了特定語法使其更具可讀性，而不必使用 `vector[]` 並以數字形式指定每個單獨的 `u8` 數值。

目前支援兩種類型的 `vector<u8>` 常值：_位元組字串 (byte strings)_ 和 _十六進制字串 (hex strings)_。

#### 位元組字串 (Byte Strings)

位元組字串是以 `b` 為前綴的帶引號字串常值，例如 `b"Hello!\n"`。

這些是 ASCII 編碼的字串，允許轉義序列 (escape sequences)。目前支援的轉義序列為：

| 轉義序列 | 描述                                      |
| -------- | ----------------------------------------- |
| `\n`     | 換行 (New line 或 Line feed)              |
| `\r`     | 回車 (Carriage return)                    |
| `\t`     | 製表符 (Tab)                              |
| `\\`     | 反斜線 (Backslash)                        |
| `\0`     | 空字元 (Null)                             |
| `\"`     | 引號 (Quote)                              |
| `\xHH`   | 十六進制轉義，插入十六進制位元組序列 `HH` |

#### 十六進制字串 (Hex Strings)

十六進制字串是以 `x` 為前綴的帶引號字串常值，例如 `x"48656C6C6F210A"`。

每對位元組（範圍從 `00` 到 `FF`）都被解釋為十六進制編碼的 `u8` 數值。因此，每對位元組對應於結果 `vector<u8>` 中的單個項目。

#### 字串常值範例

```move
fun byte_and_hex_strings() {
    assert!(b"" == x"", 0);
    assert!(b"Hello!\n" == x"48656C6C6F210A", 1);
    assert!(b"\x48\x65\x6C\x6C\x6F\x21\x0A" == x"48656C6C6F210A", 2);
    assert!(
        b"\"Hello\tworld!\"\n \r \\Null=\0" ==
            x"2248656C6C6F09776F726C6421220A200D205C4E756C6C3D00",
        3
    );
}
```

## 操作

`vector` 透過 Move 標準函數庫中的 `std::vector` 模組支援以下操作：

| 函式                                                       | 描述                                                                                           | 是否終止 (Aborts?)       |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------ |
| `vector::empty<T>(): vector<T>`                            | 建立一個可以存儲 `T` 類型數值的空向量                                                          | 永不                     |
| `vector::singleton<T>(t: T): vector<T>`                    | 建立一個長度為 1 且包含 `t` 的向量                                                             | 永不                     |
| `vector::push_back<T>(v: &mut vector<T>, t: T)`            | 將 `t` 添加到 `v` 的末端                                                                       | 永不                     |
| `vector::pop_back<T>(v: &mut vector<T>): T`                | 移除並回傳 `v` 中的最後一個元素                                                                | 如果 `v` 為空            |
| `vector::borrow<T>(v: &vector<T>, i: u64): &T`             | 回傳索引 `i` 處 `T` 的不可變引用                                                               | 如果 `i` 超出範圍        |
| `vector::borrow_mut<T>(v: &mut vector<T>, i: u64): &mut T` | 回傳索引 `i` 處 `T` 的可變引用                                                                 | 如果 `i` 超出範圍        |
| `vector::destroy_empty<T>(v: vector<T>)`                   | 刪除 `v`                                                                                       | 如果 `v` 不為空          |
| `vector::append<T>(v1: &mut vector<T>, v2: vector<T>)`     | 將 `v2` 中的元素添加到 `v1` 的末端                                                             | 永不                     |
| `vector::contains<T>(v: &vector<T>, e: &T): bool`          | 如果 `e` 在向量 `v` 中，則回傳 true。否則回傳 false                                            | 永不                     |
| `vector::swap<T>(v: &mut vector<T>, i: u64, j: u64)`       | 交換向量 `v` 中索引為 `i` 和 `j` 的元素                                                        | 如果 `i` 或 `j` 超出範圍 |
| `vector::reverse<T>(v: &mut vector<T>)`                    | 就地 (in place) 反轉向量 `v` 中元素的順序                                                      | 永不                     |
| `vector::index_of<T>(v: &vector<T>, e: &T): (bool, u64)`   | 如果 `e` 在向量 `v` 的索引 `i` 處，則回傳 `(true, i)`。否則回傳 `(false, 0)`                   | 永不                     |
| `vector::remove<T>(v: &mut vector<T>, i: u64): T`          | 移除向量 `v` 的第 `i` 個元素，位移所有後續元素。這是 O(n) 操作並保持元素順序                   | 如果 `i` 超出範圍        |
| `vector::swap_remove<T>(v: &mut vector<T>, i: u64): T`     | 將向量 `v` 的第 `i` 個元素與最後一個元素交換，然後彈出該元素。這是 O(1) 操作，但不保持元素順序 | 如果 `i` 超出範圍        |

<!-- TODO we should just link out to generated stdlib docs? Maybe?  -->

隨著時間的推動，可能會添加更多操作。

## 範例

```move
use std::vector;

let mut v = vector::empty<u64>();
vector::push_back(&mut v, 5);
vector::push_back(&mut v, 6);

assert!(*vector::borrow(&v, 0) == 5, 42);
assert!(*vector::borrow(&v, 1) == 6, 42);
assert!(vector::pop_back(&mut v) == 6, 42);
assert!(vector::pop_back(&mut v) == 5, 42);
```

## 銷毀和複製向量

`vector<T>` 的某些行為取決於元素類型 `T` 的能力。例如，包含不具備 `drop` 能力元素的向量不能像上面範例中的 `v` 那樣隱式丟棄 —— 它們必須使用 `vector::destroy_empty` 明確銷毀。

請注意，`vector::destroy_empty` 會在執行階段終止，除非 `vec` 包含零個元素：

```move
fun destroy_any_vector<T>(vec: vector<T>) {
    vector::destroy_empty(vec) // 刪除此行將導致編譯錯誤
}
```

但丟棄包含具備 `drop` 能力元素的向量不會發生錯誤：

```move
fun destroy_droppable_vector<T: drop>(vec: vector<T>) {
    // 有效！
    // 不需要進行任何明確操作來銷毀向量
}
```

同樣地，除非元素類型具有 `copy` 能力，否則無法複製向量。換句話說，當且僅當 `T` 具有 `copy` 時，`vector<T>` 才具有 `copy`。請注意，如果需要，它將被隱式複製：

```move
let x = vector[10];
let y = x; // 隱式複製
let z = x;
(y, z)
```

請記住，複製大型向量可能非常昂貴。如果這是個問題，註解 `intended` 用法可以防止意外複製。例如：

```move
let x = vector[10];
let y = move x;
let z = x; // 錯誤！x 已被移動
(y, z)
```

更多詳細資訊請參見 [類型能力](./../abilities) 和 [泛型](./../generics) 章節。

## 所有權 (Ownership)

如 [上文](#銷毀和複製向量) 所述，只有在元素可複製的情況下才能複製 `vector` 數值。在這種情況下，可以透過 [`copy`](./../variables#move-and-copy) 或 [解引用 `*`](./references#reading-and-writing-through-references) 來完成複製。
