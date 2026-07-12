---
title: 等式 (Equality) | Reference
description: Move 相等運算 (Move Equality Operations) 參考手冊：== 與 != 運算子、型別限制，以及數值與參考的比較規則。
---

# 相等性 (Equality)

Move 支援兩種相等性運算：`==` 和 `!=`

## 運算 (Operations)

| 語法 | 運算               | 描述                                                    |
| ---- | ------------------ | ------------------------------------------------------- |
| `==` | 等於 (equal)       | 如果兩個運算元的值相同，則傳回 `true`，否則傳回 `false` |
| `!=` | 不等於 (not equal) | 如果兩個運算元的值不同，則傳回 `true`，否則傳回 `false` |

### 型別檢查 (Typing)

等於 (`==`) 和不等於 (`!=`) 運算只有在兩個運算元型別相同時才能運作。

```move
0 == 0; // `true`
1u128 == 2u128; // `false`
b"hello" != x"00"; // `true`
```

相等性和不相等性也適用於 _所有_ 使用者定義的型別！

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

如果運算元的型別不同，則會出現型別檢查錯誤：

```move
1u8 == 1u128; // 錯誤！
//     ^^^^^ 預期型別為 'u8' 的參數
b"" != 0; // 錯誤！
//     ^ 預期型別為 'vector<u8>' 的參數
```

### 參考的型別檢查 (Typing with references)

在比較 [參考](./primitive-types/references) 時，參考的型別（不可變或可變）並不重要。這意味著你可以將同一個底層型別的不可變 `&` 參考與可變 `&mut` 參考進行比較。

```move
let i = &0;
let m = &mut 1;

i == m; // `false`
m == i; // `false`
m == m; // `true`
i == i; // `true`
```

上述程式碼等同於在需要的地方對每個可變參考套用顯式的凍結（freeze）：

```move
let i = &0;
let m = &mut 1;

i == freeze(m); // `false`
freeze(m) == i; // `false`
m == m; // `true`
i == i; // `true`
```

但同樣地，底層型別必須是相同的型別：

```move
let i = &0;
let s = &b"";

i == s; // 錯誤！
//   ^ 預期型別為 '&u64' 的參數
```

### 自動借用 (Automatic Borrowing)

從 Move 2024 版本開始，如果其中一個運算元是參考而另一個不是，`==` 和 `!=` 運算子會自動借用該運算元。這意味著以下程式碼可以正常運作且不會報錯：

```move
let r = &0;

// 在所有情況下，`0` 都會被自動借用為 `&0`
r == 0; // `true`
0 == r; // `true`
r != 0; // `false`
0 != r; // `false`
```

這種自動借用始終是不可變借用。

## 限制 (Restrictions)

`==` 和 `!=` 在比較時都會消耗值。因此，型別系統要求該型別必須具備 [`drop`](./abilities) 能力。請回想一下，如果不具備 [`drop` 能力](./abilities)，所有權必須在函式結束前轉移，且此類值只能在定義它們的模組內部被顯式銷毀。如果直接將這些值用於相等性 `==` 或不相等性 `!=` 比較，該值將被銷毀，這會違反 [`drop` 能力](./abilities) 的安全保證！

```move
module 0::example;

public struct Coin has store { value: u64 }
fun invalid(c1: Coin, c2: Coin) {
    c1 == c2 // 錯誤！
//  ^^    ^^ 這些資產會被銷毀！
}
```

但是，程式設計師 _總是_ 可以先借用該值而不是直接比較值，且參考型別具備 [`drop` 能力](./abilities)。例如：

```move
module 0::example;

public struct Coin has store { value: u64 }
fun swap_if_equal(c1: Coin, c2: Coin): (Coin, Coin) {
    let are_equal = &c1 == c2; // 有效，注意 `c2` 會被自動借用
    if (are_equal) (c2, c1) else (c1, c2)
}
```

## 避免額外的複製 (Avoid Extra Copies)

雖然程式設計師 _可以_ 比較任何具備 [`drop`](./abilities) 能力的型別的任何值，但通常應該透過參考進行比較，以避免代價高昂的複製。

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

這段程式碼是完全可以接受的（假設 `Foo` 具備 [`drop`](./abilities) 能力），只是效率不高。標註的複製可以被移除並替換為借用：

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

`==` 本身的效率保持不變，但移除了 `copy`，因此程式效率更高。
