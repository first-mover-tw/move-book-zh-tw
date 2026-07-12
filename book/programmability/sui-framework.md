---
description:
  Sui 框架 (The Sui Framework)：內建模組 (built-in modules)，提供儲存、代幣、顯示、時鐘、事件等每個套件都可使用的
  Sui 專屬功能。
---

# Sui 框架 (Sui Framework) {#sui-framework}

Sui Framework 是 [Package Manifest](./../concepts/manifest) 中預設的依賴集合。它依賴於
[Standard Library](./../move-basics/standard-library)，並提供 Sui 專屬的功能：儲存操作、原生型別，以及本章其餘內容所建立在其上的模組。

_為了方便起見，我們將 Sui Framework 中的模組分成多個類別，但它們仍然是同一個框架的一部分。_

## 核心 (Core) {#core}

<!-- Custom CSS addition in the theme/custom.css  -->
<div class="modules-table">

| Module                                                                                         | Description                                              | Chapter                                                     |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------- |
| [sui::address](https://docs.sui.io/references/framework/sui/address)                           | 為 [address 型別](./../move-basics/address) 新增轉換方法 | [Address](./../move-basics/address)                         |
| [sui::transfer](https://docs.sui.io/references/framework/sui/transfer)                         | 實作 Object 的儲存操作                                   | [Storage Functions](./../storage/storage-functions.md)      |
| [sui::tx_context](https://docs.sui.io/references/framework/sui/tx_context)                     | 包含 `TxContext` 結構體以及讀取它的方法                  | [Transaction Context](./transaction-context)                |
| [sui::object](https://docs.sui.io/references/framework/sui/object)                             | 定義建立物件所需的 `UID` 與 `ID` 型別                    | [UID and ID](./../storage/uid-and-id.md)                    |
| [sui::derived_object](https://docs.sui.io/references/framework/sui/derived_object)             | 允許透過金鑰衍生產生 `UID`                               | [UID Derivation](./../storage/uid-and-id.md#uid-derivation) |
| [sui::clock](https://docs.sui.io/references/framework/sui/clock)                               | 定義 `Clock` 型別及其方法                                | [Epoch and Time](./epoch-and-time)                          |
| [sui::dynamic_field](https://docs.sui.io/references/framework/sui/dynamic_field)               | 實作新增、使用與移除動態欄位的方法                       | [Dynamic Fields](./dynamic-fields)                          |
| [sui::dynamic_object_field](https://docs.sui.io/references/framework/sui/dynamic_object_field) | 實作新增、使用與移除動態物件欄位的方法                   | [Dynamic Object Fields](./dynamic-object-fields)            |
| [sui::event](https://docs.sui.io/references/framework/sui/event)                               | 允許發出事件供鏈下監聽器使用                             | [Events](./events)                                          |
| [sui::package](https://docs.sui.io/references/framework/sui/package)                           | 定義 `Publisher` 型別以及套件升級方法                    | [Publisher](./publisher)                                    |
| [sui::display](https://docs.sui.io/references/framework/sui/display)                           | 實作 `Display` 物件以及建立與更新它的方式                | [Display](./display)                                        |

</div>

## 集合 (Collections) {#collections}

<div class="modules-table">

| Module                                                                         | Description                               | Chapter                                      |
| ------------------------------------------------------------------------------ | ----------------------------------------- | -------------------------------------------- |
| [sui::vec_set](https://docs.sui.io/references/framework/sui/vec_set)           | 實作一種 set 型別                         | [Collections](./collections)                 |
| [sui::vec_map](https://docs.sui.io/references/framework/sui/vec_map)           | 實作以 vector 為鍵的 map                  | [Collections](./collections)                 |
| [sui::table](https://docs.sui.io/references/framework/sui/table)               | 實作 `Table` 型別以及與其互動的方法       | [Dynamic Collections](./dynamic-collections) |
| [sui::linked_table](https://docs.sui.io/references/framework/sui/linked_table) | 實作 `LinkedTable` 型別以及與其互動的方法 | [Dynamic Collections](./dynamic-collections) |
| [sui::bag](https://docs.sui.io/references/framework/sui/bag)                   | 實作 `Bag` 型別以及與其互動的方法         | [Dynamic Collections](./dynamic-collections) |
| [sui::object_table](https://docs.sui.io/references/framework/sui/object_table) | 實作 `ObjectTable` 型別以及與其互動的方法 | [Dynamic Collections](./dynamic-collections) |
| [sui::object_bag](https://docs.sui.io/references/framework/sui/object_bag)     | 實作 `ObjectBag` 型別以及與其互動的方法   | [Dynamic Collections](./dynamic-collections) |

</div>

## 代幣與資產 (Coins and Assets) {#coins-and-assets}

<div class="modules-table">

| Module                                                                   | Description                          | Chapter                                |
| ------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------- |
| [sui::balance](https://docs.sui.io/references/framework/sui/balance)     | `Balance` 型別 —— 價值的底層儲存方式 | [Balance and Coin](./balance-and-coin) |
| [sui::coin](https://docs.sui.io/references/framework/sui/coin)           | `Coin` 型別 —— 可轉移的同質化資產    | [Balance and Coin](./balance-and-coin) |
| [sui::sui](https://docs.sui.io/references/framework/sui/sui)             | SUI 代幣型別                         | [Balance and Coin](./balance-and-coin) |
| [sui::pay](https://docs.sui.io/references/framework/sui/pay)             | 用於拆分與合併代幣的輔助函式         | -                                      |
| [sui::deny_list](https://docs.sui.io/references/framework/sui/deny_list) | 用於受監管代幣型別的拒絕清單         | -                                      |
| [sui::token](https://docs.sui.io/references/framework/sui/token)         | 封閉迴路（closed-loop）代幣標準      | -                                      |

</div>

## 實用工具 (Utilities) {#utilities}

<div class="modules-table">

| Module                                                             | Description                                | Chapter                                 |
| ------------------------------------------------------------------ | ------------------------------------------ | --------------------------------------- |
| [sui::bcs](https://docs.sui.io/references/framework/sui/bcs)       | 實作 BCS 編碼與解碼函式                    | [Binary Canonical Serialization](./bcs) |
| [sui::borrow](https://docs.sui.io/references/framework/sui/borrow) | 實作以 _value_ 方式借用的借用機制          | [Hot Potato](./hot-potato-pattern)      |
| [sui::hex](https://docs.sui.io/references/framework/sui/hex)       | 實作十六進位編碼與解碼函式                 | -                                       |
| [sui::random](https://docs.sui.io/references/framework/sui/random) | `Random` 物件與安全的鏈上隨機性            | [Randomness](./randomness)              |
| [sui::types](https://docs.sui.io/references/framework/sui/types)   | 提供檢查型別是否為 One-Time-Witness 的方式 | [One Time Witness](./one-time-witness)  |

</div>

該框架也包含本書未涵蓋的模組：商業原語
（[sui::kiosk](https://docs.sui.io/references/framework/sui/kiosk)、
[sui::transfer_policy](https://docs.sui.io/references/framework/sui/transfer_policy)）、一組
密碼學函式（[sui::hash](https://docs.sui.io/references/framework/sui/hash)、
[sui::ed25519](https://docs.sui.io/references/framework/sui/ed25519)、
[sui::bls12381](https://docs.sui.io/references/framework/sui/bls12381) 等等），以及一些
輔助工具，例如 [sui::url](https://docs.sui.io/references/framework/sui/url) 與
[sui::versioned](https://docs.sui.io/references/framework/sui/versioned)。完整清單請參閱
[框架文件](https://docs.sui.io/references/framework)。

## 匯出地址 (Exported Addresses) {#exported-addresses}

Sui Framework 匯出了兩個具名地址：`sui = 0x2`，以及來自 std 依賴的 `std = 0x1`。

## 隱式匯入 (Implicit Imports) {#implicit-imports}

就像 [Standard Library](./../move-basics/standard-library#implicit-imports) 一樣，Sui Framework 中
有些模組與型別會被隱式匯入。以下是不需明確 `use` 匯入即可使用的模組與
型別清單：

- sui::object
- sui::object::ID
- sui::object::UID
- sui::tx_context
- sui::tx_context::TxContext
- sui::transfer

## 原始碼 (Source Code) {#source-code}

Sui Framework 的原始碼可在
[Sui repository](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/sui-framework/sources) 中取得。
