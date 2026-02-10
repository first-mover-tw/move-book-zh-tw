---
title: '模組 (Modules) | 參考手冊'
description: "Move 模組參考手冊：宣告模組、定義類型與函數、控制可見度，以及在套件中組織程式碼。"
---

# 模組 (Modules)

**模組 (Modules)** 是核心程式單元，定義了類型以及操作這些類型的函式。結構體 (Struct) 類型定義了 Move [存儲 (storage)](./abilities#key) 的結構 (schema)，而模組函式定義了與這些類型的數值互動的規則。雖然模組本身也存儲在存儲中，但它們無法從 Move 程式內部存取。在區塊鏈環境中，模組存儲在鏈上，這個過程通常稱為「發布 (publishing)」。發布後，可以根據該特定 Move 實例的規則呼叫 [`entry`](./functions#entry-modifier) 和 [`public`](./functions#visibility) 函式。

## 語法

模組具有以下語法：

```text
module <address>::<identifier> {
    (<use> | <type> | <function> | <constant>)*
}
```

其中 `<address>` 是一個有效的 [地址 (address)](./primitive-types/address)，指定了模組所在的套件。

例如：

```move
module 0::test;

use std::debug;

const ONE: u64 = 1;

public struct Example has copy, drop { i: u64 }

public fun print(x: u64) {
    let sum = x + ONE;
    let example = Example { i: sum };
    debug::print(&sum)
}
```

## 名稱

`module test_addr::test` 部分指定模組 `test` 將發布在 [套件設定](./packages) 中為名稱 `test_addr` 分配的數字 [地址 (address)](./primitive-types/address) 數值下。

模組通常應使用 [具名地址 (named addresses)](./primitive-types/address) 來宣告（相對於直接使用數字值）。例如：

```move
module test_addr::test;

use std::debug;
use test_addr::another_test;

public struct Example has copy, drop { a: address }

public fun print() {
    let example = Example { a: @test_addr };
    debug::print(&example)
}
```

這些具名地址通常與 [套件 (package)](./packages) 的名稱相匹配。

由於具名地址僅存在於原始語言層級和編譯期間，具名地址在位元組碼層級將被完全替換為它們的數值。例如，如果我們有以下程式碼：

```move
fun example() {
    my_addr::m::foo(@my_addr);
}
```

並且我們在將 `my_addr` 設置為 `0xC0FFEE` 的情況下對其進行編譯，那麼它在操作上將等同於以下內容：

```move
fun example() {
    0xC0FFEE::m::foo(@0xC0FFEE);
}
```

雖然在原始語言層次這兩種不同的存取方式是等價的，但最佳做法是始終使用具名地址，而不是分配給該地址的數字值。

模組名稱可以以小寫字母 `a` 到 `z` 或大寫字母 `A` 到 `Z` 開頭。在第一個字元之後，模組名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
module a::my_module {}
module a::foo_bar_42 {}
```

通常，模組名稱以小寫字母開頭。名為 `my_module` 的模組應存儲在名為 `my_module.move` 的原始檔中。

## 成員

`module` 區塊內的所有成員可以以任何順序出現。從根本上說，模組是 [`類型 (types)`](./structs) 和 [`函式 (functions)`](./functions) 的集合。[`use`](./uses) 關鍵字引用來自其他模組的成員。[`const`](./constants) 關鍵字定義了可以在模組函式中使用的常數。

[`friend`](./friends) 語法是用於指定受信任模組清單的一種已棄用概念。該概念已被 [`public(package)`](./functions#visibility) 取代。

<!-- TODO member access rules -->
