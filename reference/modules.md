---
title: 模組 (Modules) | 參考手冊
description: Move 模組參考手冊：宣告模組、定義型別與函式、控制可見性，以及在套件中組織程式碼。
keywords:
  - Move
  - Sui
  - Move reference
  - modules
  - reference
questions:
  - How does Modules work in Move?
  - What is the syntax for Modules in Move?
  - What is Names in Move?
  - What is Members in Move?
answer: 'Move module reference: declare modules, define types and functions, control visibility, and organize code in packages.'
goal:
  description: 'Reader understands move module reference: declare modules, define types and functions, control visibility, and organize code in packages'
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

# 模組 (Modules) {#modules}

**模組**是核心的程式單元，用於定義型別及操作這些型別的函式。結構型別定義 Move [儲存空間](./abilities#key)的結構描述，而模組函式則定義與這些型別值互動的規則。雖然模組本身也儲存在儲存空間中，但無法從 Move 程式內存取。在區塊鏈環境中，模組會儲存在鏈上，此程序通常稱為「發布」。發布後，可依照該特定 Move 實作的規則呼叫 [`entry`](./functions#entry-modifier) 與 [`public`](./functions#visibility) 函式。

## 語法 (Syntax) {#syntax}

模組具有下列語法：

```text
module <address>::<identifier> {
    (<use> | <type> | <function> | <constant>)*
}
```

其中，`<address>` 是有效的 [地址](./primitive-types/address)，用於指定模組所屬的套件。

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

## 名稱 (Names) {#names}

`module test_addr::test` 部分指定模組 `test` 將會發布在[套件設定](./packages)中指派給名稱 `test_addr` 的數值[地址](./primitive-types/address)下。

模組通常應使用[具名地址](./primitive-types/address)宣告（而非直接使用數值）。例如：

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

這些具名地址通常會與[套件](./packages)名稱相符。

由於具名地址僅存在於原始碼語言層級及編譯期間，因此在位元碼層級中，具名地址會完全替換為其值。例如，若我們有下列程式碼：

```move
fun example() {
    my_addr::m::foo(@my_addr);
}
```

且我們在 `my_addr` 設定為 `0xC0FFEE` 時編譯它，則其執行效果等同於下列程式碼：

```move
fun example() {
    0xC0FFEE::m::foo(@0xC0FFEE);
}
```

雖然在原始碼層級中，這兩種不同的存取方式等效，但最佳做法是一律使用具名地址，而非指派給該地址的數值。

模組名稱可由 `a` 至 `z` 的小寫字母或 `A` 至 `Z` 的大寫字母開頭。第一個字元之後，模組名稱可包含底線 `_`、`a` 至 `z` 的字母、`A` 至 `Z` 的字母，或 `0` 至 `9` 的數字。

```move
module a::my_module {}
module a::foo_bar_42 {}
```

通常，模組名稱以小寫字母開頭。名為 `my_module` 的模組應儲存在名為 `my_module.move` 的原始碼檔案中。

## 成員 (Members) {#members}

`module` 區塊中的所有成員可依任意順序出現。從根本上說，模組是由 [`types`](./structs) 與 [`functions`](./functions) 組成的集合。[`use`](./uses) 關鍵字會參考其他模組的成員。[`const`](./constants) 關鍵字會定義可在模組函式中使用的常數。

[`friend`](./friends) 語法是用於指定受信任模組清單的已淘汰概念。此概念已由 [`public(package)`](./functions#visibility) 取代。

<!-- TODO 成員存取規則 -->
