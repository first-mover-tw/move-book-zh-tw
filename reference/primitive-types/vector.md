---
title: 向量 (Vector) | 參考手冊
description:
  向量型別參考手冊 (Vector Type Reference)：說明如何建立、存取、push、pop、銷毀向量 (vector)，並提供含完整
  API 文件的向量字面值 (vector literal) 用法。
---

# 向量 (Vector)

`vector<T>` 是 Move 中唯一提供的原始集合型別。`vector<T>` 是 `T` 型別的同質集合，可以透過在「末尾」新增 (push) 或彈出 (pop) 值來增長或縮減。

`vector<T>` 可以使用任何型別 `T` 進行實例化。例如，`vector<u64>`、`vector<address>`、`vector<0x42::my_module::MyData>` 和 `vector<vector<u8>>` 都是有效的向量型別。

## 字面量 (Literals)

### 通用 `vector` 字面量 (General `vector` Literals)

任何型別的向量都可以使用 `vector` 字面量建立。

| 語法                  | 型別                                                                       | 描述                                    |
| --------------------- | -------------------------------------------------------------------------- | --------------------------------------- |
| `vector[]`            | `vector[]: vector<T>` 其中 `T` 是任何單一非參考型別                        | 一個空向量                              |
| `vector[e1, ..., en]` | `vector[e1, ..., en]: vector<T>` 其中 `e_i: T` 且 $0 < i \le n$ 且 $n > 0$ | 一個具有 `n` 個元素的向量（長度為 `n`） |

在這些情況下，`vector` 的型別會被推論出來，可以從元素型別推論，也可以從向量的用途推論。如果無法推論型別，或者為了增加清晰度，可以明確指定型別：

```move
vector<T>[]: vector<T>
vector<T>[e1, ..., en]: vector<T>
```

#### 向量字面量範例 (Example Vector Literals)

```move
(vector[]: vector<bool>);
(vector[0u8, 1u8, 2u8]: vector<u8>);
(vector<u128>[]: vector<u128>);
(vector<address>[@0x42, @0x100]: vector<address>);
```

### `vector<u8>` 字面量 (`vector<u8>` literals)

Move 中向量的一個常見用途是表示「位元組陣列 (byte arrays)」，這通常使用 `vector<u8>` 來表示。這些值常用於加密目的，例如公鑰或雜湊結果。這些值非常普遍，因此提供了特殊的語法來使值更具可讀性，而不是必須使用 `vector[]` 並以數字形式指定每個獨立的 `u8` 值。

目前支援兩種型別的 `vector<u8>` 字面量：_位元組字串 (byte strings)_ 和 _十六進位字串 (hex strings)_。

#### 位元組字串 (Byte Strings)

位元組字串是以 `b` 為前綴的引號字串字面量，例如 `b"Hello!\n"`。

這些是 ASCII 編碼的字串，允許轉義序列 (escape sequences)。目前支援的轉義序列有：

| 轉義序列 | 描述                                      |
| -------- | ----------------------------------------- |
| `\n`     | 換行符 (New line 或 Line feed)            |
| `\r`     | 回車符 (Carriage return)                  |
| `\t`     | 製表符 (Tab)                              |
| `\\`     | 反斜線 (Backslash)                        |
| `\0`     | 空字元 (Null)                             |
| `\"`     | 引號 (Quote)                              |
| `\xHH`   | 十六進位轉義，插入十六進位位元組序列 `HH` |

#### 十六進位字串 (Hex Strings)

十六進位字串是以 `x` 為前綴的引號字串字面量，例如 `x"48656C6C6F210A"`。

每對位元組（範圍從 `00` 到 `FF`）都被解釋為十六進位編碼的 `u8` 值。因此，每對位元組對應於結果 `vector<u8>` 中的一個條目。

#### 字串字面量範例 (Example String Literals)

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

## 操作 (Operations)

`vector` 透過 Move 標準庫中的 `std::vector` 模組支援以下操作：

| 函式                                                       | 描述                                                                                             | 是否中斷 (Aborts)?   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------- |
| `vector::empty<T>(): vector<T>`                            | 建立一個可以儲存 `T` 型別值的空向量                                                              | 永不                 |
| `vector::singleton<T>(t: T): vector<T>`                    | 建立一個大小為 1 且包含 `t` 的向量                                                               | 永不                 |
| `vector::push_back<T>(v: &mut vector<T>, t: T)`            | 將 `t` 新增到 `v` 的末尾                                                                         | 永不                 |
| `vector::pop_back<T>(v: &mut vector<T>): T`                | 移除並回傳 `v` 中的最後一個元素                                                                  | 如果 `v` 為空        |
| `vector::borrow<T>(v: &vector<T>, i: u64): &T`             | 回傳索引 `i` 處 `T` 的不可變參考                                                                 | 如果 `i` 越界        |
| `vector::borrow_mut<T>(v: &mut vector<T>, i: u64): &mut T` | 回傳索引 `i` 處 `T` 的可變參考                                                                   | 如果 `i` 越界        |
| `vector::destroy_empty<T>(v: vector<T>)`                   | 刪除 `v`                                                                                         | 如果 `v` 不為空      |
| `vector::append<T>(v1: &mut vector<T>, v2: vector<T>)`     | 將 `v2` 中的元素新增到 `v1` 的末尾                                                               | 永不                 |
| `vector::contains<T>(v: &vector<T>, e: &T): bool`          | 如果 `e` 在向量 `v` 中則回傳 true。否則回傳 false                                                | 永不                 |
| `vector::swap<T>(v: &mut vector<T>, i: u64, j: u64)`       | 交換向量 `v` 中第 `i` 和第 `j` 個索引處的元素                                                    | 如果 `i` 或 `j` 越界 |
| `vector::reverse<T>(v: &mut vector<T>)`                    | 原地 (In place) 反轉向量 `v` 中元素的順序                                                        | 永不                 |
| `vector::index_of<T>(v: &vector<T>, e: &T): (bool, u64)`   | 如果 `e` 在向量 `v` 的索引 `i` 處則回傳 `(true, i)`。否則回傳 `(false, 0)`                       | 永不                 |
| `vector::remove<T>(v: &mut vector<T>, i: u64): T`          | 移除向量 `v` 的第 `i` 個元素，並平移後續所有元素。這是 O(n) 操作，並保留元素順序                 | 如果 `i` 越界        |
| `vector::swap_remove<T>(v: &mut vector<T>, i: u64): T`     | 將向量 `v` 的第 `i` 個元素與最後一個元素交換，然後彈出該元素。這是 O(1) 操作，但不會保留元素順序 | 如果 `i` 越界        |

<!-- TODO 我們是否應該直接連結到產生的標準庫文件？也許吧？ -->

隨著時間推移可能會新增更多操作。

## 範例 (Example)

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

## 銷毀與複製向量 (Destroying and copying `vector`s)

`vector<T>` 的某些行為取決於元素型別 `T` 的[能力 (abilities)](./../abilities)。例如，包含不具備 `drop` 能力元素的向量無法像上述範例中的 `v` 那樣被隱式捨棄——它們必須使用 `vector::destroy_empty` 明確銷毀。

請注意，除非 `vec` 包含零個元素，否則 `vector::destroy_empty` 會在執行時中斷：

```move
fun destroy_any_vector<T>(vec: vector<T>) {
    vector::destroy_empty(vec) // 刪除此行將導致編譯錯誤
}
```

但對於捨棄包含具備 `drop` 能力元素的向量，則不會發生錯誤：

```move
fun destroy_droppable_vector<T: drop>(vec: vector<T>) {
    // 有效！
    // 不需要採取任何明確行動來銷毀向量
}
```

同樣地，除非元素型別具備 `copy` 能力，否則向量無法被複製。換句話說，當且僅當 `T` 具備 `copy` 時，`vector<T>` 才具備 `copy` 能力。請注意，如果需要，它將被隱式複製：

```move
let x = vector[10];
let y = x; // 隱式複製
let z = x;
(y, z)
```

請記住，複製大型向量可能代價高昂。如果這是個顧慮，標註預期的用法可以防止意外複製。例如：

```move
let x = vector[10];
let y = move x;
let z = x; // 錯誤！x 已被轉移 (moved)
(y, z)
```

欲了解更多詳情，請參見[型別能力](./../abilities)與[泛型](./../generics)章節。

## 所有權 (Ownership)

如[上文](#銷毀與複製向量-destroying-and-copying-vectors)所述，唯有當元素可以複製時，`vector` 值才能被複製。在這種情況下，可以透過 [`copy`](./../variables#move-and-copy) 或[解參考 `*`](./references#reading-and-writing-through-references) 進行複製。
