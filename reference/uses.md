---
title: 使用 (Uses) 與別名 (Aliases) | 參考手冊
description: Move use 宣告 (use) 與別名 (aliases) 參考：匯入模組 (modules)、建立別名、將匯入項目分組，並解析命名衝突 (naming conflicts)。
keywords:
  - Move
  - Sui
  - Move reference
  - uses
  - aliases
  - reference
questions:
  - How does Uses and Aliases work in Move?
  - What is the syntax for Uses and Aliases in Move?
  - What is Inside a module in Move?
  - What is Inside an expression in Move?
answer: 'Move use and aliases reference: import modules, create aliases, group imports, and resolve naming conflicts.'
goal:
  description: 'Reader understands move use and aliases reference: import modules, create aliases, group imports, and resolve naming conflicts'
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

# 使用與別名 (Uses and Aliases) {#uses-and-aliases}

`use` 語法可用於為其他模組中的成員建立別名。`use` 可用於建立持續於整個模組，或指定運算式區塊範圍內的別名。

## 語法 (Syntax) {#syntax}

`use` 有數種不同的語法情況。從最簡單的開始，以下用於建立其他模組的別名：

```move
use <address>::<module name>;
use <address>::<module name> as <module alias name>;
```

例如：

```move
use std::vector;
use std::option as o;
```

`use std::vector;` 為 `std::vector` 引入別名 `vector`。這表示在任何原本要使用模組名稱 `std::vector` 的地方（假設此 `use` 位於作用域內），都可以改用 `vector`。`use std::vector;` 等同於 `use std::vector as vector;`

同樣地，`use std::option as o;` 可讓你使用 `o` 取代 `std::option`。

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

如果你想匯入特定模組成員（例如函式或結構體），可以使用以下語法。

```move
use <address>::<module name>::<module member>;
use <address>::<module name>::<module member> as <member alias>;
```

例如：

```move
use std::vector::push_back;
use std::option::some as s;
```

這可讓你不必使用完整限定名稱即可使用函式 `std::vector::push_back`。同樣地，`std::option::some` 可使用 `s`。你可以分別改用 `push_back` 與 `s`。同樣地，`use std::vector::push_back;` 等同於 `use std::vector::push_back as push_back;`

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

### 多個別名 (Multiple Aliases) {#multiple-aliases}

如果你想一次為多個模組成員新增別名，可以使用以下語法：

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

### Self 別名 (Self aliases) {#self-aliases}

如果除了模組成員外，還需要為模組本身新增別名，可以透過 `Self` 在單一 `use` 中完成。`Self` 是一種類似成員的項目，指向該模組。

```move
use std::option::{Self, some, none};
```

為求清楚，以下所有寫法皆等同：

```move
use std::option;
use std::option as option;
use std::option::Self;
use std::option::Self as option;
use std::option::{Self};
use std::option::{Self as option};
```

### 相同定義的多個別名 (Multiple Aliases for the Same Definition) {#multiple-aliases-for-the-same-definition}

如有需要，你可以為任何項目建立任意數量的別名：

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

### 巢狀匯入 (Nested imports) {#nested-imports}

在 Move 中，你也可以透過相同的 `use` 宣告匯入多個名稱。這會將所有提供的名稱帶入作用域：

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

## `module` 內部 (Inside a `module`) {#inside-a-module}

在 `module` 內部，所有 `use` 宣告都可使用，不受宣告順序影響。

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

由 `use` 在模組中宣告的別名可在該模組內使用。

此外，導入的別名不得與其他模組成員衝突。如需更多詳細資訊，請參閱
[唯一性](#uniqueness)。

## 運算式內部 (Inside an expression) {#inside-an-expression}

你可以在任何運算式區塊的開頭加入 `use` 宣告。

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

與 `let` 相同，`use` 在運算式區塊中引入的別名會在該區塊結束時移除。

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

在區塊結束後嘗試使用該別名會產生錯誤。

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

任何 `use` 都必須是區塊中的第一個項目。若 `use` 位於任何運算式或 `let` 之後，將產生剖析錯誤。

```move
{
    let mut v = vector[];
    use std::vector; // 錯誤！
}
```

這可讓你在許多情況下縮短匯入區塊。請注意，這些匯入與前述匯入相同，皆須遵守後續章節所述的命名與唯一性規則。

## 命名規則 (Naming rules) {#naming-rules}

別名必須遵循與其他模組成員相同的規則。這表示，結構（以及常數）的別名必須以 `A` 到 `Z` 開頭。

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

## 唯一性 (Uniqueness) {#uniqueness}

在指定範圍內，所有由 `use` 宣告引入的別名都必須是唯一的。

對於模組而言，這表示由 `use` 引入的別名不可重疊：

```move
module a::example;

use std::option::{none as foo, some as foo}; // 錯誤！
//                                     ^^^ 重複的 'foo'

use std::option::none as bar;

use std::option::some as bar; // 錯誤！
//                       ^^^ 重複的 'bar'
```

而且它們不得與模組的任何其他成員重疊：

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

在運算式區塊內，它們不得彼此重疊，但可以
[遮蔽](#shadowing) 外層範圍中的其他別名或名稱。

## 名稱遮蔽 (Shadowing) {#shadowing}

運算式區塊內的 `use` 別名可以遮蔽外層作用域中的名稱（模組成員或別名）。如同區域變數的名稱遮蔽，遮蔽會在運算式區塊結束時結束；

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

## 未使用的 Use 或別名 (Unused Use or Alias) {#unused-use-or-alias}

未使用的 `use` 會產生警告

```move
module a::example;

use std::option::{some, none}; // 警告！
//                      ^^^^ 未使用的別名 'none'

public fun example(): std::option::Option<u8> {
    some(0)
}
```
