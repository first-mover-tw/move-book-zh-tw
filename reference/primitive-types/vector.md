---
title: 向量 (Vector) | 參考手冊
description: Move 向量 (vector) 型別 (type) 參考 (reference)：建立 (create)、存取 (access)、推入 (push)、彈出 (pop)、銷毀 (destroy) 向量 (vectors)，並使用具完整 API 文件 (documentation) 的向量 (vector) 常值 (literals)。
keywords:
  - Move
  - Sui
  - Move reference
  - vector
  - reference
  - collections
questions:
  - How does Vector work in Move?
  - What is the syntax for Vector in Move?
  - What is Literals in Move?
  - What is Operations in Move?
answer: 'Move vector type reference: create, access, push, pop, destroy vectors, and use vector literals with full API documentation.'
goal:
  description: 'Reader understands move vector type reference: create, access, push, pop, destroy vectors, and use vector literals with full API documentation'
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

`vector<T>` 是 Move 提供的唯一原始集合型別。`vector<T>` 是由 `T` 組成的同質集合，可透過在「末端」推入／彈出值來擴張或縮小。

`vector<T>` 可使用任何型別 `T` 進行具現化。例如，`vector<u64>`、`vector<address>`、`vector<0x42::my_module::MyData>` 與 `vector<vector<u8>>` 都是有效的向量型別。

## 字面值 (Literals) {#literals}

### 一般 `vector` 字面值 (General `vector` Literals) {#general-vector-literals}

可使用 `vector` 字面值建立任何型別的向量。

| 語法                  | 型別                                                                        | 說明                                |
| --------------------- | --------------------------------------------------------------------------- | ----------------------------------- |
| `vector[]`            | `vector[]: vector<T>`，其中 `T` 為任一單一非參考型別                        | 空向量                              |
| `vector[e1, ..., en]` | `vector[e1, ..., en]: vector<T>`，其中 `e_i: T`，且 `0 < i <= n` 與 `n > 0` | 包含 `n` 個元素的向量（長度為 `n`） |

在這些情況中，`vector` 的型別會從元素型別或向量的使用方式推斷而得。若無法推斷型別，或只是為了讓內容更清楚，可以明確指定型別：

```move
vector<T>[]: vector<T>
vector<T>[e1, ..., en]: vector<T>
```

#### 向量字面值範例 (Example Vector Literals) {#example-vector-literals}

```move
(vector[]: vector<bool>);
(vector[0u8, 1u8, 2u8]: vector<u8>);
(vector<u128>[]: vector<u128>);
(vector<address>[@0x42, @0x100]: vector<address>);
```

### `vector<u8>` 字面值 (`vector<u8>` literals) {#vectoru8-literals}

Move 中向量的一個常見使用情境是表示「位元組陣列」，其以 `vector<u8>` 表示。這些值通常用於密碼學用途，例如公開金鑰或雜湊結果。這些值十分常見，因此提供了特定語法，讓值更容易閱讀，而不必使用必須以數值形式指定每個個別 `u8` 值的 `vector[]`。

目前支援兩種 `vector<u8>` 字面值：_位元組字串_ 與 _十六進位字串_。

#### 位元組字串 (Byte Strings) {#byte-strings}

位元組字串是以 `b` 為前綴的帶引號字串字面值，例如 `b"Hello!\n"`。

這些是允許跳脫序列的 ASCII 編碼字串。目前支援的跳脫序列如下：

| 跳脫序列 | 說明                                      |
| -------- | ----------------------------------------- |
| `\n`     | 換行（或換行字元）                        |
| `\r`     | 歸位字元                                  |
| `\t`     | 定位字元                                  |
| `\\`     | 反斜線                                    |
| `\0`     | 空字元                                    |
| `\"`     | 引號                                      |
| `\xHH`   | 十六進位跳脫，插入十六進位位元組序列 `HH` |

#### 十六進位字串 (Hex Strings) {#hex-strings}

十六進位字串是以 `x` 為前綴的帶引號字串字面值，例如 `x"48656C6C6F210A"`。

每對範圍從 `00` 到 `FF` 的位元組都會解讀為十六進位編碼的 `u8` 值。因此，每一對位元組都對應結果 `vector<u8>` 中的一個項目。

#### 字串字面值範例 (Example String Literals) {#example-string-literals}

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

## 操作 (Operations) {#operations}

`vector` 透過 Move 標準函式庫中的 `std::vector` 模組支援下列操作：

| 函式                                                       | 說明                                                                                                    | 會中止？               |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------- |
| `vector::empty<T>(): vector<T>`                            | 建立可儲存型別 `T` 值的空向量                                                                           | 永不                   |
| `vector::singleton<T>(t: T): vector<T>`                    | 建立包含 `t`、大小為 1 的向量                                                                           | 永不                   |
| `vector::push_back<T>(v: &mut vector<T>, t: T)`            | 將 `t` 加入 `v` 的末端                                                                                  | 永不                   |
| `vector::pop_back<T>(v: &mut vector<T>): T`                | 移除並回傳 `v` 中的最後一個元素                                                                         | 若 `v` 為空            |
| `vector::borrow<T>(v: &vector<T>, i: u64): &T`             | 回傳索引 `i` 處 `T` 的不可變參考                                                                        | 若 `i` 超出範圍        |
| `vector::borrow_mut<T>(v: &mut vector<T>, i: u64): &mut T` | 回傳索引 `i` 處 `T` 的可變參考                                                                          | 若 `i` 超出範圍        |
| `vector::destroy_empty<T>(v: vector<T>)`                   | 刪除 `v`                                                                                                | 若 `v` 不為空          |
| `vector::append<T>(v1: &mut vector<T>, v2: vector<T>)`     | 將 `v2` 中的元素加入 `v1` 的末端                                                                        | 永不                   |
| `vector::contains<T>(v: &vector<T>, e: &T): bool`          | 若 `e` 位於向量 `v` 中則回傳 true，否則回傳 false                                                       | 永不                   |
| `vector::swap<T>(v: &mut vector<T>, i: u64, j: u64)`       | 交換向量 `v` 中第 `i` 與第 `j` 個索引位置的元素                                                         | 若 `i` 或 `j` 超出範圍 |
| `vector::reverse<T>(v: &mut vector<T>)`                    | 就地反轉向量 `v` 中元素的順序                                                                           | 永不                   |
| `vector::index_of<T>(v: &vector<T>, e: &T): (bool, u64)`   | 若 `e` 位於向量 `v` 的索引 `i` 處，則回傳 `(true, i)`；否則回傳 `(false, 0)`                            | 永不                   |
| `vector::remove<T>(v: &mut vector<T>, i: u64): T`          | 移除向量 `v` 的第 `i` 個元素，並位移所有後續元素。此操作為 O(n)，且會保留向量中的元素順序               | 若 `i` 超出範圍        |
| `vector::swap_remove<T>(v: &mut vector<T>, i: u64): T`     | 將向量 `v` 的第 `i` 個元素與最後一個元素交換，接著彈出該元素。此操作為 O(1)，但不會保留向量中的元素順序 | 若 `i` 超出範圍        |

<!-- TODO：我們是否應該直接連結至產生的標準函式庫文件？或許？  -->

未來可能會加入更多操作。

## 範例 (Example) {#example}

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

## 銷毀與複製 `vector` (Destroying and copying `vector`s) {#destroying-and-copying-vectors}

`vector<T>` 的某些行為取決於元素型別 `T` 的能力。例如，包含不具備 `drop` 能力元素的向量，無法像上述範例中的 `v` 一樣隱含捨棄——必須使用 `vector::destroy_empty` 明確銷毀。

請注意，除非 `vec` 包含零個元素，否則 `vector::destroy_empty` 會在執行階段中止：

```move
fun destroy_any_vector<T>(vec: vector<T>) {
    vector::destroy_empty(vec) // 刪除此行將造成編譯器錯誤
}
```

但捨棄包含具備 `drop` 能力元素的向量時不會發生錯誤：

```move
fun destroy_droppable_vector<T: drop>(vec: vector<T>) {
    // 有效！
    // 不需要明確執行任何操作來銷毀向量
}
```

同樣地，除非元素型別具備 `copy`，否則向量無法複製。換言之，僅當 `T` 具備 `copy` 時，`vector<T>` 才具備 `copy`。請注意，若有需要，它會被隱含複製：

```move
let x = vector[10];
let y = x; // 隱含複製
let z = x;
(y, z)
```

請記住，複製大型向量可能成本高昂。若這是需要考量的問題，為預定的使用方式加上註記可避免意外複製。例如：

```move
let x = vector[10];
let y = move x;
let z = x; // 錯誤！x 已被移動
(y, z)
```

如需更多詳細資訊，請參閱[型別能力](./../abilities)與[泛型](./../generics)章節。

## 所有權 (Ownership) {#ownership}

如[上文](#destroying-and-copying-vectors)所述，只有元素可複製時，`vector` 值才能複製。在此情況下，可透過 [`copy`](./../variables#move-and-copy) 或[解參考 `*`](./references#reading-and-writing-through-references)執行複製。
