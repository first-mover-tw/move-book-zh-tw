---
title: '導入與別名 (Uses and Aliases) | 參考手冊'
description: "Move 導入與別名參考手冊：導入模組、建立別名、分組導入以及解決命名衝突。"
---

# 導入與別名 (Uses and Aliases)

`use` 語法可用於為其他模組中的成員建立別名。`use` 可用於建立持續整個模組或給定表達式區塊作用域的別名。

## 語法

`use` 有多種不同的語句情況。從最簡單的開始，我們有以下用於為其他模組建立別名的語法：

```move
use <address>::<module name>;
use <address>::<module name> as <module alias name>;
```

例如：

```move
use std::vector;
use std::option as o;
```

`use std::vector;` 為 `std::vector` 引入了一個別名 `vector`。這意味著在任何您想使用模組名稱 `std::vector` 的地方（假設此 `use` 在作用域內），您都可以改用 `vector`。`use std::vector;` 等同於 `use std::vector as vector;`。

同樣地，`use std::option as o;` 會讓您使用 `o` 代替 `std::option`。

```move
use std::vector;
use std::option as o;

fun new_vec(): vector<o::Option<u8>> {
    let mut v = vector[];
    vector::push_back(&mut v, o::some(0));
    vector::push_back(&mut v, o::none());
    v
}
```

如果您想導入特定的模組成員（如函式或結構體），可以使用以下語法：

```move
use <address>::<module name>::<module member>;
use <address>::<module name>::<module member> as <member alias>;
```

例如：

```move
use std::vector::push_back;
use std::option::some as s;
```

這將讓您使用函式 `std::vector::push_back` 而無需完整路徑。同樣地，對於 `std::option::some` 可以使用 `s`。相反地，您可以分別使用 `push_back` 和 `s`。同樣，`use std::vector::push_back;` 等同於 `use std::vector::push_back as push_back;`。

```move
use std::vector::push_back;
use std::option::some as s;

fun new_vec(): vector<std::option::Option<u8>> {
    let mut v = vector[];
    vector::push_back(&mut v, s(0));
    vector::push_back(&mut v, std::option::none());
    v
}
```

### 多個別名

如果您想一次為多個模組成員添加別名，可以使用以下語法：

```move
use <address>::<module name>::{<module member>, <module member> as <member alias> ... };
```

例如：

```move
use std::vector::push_back;
use std::option::{some as s, none as n};

fun new_vec(): vector<std::option::Option<u8>> {
    let mut v = vector[];
    push_back(&mut v, s(0));
    push_back(&mut v, n());
    v
}
```

### Self 別名

如果您除了模組成員外還需要為模組本身添加別名，可以在單次 `use` 中使用 `Self`。`Self` 是一種成員，指代模組本身。

```move
use std::option::{Self, some, none};
```

為了清晰起見，以下內容都是等效的：

```move
use std::option;
use std::option as option;
use std::option::Self;
use std::option::Self as option;
use std::option::{Self};
use std::option::{Self as option};
```

### 同一定義的多個別名

如果需要，您可以為任何項目設定任意數量的別名：

```move
use std::vector::push_back;
use std::option::{Option, some, none};

fun new_vec(): vector<Option<u8>> {
    let mut v = vector[];
    push_back(&mut v, some(0));
    push_back(&mut v, none());
    v
}
```

### 巢狀導入

在 Move 中，您還可以在同一個 `use` 宣告中導入多個名稱。這會將所有提供的名稱引入作用域：

```move
use std::{
    vector::{Self as vec, push_back},
    string::{String, Self as str}
};

fun example(s: &mut String) {
    let mut v = vec::empty();
    push_back(&mut v, 0);
    push_back(&mut v, 10);
    str::append_utf8(s, v);
}
```

## 在 `module` 內部

在 `module` 內部，所有 `use` 宣告無論宣告順序如何都是可用的。

```move
module a::example;

use std::vector;

fun new_vec(): vector<Option<u8>> {
    let mut v = vector[];
    vector::push_back(&mut v, 0);
    vector::push_back(&mut v, 10);
    v
}

use std::option::{Option, some, none};
```

模組中宣告的 `use` 別名在該模組內可用。

此外，引入的別名不能與其他模組成件衝突。詳情請參閱 [唯一性](#唯一性)。

## 在表達式內部

您可以在任何表達式區塊的開頭添加 `use` 宣告：

```move
module a::example;

fun new_vec(): vector<Option<u8>> {
    use std::vector::push_back;
    use std::option::{Option, some, none};

    let mut v = vector[];
    push_back(&mut v, some(0));
    push_back(&mut v, none());
    v
}
```

與 `let` 一樣，表達式區塊中 `use` 引入的別名在該區塊結束時會被移除。

```move
module a::example;

fun new_vec(): vector<Option<u8>> {
    let result = {
        use std::vector::push_back;
        use std::option::{Option, some, none};

        let mut v = vector[];
        push_back(&mut v, some(0));
        push_back(&mut v, none());
        v
    };
    result
}
```

嘗試在區塊結束後使用該別名將導致錯誤：

```move
fun new_vec(): vector<Option<u8>> {
    let mut result = {
        use std::vector::push_back;
        use std::option::{Option, some, none};

        let mut v = vector[];
        push_back(&mut v, some(0));
        v
    };
    push_back(&mut result, std::option::none());
    // ^^^^^^ 錯誤！未綁定的函式 'push_back'
    result
}
```

任何 `use` 必須是區塊中的第一項。如果 `use` 出現在任何表達式或 `let` 之後，將導致解析錯誤：

```move
{
    let mut v = vector[];
    use std::vector; // 錯誤！
}
```

這允許您在許多情況下縮短導入區塊。請注意，與之前的導入一樣，這些導入都受以下各節所述的命名和唯一性規則約束。

## 命名規則

別名必須遵循與其他模組成員相同的規則。這意味著結構體（和常數）的別名必須以 `A` 到 `Z` 開頭。

```move
module a::data {
    public struct S {}
    const FLAG: bool = false;
    public fun foo() {}
}
module a::example {
    use a::data::{
        S as s, // 錯誤！
        FLAG as fLAG, // 錯誤！
        foo as FOO,  // 有效
        foo as bar, // 有效
    };
}
```

## 唯一性

在給定的作用域內，由 `use` 宣告引入的所有別名必須是唯一的。

對於模組來說，這意味著 `use` 引入的別名不能重疊：

```move
module a::example;

use std::option::{none as foo, some as foo}; // 錯誤！
//                                     ^^^ 重複的 'foo'

use std::option::none as bar;

use std::option::some as bar; // 錯誤！
//                       ^^^ 重複的 'bar'
```

並且，它們不能與模組的其他成員重疊：

```move
module a::data {
    public struct S {}
}

module example {
    use a::data::S;

    public struct S { value: u64 } // 錯誤！
    //            ^ 與上方的別名 'S' 衝突
}
```

在表達式區塊內，它們不能互相重疊，但可以 [遮蔽 (shadow)](#遮蔽) 來自外部作用域的其他別名或名稱。

## 遮蔽 (Shadowing)

表達式區塊內部的 `use` 別名可以遮蔽來自外部作用域的名稱（模組成員或別名）。與區域變數的遮蔽一樣，遮蔽在表達式區塊結束時結束。

```move
module a::example;

public struct WrappedVector { vec: vector<u64> }

public fun empty(): WrappedVector {
    WrappedVector { vec: std::vector::empty() }
}

public fun push_back(v: &mut WrappedVector, value: u64) {
    std::vector::push_back(&mut v.vec, value);
}

fun example1(): WrappedVector {
    use std::vector::push_back;
    // 'push_back' 現在指代 std::vector::push_back
    let mut vec = vector[];
    push_back(&mut vec, 0);
    push_back(&mut vec, 1);
    push_back(&mut vec, 10);
    WrappedVector { vec }
}

fun example2(): WrappedVector {
    let vec = {
        use std::vector::push_back;
        // 'push_back' 現在指代 std::vector::push_back

        let mut v = vector[];
        push_back(&mut v, 0);
        push_back(&mut v, 1);
        v
    };
    // 'push_back' 現在指代 Self::push_back
    let mut res = WrappedVector { vec };
    push_back(&mut res, 10);
    res
}
```

## 未使用的導入或別名

未使用的 `use` 將導致警告：

```move
module a::example;

use std::option::{some, none}; // 警告！
//                      ^^^^ 未使用的別名 'none'

public fun example(): std::option::Option<u8> {
    some(0)
}
```
