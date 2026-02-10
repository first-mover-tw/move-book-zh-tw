---
title: '等式 (Equality) | Reference'
description: "Move 等式操作參考：== 和 != 運算子、型別限制，以及值與參考的比較規則。"
---

# 等式 (Equality)

Move 支援兩個等式操作 `==` 和 `!=`

## 操作

| 語法 | 操作 | 說明 |
| ------ | --------- | --------------------------------------------------------------------------- |
| `==`   | 等於 | 如果兩個運算元具有相同的值，則返回 `true`，否則返回 `false` |
| `!=`   | 不等於 | 如果兩個運算元具有不同的值，則返回 `true`，否則返回 `false` |

### 型別

等式 (`==`) 和不等式 (`!=`) 操作只有在兩個運算元的型別相同時才有效

```move
0 == 0; // `true`
1u128 == 2u128; // `false`
b"hello" != x"00"; // `true`
```

等式和不等式也可以在 **所有** 使用者定義型別上運作！

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

如果運算元具有不同的型別，則會出現型別檢查錯誤

```move
1u8 == 1u128; // 錯誤！
//     ^^^^^ 預期型別為 'u8' 的引數
b"" != 0; // 錯誤！
//     ^ 預期型別為 'vector<u8>' 的引數
```

### 參考的型別

比較[參考](./primitive-types/references)時，參考的型別（不可變或可變）不重要。這意味著您可以將不可變 `&` 參考與相同基礎型別的可變參考 `&mut` 進行比較。

```move
let i = &0;
let m = &mut 1;

i == m; // `false`
m == i; // `false`
m == m; // `true`
i == i; // `true`
```

上述等同於在需要時對每個可變參考應用顯式凍結

```move
let i = &0;
let m = &mut 1;

i == freeze(m); // `false`
freeze(m) == i; // `false`
m == m; // `true`
i == i; // `true`
```

但基礎型別必須是相同型別

```move
let i = &0;
let s = &b"";

i == s; // 錯誤！
//   ^ 預期型別為 '&u64' 的引數
```

### 自動借用

從 Move 2024 版本開始，`==` 和 `!=` 運算子如果其中一個運算元是參考而另一個不是，則會自動借用它們的運算元。這意味著以下程式碼可以無錯誤地執行：

```move
let r = &0;

// 在所有情況下，`0` 都會自動借用為 `&0`
r == 0; // `true`
0 == r; // `true`
r != 0; // `false`
0 != r; // `false`
```

此自動借用始終是不可變借用。

## 限制

`==` 和 `!=` 在比較時都會消耗值。因此，型別系統強制要求該型別必須具有 [`drop`](./abilities) 能力。回想一下，沒有 [`drop` 能力](./abilities)，所有權必須在函式結束時轉移，這類值只能在其宣告模組內明確銷毀。如果這些值直接與 `==` 或 `!=` 一起使用，該值將被銷毀，這將破壞 [`drop` 能力](./abilities)安全保證！

```move
module 0::example;

public struct Coin has store { value: u64 }
fun invalid(c1: Coin, c2: Coin) {
    c1 == c2 // 錯誤！
//  ^^    ^^ 這些資產將被銷毀！
}
```

但是，程式設計師 **總是** 可以先借用該值而不是直接比較該值，而參考型別具有 [`drop` 能力](./abilities)。例如

```move
module 0::example;

public struct Coin has store { value: u64 }
fun swap_if_equal(c1: Coin, c2: Coin): (Coin, Coin) {
    let are_equal = &c1 == c2; // 有效，注意 `c2` 會自動借用
    if (are_equal) (c2, c1) else (c1, c2)
}
```

## 避免額外複製

雖然程式設計師 **可以** 比較任何具有 [`drop` 能力](./abilities)的型別的值，但程式設計師應常常通過參考進行比較以避免昂貴的複製。

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

此程式碼完全可以接受（假設 `Foo` 具有 [`drop` 能力](./abilities)），但效率不高。突出顯示的複製可以移除並用借用替換

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

`==` 本身的效率保持相同，但移除了 `copy`，因此程式更有效率。
