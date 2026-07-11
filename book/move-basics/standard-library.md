---
description: 標準函式庫 (Standard Library) 概覽：說明字串、向量、選項與型別名稱等每個 Move 套件都能使用的常見模組。
---

# 標準函式庫 (Standard Library) {#standard-library}

Move 標準函式庫提供原生型別與操作相關的功能。它是一組標準模組的集合，不與儲存互動，但提供用於處理與操作資料的基本工具。它是 [Sui 框架](./../programmability/sui-framework) 唯一的依賴項，且與其一同被引入。

## 最常用的模組 (Most Common Modules) {#most-common-modules}

在本書中，我們會詳細介紹標準函式庫中的大部分模組，不過先概略介紹一下功能也很有幫助，讓你能大致了解有哪些可用功能以及是由哪個模組實作的。

<!-- Custom CSS addition in the theme/custom.css  -->
<div class="modules-table">

| Module                                                                           | Description                                                                | Chapter                              |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| [std::string](https://docs.sui.io/references/framework/std/string)               | Provides basic string operations                                           | [String](./string)                   |
| [std::ascii](https://docs.sui.io/references/framework/std/ascii)                 | Provides basic ASCII operations                                            | -                                    |
| [std::option](https://docs.sui.io/references/framework/std/option)               | Implements `Option<T>`                                                     | [Option](./option)                   |
| [std::vector](https://docs.sui.io/references/framework/std/vector)               | Native operations on the vector type                                       | [Vector](./vector)                   |
| [std::internal](https://docs.sui.io/references/framework/std/internal)           | Provides the `Permit<T>` type for module-authorized calls                  | [Internal Permit](./internal-permit) |
| [std::bcs](https://docs.sui.io/references/framework/std/bcs)                     | Contains the `bcs::to_bytes()` function                                    | [BCS](./../programmability/bcs)      |
| [std::address](https://docs.sui.io/references/framework/std/address)             | Contains a single `address::length` function                               | [Address](./address)                 |
| [std::type_name](https://docs.sui.io/references/framework/std/type_name)         | Allows runtime _type reflection_                                           | [Type Reflection](./type-reflection) |
| [std::hash](https://docs.sui.io/references/framework/std/hash)                   | Hashing functions: `sha2_256` and `sha3_256`                               | -                                    |
| [std::debug](https://docs.sui.io/references/framework/std/debug)                 | Contains debugging functions, which are available in only in **test** mode | -                                    |
| [std::unit_test](https://docs.sui.io/references/framework/std/unit_test)         | The `assert_eq!` and `assert_ref_eq!` macros for **test** code             | [Testing](./testing)                 |
| [std::bit_vector](https://docs.sui.io/references/framework/std/bit_vector)       | Provides operations on bit vectors                                         | -                                    |
| [std::uq32_32](https://docs.sui.io/references/framework/std/uq32_32)             | Fixed-point arithmetic: the `UQ32_32` type                                 | -                                    |
| [std::uq64_64](https://docs.sui.io/references/framework/std/uq64_64)             | Fixed-point arithmetic: the `UQ64_64` type                                 | -                                    |
| [std::fixed_point32](https://docs.sui.io/references/framework/std/fixed_point32) | The `FixedPoint32` type; deprecated in favor of `std::uq32_32`             | -                                    |

</div>

## 整數模組 (Integer Modules) {#integer-modules}

Move 標準函式庫提供了一組與整數型別相關的函式。這些函式被拆分到多個模組中，每個模組對應一個特定的整數型別。這些模組不應該被直接引入，因為它們的函式在每個整數值上都可以直接使用。

> 所有模組都提供同一組函式：`min`、`max`、`diff`、
> `divide_and_round_up`、`sqrt`、`pow` 與 `to_string`；用於轉換為較小型別的檢查型轉換函式——
> `try_as_u8`、`try_as_u16` 等等；以及巨集（macro），例如 `max_value!` 與迭代
> 輔助函式 `do!` 與 `range_do!`。

<!-- Custom CSS addition in the theme/custom.css  -->
<div class="modules-table">

| Module                                                         | Description                   |
| -------------------------------------------------------------- | ----------------------------- |
| [std::u8](https://docs.sui.io/references/framework/std/u8)     | Functions for the `u8` type   |
| [std::u16](https://docs.sui.io/references/framework/std/u16)   | Functions for the `u16` type  |
| [std::u32](https://docs.sui.io/references/framework/std/u32)   | Functions for the `u32` type  |
| [std::u64](https://docs.sui.io/references/framework/std/u64)   | Functions for the `u64` type  |
| [std::u128](https://docs.sui.io/references/framework/std/u128) | Functions for the `u128` type |
| [std::u256](https://docs.sui.io/references/framework/std/u256) | Functions for the `u256` type |

</div>

## 匯出的位址 (Exported Addresses) {#exported-addresses}

標準函式庫匯出了單一個具名位址——`std = 0x1`。這就是本書中所使用的 `std` 別名的定義處。

## 隱式匯入 (Implicit Imports) {#implicit-imports}

有些模組會被隱式引入，並在模組中無需明確的 `use` 匯入即可使用。對於標準函式庫而言，這些模組與型別包括：

- std::vector
- std::option
- std::option::Option
- std::internal

請注意，`std::internal` 是以模組的形式被引入，而非成員：它的成員仍保留模組
前綴，例如 `internal::Permit<T>` 與 `internal::permit<T>()`——不需要 `use` 陳述式。詳見
[Internal Permit 內部授權許可](./internal-permit) 章節了解其用法。

## 匯入不含 Sui 框架的 std (Importing std without Sui Framework) {#importing-std-without-sui-framework}

Move 標準函式庫可以直接被匯入到套件中。然而，光靠 `std` 並
不足以建構出有意義的應用程式，因為它不提供任何儲存能力，也無法
與鏈上狀態互動。

```toml
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }
```

## 原始碼 (Source Code) {#source-code}

Move 標準函式庫的原始碼可在
[Sui 儲存庫](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/move-stdlib/sources)中取得。
