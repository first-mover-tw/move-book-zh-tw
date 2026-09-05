---
description: Move 標準函式庫 (Move Standard Library) 概觀：每個 Move 套件 (Move package) 中皆可使用的字串 (strings)、向量 (vectors)、選項 (options) 與型別名稱 (type names) 通用模組 (common modules)。
title: 標準函式庫 (Standard Library)
keywords:
  - Move
  - Sui
  - Move tutorial
  - standard
  - library
questions:
  - What is Standard Library in Move?
  - How do I use Standard Library in Move?
  - What is Most Common Modules in Move?
  - What is Integer Modules in Move?
answer: 'Overview of the Move Standard Library: common modules for strings, vectors, options, and type names available in every Move package.'
goal:
  description: 'Reader understands overview of the Move Standard Library: common modules for strings, vectors, options, and type names available in every Move package'
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

# 標準函式庫 (Standard Library) {#standard-library}

Move 標準函式庫為原生型別與操作提供功能。它是由不與儲存體互動的模組組成之標準
集合，但提供處理與操作資料的基本工具。它是
[Sui Framework](./../programmability/sui-framework) 唯一的依賴項，並會與其一同匯入。

## 最常用的模組 (Most Common Modules) {#most-common-modules}

本書會深入說明標準函式庫中的大多數模組；不過，先概覽其功能也很有幫助，讓你能了解
可用的功能以及實作這些功能的模組。

<!-- 在 theme/custom.css 中新增自訂 CSS -->
<div class="modules-table">

| 模組                                                                             | 說明                                                           | 章節                                 |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------ |
| [std::string](https://docs.sui.io/references/framework/std/string)               | 提供基本的字串操作                                             | [字串](./string)                     |
| [std::ascii](https://docs.sui.io/references/framework/std/ascii)                 | 提供基本的 ASCII 操作                                          | -                                    |
| [std::option](https://docs.sui.io/references/framework/std/option)               | 實作 `Option<T>`                                               | [Option](./option)                   |
| [std::vector](https://docs.sui.io/references/framework/std/vector)               | 向量型別的原生操作                                             | [向量](./vector)                     |
| [std::internal](https://docs.sui.io/references/framework/std/internal)           | 為經模組授權的呼叫提供 `Permit<T>` 型別                        | [Internal Permit](./internal-permit) |
| [std::bcs](https://docs.sui.io/references/framework/std/bcs)                     | 包含 `bcs::to_bytes()` 函式                                    | [BCS](./../programmability/bcs)      |
| [std::address](https://docs.sui.io/references/framework/std/address)             | 包含唯一的 `address::length` 函式                              | [地址](./address)                    |
| [std::type_name](https://docs.sui.io/references/framework/std/type_name)         | 允許在執行階段進行 _型別反射_                                  | [型別反射](./type-reflection)        |
| [std::hash](https://docs.sui.io/references/framework/std/hash)                   | 雜湊函式：`sha2_256` 與 `sha3_256`                             | -                                    |
| [std::debug](https://docs.sui.io/references/framework/std/debug)                 | 包含偵錯函式，僅可在 **test** 模式中使用                       | -                                    |
| [std::unit_test](https://docs.sui.io/references/framework/std/unit_test)         | 適用於 **test** 原始碼的 `assert_eq!` 與 `assert_ref_eq!` 巨集 | [測試](./testing)                    |
| [std::bit_vector](https://docs.sui.io/references/framework/std/bit_vector)       | 提供位元向量的操作                                             | -                                    |
| [std::uq32_32](https://docs.sui.io/references/framework/std/uq32_32)             | 定點數運算：`UQ32_32` 型別                                     | -                                    |
| [std::uq64_64](https://docs.sui.io/references/framework/std/uq64_64)             | 定點數運算：`UQ64_64` 型別                                     | -                                    |
| [std::fixed_point32](https://docs.sui.io/references/framework/std/fixed_point32) | `FixedPoint32` 型別；已淘汰，改用 `std::uq32_32`               | -                                    |

</div>

## 整數模組 (Integer Modules) {#integer-modules}

Move 標準函式庫提供一組與整數型別相關的函式。這些函式分散於多個模組中，
每個模組對應特定的整數型別。這些模組不應直接匯入，因為其函式可用於每個整數值。

> 所有模組皆提供相同的一組函式：`min`、`max`、`diff`、
> `divide_and_round_up`、`sqrt`、`pow` 與 `to_string`；可檢查的較小型別轉換，
> 例如 `try_as_u8`、`try_as_u16` 等；以及巨集，例如 `max_value!` 與迭代
> 輔助工具 `do!` 和 `range_do!`。

<!-- 在 theme/custom.css 中新增自訂 CSS -->
<div class="modules-table">

| 模組                                                           | 說明              |
| -------------------------------------------------------------- | ----------------- |
| [std::u8](https://docs.sui.io/references/framework/std/u8)     | `u8` 型別的函式   |
| [std::u16](https://docs.sui.io/references/framework/std/u16)   | `u16` 型別的函式  |
| [std::u32](https://docs.sui.io/references/framework/std/u32)   | `u32` 型別的函式  |
| [std::u64](https://docs.sui.io/references/framework/std/u64)   | `u64` 型別的函式  |
| [std::u128](https://docs.sui.io/references/framework/std/u128) | `u128` 型別的函式 |
| [std::u256](https://docs.sui.io/references/framework/std/u256) | `u256` 型別的函式 |

</div>

## 匯出的地址 (Exported Addresses) {#exported-addresses}

標準函式庫匯出一個具名地址：`std = 0x1`。本書中使用的 `std` 別名便是在此定義。

## 隱式匯入 (Implicit Imports) {#implicit-imports}

部分模組會被隱式匯入，因此可在模組中使用，而無須明確撰寫 `use`
匯入。對標準函式庫而言，這些模組與型別包括：

- std::vector
- std::option
- std::option::Option
- std::internal

請注意，`std::internal` 是以模組而非成員方式匯入：其成員會保留模組
前綴，例如 `internal::Permit<T>` 與 `internal::permit<T>()`，無須 `use`
陳述式。請參閱 [Internal Permit](./internal-permit) 章節，了解其使用方式。

## 不使用 Sui Framework 匯入 std (Importing std without Sui Framework) {#importing-std-without-sui-framework}

Move 標準函式庫可直接匯入套件。不過，僅有 `std` 並不足以建置有意義的應用程式，
因為它不提供任何儲存能力，也無法與鏈上狀態互動。

```toml
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }
```

## 原始碼 (Source Code) {#source-code}

Move 標準函式庫的原始碼可在
[Sui 儲存庫](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/move-stdlib/sources) 取得。
