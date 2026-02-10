# 標準庫 (Standard Library)

Move 標準庫為原生類型和運算提供功能。它是一組不與儲存空間互動的標準模組，但提供處理和操作資料的基本工具。它是 [Sui 框架](./../programmability/sui-framework) 唯一的依賴項，並與之一併匯入。

## 最常用的模組

在本書中，我們將詳細介紹標準庫中的大部分模組，但提供一個功能概覽也很有幫助，這樣您可以瞭解可用內容及其對應的實作模組。

<div class="modules-table">

| 模組                                                                             | 說明                                                                       | 章節                                 |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| [std::string](https://docs.sui.io/references/framework/std/string)               | 提供基本字串操作                                                           | [字串 (String)](./string)            |
| [std::ascii](https://docs.sui.io/references/framework/std/ascii)                 | 提供基本 ASCII 操作                                                        | -                                    |
| [std::option](https://docs.sui.io/references/framework/std/option)               | 實作 `Option<T>`                                                           | [選項 (Option)](./option)            |
| [std::vector](https://docs.sui.io/references/framework/std/vector)               | 向量類型的原生操作                                                         | [向量 (Vector)](./vector)            |
| [std::bcs](https://docs.sui.io/references/framework/std/bcs)                     | 包含 `bcs::to_bytes()` 函式                                                | [BCS](./../programmability/bcs)      |
| [std::address](https://docs.sui.io/references/framework/std/address)             | 包含單一 `address::length` 函式                                            | [地址 (Address)](./address)          |
| [std::type_name](https://docs.sui.io/references/framework/std/type_name)         | 允許執行時期 **類型反射 (type reflection)**                                | [類型反射](./type-reflection)        |
| [std::hash](https://docs.sui.io/references/framework/std/hash)                   | 哈希函式：`sha2_256` 和 `sha3_256`                                         | -                                    |
| [std::debug](https://docs.sui.io/references/framework/std/debug)                 | 包含偵錯函式，僅在 **測試 (test)** 模式下可用                              | -                                    |
| [std::bit_vector](https://docs.sui.io/references/framework/std/bit_vector)       | 提供對位元向量的操作                                                       | -                                    |
| [std::fixed_point32](https://docs.sui.io/references/framework/std/fixed_point32) | 提供 `FixedPoint32` 類型                                                   | -                                    |

</div>

## 整數模組

Move 標準庫提供了一組與整數類型相關的函式。這些函式分佈在多個模組中，每個模組與特定的整數類型相關聯。這些模組不應被直接匯入，因為它們的函式在每個整數值上都可用。

> 所有模組都提供相同的函式集：`max`、`diff`、`divide_and_round_up`、`sqrt` 和 `pow`。

<div class="modules-table">

| 模組                                                           | 說明                          |
| -------------------------------------------------------------- | ----------------------------- |
| [std::u8](https://docs.sui.io/references/framework/std/u8)     | 適用於 `u8` 類型的函式        |
| [std::u16](https://docs.sui.io/references/framework/std/u16)   | 適用於 `u16` 類型的函式       |
| [std::u32](https://docs.sui.io/references/framework/std/u32)   | 適用於 `u32` 類型的函式       |
| [std::u64](https://docs.sui.io/references/framework/std/u64)   | 適用於 `u64` 類型的函式       |
| [std::u128](https://docs.sui.io/references/framework/std/u128) | 適用於 `u128` 類型的函式      |
| [std::u256](https://docs.sui.io/references/framework/std/u256) | 適用於 `u256` 類型的函式      |

</div>

## 導出的地址

標準庫導出了一個具名地址 — `std = 0x1`。請注意，別名 `std` 在此處定義。

```toml
[addresses]
std = "0x1"
```

## 隱式匯入 (Implicit Imports)

某些模組會被隱式匯入，無需明確的 `use` 語法即可在模組中使用。對於標準庫，這些模組和類型包括：

- std::vector
- std::option
- std::option::Option

## 在沒有 Sui 框架的情況下匯入 std

Move 標準庫可以被直接匯入到套件中。然而，單獨的 `std` 不足以建立有意義的應用程式，因為它不提供任何儲存能力，也無法與鏈上狀態進行互動。

```toml
MoveStdlib = { git = "https://github.com/MystenLabs/sui.git", subdir = "crates/sui-framework/packages/move-stdlib", rev = "framework/mainnet" }
```

## 原始碼

Move 標準庫的原始碼可在 [Sui 儲存庫](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/move-stdlib/sources) 中找到。
