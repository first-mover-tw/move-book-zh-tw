---
title: 導入與別名 (Uses and Aliases) | 參考手冊
description: 使用 Move 的 use 和別名參考手冊：匯入模組、建立別名、群組匯入、解決命名衝突。
---

# 使用與別名 (Uses and Aliases)

`use` 語法可以用於為其他模組中的成員建立別名。`use` 可以用來建立持續整個模組或特定運算式區塊作用域的別名。

## 語法 (Syntax)

`use` 有幾種不同的語法情況。從最簡單的開始，我們有以下用於建立其他模組別名的語法：

```move
use <address>::<module name>;
use <address>::<module name> as <module alias name>;
```

例如：

```move
use std::vector;
use std::option as o;
```

`use std::vector;` 引入了 `std::vector` 的別名 `vector`。這意味著在任何你想使用模組名稱 `std::vector` 的地方（假設此 `use` 在作用域內），你都可以改用 `vector`。`use std::vector;` 等同於 `use std::vector as vector;`。

同樣地，`use std::option as o;` 會讓你使用 `o` 而不是 `std::option`。

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

如果你想匯入特定的模組成員（如函式或結構體），可以使用以下語法：

```move
use <address>::<module name>::<module member>;
use <address>::<module name>::<module member> as <member alias>;
```

例如：

```move
use std::vector::push_back;
use std::option::some as s;
```

這會讓你直接使用函式 `std::vector::push_back` 而無需完整限定名。同樣地，對於 `std::option::some` 可以使用 `s`。相反地，你可以分別使用 `push_back` 和 `s`。再次強調，`use std::vector::push_back;` 等同於 `use std::vector::push_back as push_back;`。

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

### 多重別名 (Multiple Aliases)

如果你想一次性為多個模組成員新增別名，可以使用以下語法：

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

### Self 別名 (Self aliases)

如果你除了模組成員外，還需要為模組本身新增別名，可以在單個 `use` 中使用 `Self`。`Self` 是一種指向模組本身的特殊成員。

```move
use std::option::{Self, some, none};
```

為了清晰起見，以下所有寫法都是等效的：

```move
use std::option;
use std::option as option;
use std::option::Self;
use std::option::Self as option;
use std::option::{Self};
use std::option::{Self as option};
```

### 為同一定義設定多重別名 (Multiple Aliases for the Same Definition)

如果需要，你可以為任何項目設定不限數量的別名：

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

### 巢狀匯入 (Nested imports)

在 Move 中，你也可以在同一個 `use` 宣告中匯入多個名稱。這會將所有提供的名稱引入作用域：

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

## 在 `module` 內部 (Inside a `module`)

在 `module` 內部，所有 `use` 宣告不論宣告順序如何均可使用。

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

在模組中透過 `use` 宣告的別名可於該模組內使用。

此外，引入的別名不能與其他模組成員衝突。詳情請參見[唯一性](#唯一性-uniqueness)。

## 在運算式內部 (Inside an expression)

你可以將 `use` 宣告新增到任何運算式區塊的開頭：

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

與 `let` 一樣，在運算式區塊中由 `use` 引入的別名會在該區塊結束時移除。

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

嘗試在區塊結束後使用別名將導致錯誤：

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
    // ^^^^^^ 錯誤！未繫結的函式 'push_back'
    result
}
```

任何 `use` 必須是區塊中的首個項目。如果 `use` 出現在任何運算式或 `let` 之後，將導致解析錯誤：

```move
{
    let mut v = vector[];
    use std::vector; // 錯誤！
}
```

這讓你在許多情況下可以縮短匯入區塊。請注意，這些匯入與之前的匯入一樣，都受後續章節描述的命名和唯一性規則約束。

## 命名規則 (Naming rules)

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

## 唯一性 (Uniqueness)

在給定的作用域內，所有由 `use` 宣告引入的別名必須是唯一的。

對於模組而言，這意味著由 `use` 引入的別名不能重疊：

```move
module a::example;

use std::option::{none as foo, some as foo}; // 錯誤！
//                                     ^^^ 重複的 'foo'

use std::option::none as bar;

use std::option::some as bar; // 錯誤！
//                       ^^^ 重複的 'bar'
```

而且，它們不能與模組的其他成員重疊：

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

在運算式區塊內部，它們不能相互重疊，但可以[遮蔽](#shadowing)來自外部作用域的其他別名或名稱。

## 遮蔽 (Shadowing) {#shadowing}

運算式區塊內部的 `use` 別名可以遮蔽來自外部作用域的名稱（模組成員或別名）。與區域變數的遮蔽一樣，遮蔽在運算式區塊結束時終止。

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
    // 'push_back' 現在指向 std::vector::push_back
    let mut vec = vector[];
    push_back(&mut vec, 0);
    push_back(&mut vec, 1);
    push_back(&mut vec, 10);
    WrappedVector { vec }
}

fun example2(): WrappedVector {
    let vec = {
        use std::vector::push_back;
        // 'push_back' 現在指向 std::vector::push_back

        let mut v = vector[];
        push_back(&mut v, 0);
        push_back(&mut v, 1);
        v
    };
    // 'push_back' 現在指向 Self::push_back
    let mut res = WrappedVector { vec };
    push_back(&mut res, 10);
    res
}
```

## 未使用的 Use 或別名 (Unused Use or Alias)

未使用的 `use` 將導致警告：

```move
module a::example;

use std::option::{some, none}; // 警告！
//                      ^^^^ 未使用的別名 'none'

public fun example(): std::option::Option<u8> {
    some(0)
}
```
