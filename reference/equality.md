---
title: 相等性 (Equality) | 參考手冊
description: Move 相等性操作 (Move equality operations) 參考手冊：`==` 和 `!=` 運算子、型別限制，以及值與參考的比較規則。
keywords:
  - Move
  - Sui
  - Move reference
  - equality
  - reference
questions:
  - How does Equality work in Move?
  - What is the syntax for Equality in Move?
  - What is Operations in Move?
  - What is Restrictions in Move?
answer: 'Move equality operations reference: == and != operators, type restrictions, and comparison rules for values and references.'
goal:
  description: 'Reader understands move equality operations reference: == and != operators, type restrictions, and comparison rules for values and references'
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

# 相等性 (Equality) {#equality}

Move 支援兩種相等性運算 `==` 與 `!=`

## 運算 (Operations) {#operations}

| 語法 | 運算   | 說明                                                    |
| ---- | ------ | ------------------------------------------------------- |
| `==` | 相等   | 若兩個運算元具有相同值，則回傳 `true`；否則回傳 `false` |
| `!=` | 不相等 | 若兩個運算元具有不同值，則回傳 `true`；否則回傳 `false` |

### 型別檢查 (Typing) {#typing}

相等（`==`）與不相等（`!=`）運算都僅在兩個運算元為相同型別時才能運作。

```move
0 == 0; // `true`
1u128 == 2u128; // `false`
b"hello" != x"00"; // `true`
```

相等與不相等運算也適用於*所有*使用者自訂型別！

```move
module 0::example;

public struct S has copy, drop { f: u64, s: vector<u8> }

fun always_true(): bool {
    let s = S { f: 0, s: b"" };
    s == s
}

fun always_false(): bool {
    let s = S { f: 0, s: b"" };
    s != s
}
```

若運算元具有不同型別，會發生型別檢查錯誤。

```move
1u8 == 1u128; // 錯誤！
//     ^^^^^ 預期型別為 'u8' 的引數
b"" != 0; // 錯誤！
//     ^ 預期型別為 'vector<u8>' 的引數
```

### 使用參考進行型別檢查 (Typing with references) {#typing-with-references}

比較[參考](./primitive-types/references)時，參考的型別（不可變或可變）並不重要。這表示你可以將不可變的 `&` 參考與具有相同底層型別的可變 `&mut` 參考比較。

```move
let i = &0;
let m = &mut 1;

i == m; // `false`
m == i; // `false`
m == m; // `true`
i == i; // `true`
```

上述內容等同於在需要的位置，對每個可變參考明確套用 freeze。

```move
let i = &0;
let m = &mut 1;

i == freeze(m); // `false`
freeze(m) == i; // `false`
m == m; // `true`
i == i; // `true`
```

但同樣地，底層型別必須相同。

```move
let i = &0;
let s = &b"";

i == s; // 錯誤！
//   ^ 預期型別為 '&u64' 的引數
```

### 自動借用 (Automatic Borrowing) {#automatic-borrowing}

從 Move 2024 版本開始，若其中一個運算元是參考、另一個不是，`==` 與 `!=` 運算子會自動借用其運算元。這表示下列程式碼可在沒有任何錯誤的情況下運作：

```move
let r = &0;

// 在所有情況中，`0` 都會自動借用為 `&0`
r == 0; // `true`
0 == r; // `true`
r != 0; // `false`
0 != r; // `false`
```

此自動借用一律為不可變借用。

## 限制 (Restrictions) {#restrictions}

`==` 與 `!=` 在比較值時都會消耗該值。因此，型別系統會強制要求型別必須具有 [`drop`](./abilities)。請回想，若沒有 [`drop` ability](./abilities)，所有權必須在函式結束前轉移，而此類值只能在其宣告模組內明確銷毀。若直接以此類值搭配相等 `==` 或不相等 `!=` 運算，該值將遭銷毀，進而破壞 [`drop` ability](./abilities) 的安全保證！

```move
module 0::example;

public struct Coin has store { value: u64 }
fun invalid(c1: Coin, c2: Coin) {
    c1 == c2 // 錯誤！
//  ^^    ^^ 這些資產將被銷毀！
}
```

不過，程式設計師*一律*可以先借用值，而非直接比較該值；且參考型別具有 [`drop` ability](./abilities)。例如：

```move
module 0::example;

public struct Coin has store { value: u64 }
fun swap_if_equal(c1: Coin, c2: Coin): (Coin, Coin) {
    let are_equal = &c1 == c2; // 有效，注意 `c2` 會自動借用
    if (are_equal) (c2, c1) else (c1, c2)
}
```

## 避免額外複製 (Avoid Extra Copies) {#avoid-extra-copies}

雖然程式設計師*可以*比較任何型別具有 [`drop`](./abilities) 的值，但通常應透過參考比較，以避免成本高昂的複製。

```move
let v1: vector<u8> = function_that_returns_vector();
let v2: vector<u8> = function_that_returns_vector();
assert!(copy v1 == copy v2, 42);
//      ^^^^       ^^^^
use_two_vectors(v1, v2);

let s1: Foo = function_that_returns_large_struct();
let s2: Foo = function_that_returns_large_struct();
assert!(copy s1 == copy s2, 42);
//      ^^^^       ^^^^
use_two_foos(s1, s2);
```

此程式碼完全可接受（假設 `Foo` 具有 [`drop`](./abilities)），但效率不佳。可移除突顯的複製，並改以借用取代：

```move
let v1: vector<u8> = function_that_returns_vector();
let v2: vector<u8> = function_that_returns_vector();
assert!(&v1 == &v2, 42);
//      ^      ^
use_two_vectors(v1, v2);

let s1: Foo = function_that_returns_large_struct();
let s2: Foo = function_that_returns_large_struct();
assert!(&s1 == &s2, 42);
//      ^      ^
use_two_foos(s1, s2);
```

`==` 本身的效率維持不變，但移除了 `copy`，因此程式會更有效率。
