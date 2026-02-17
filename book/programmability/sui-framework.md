---

description: "The Sui Framework: built-in modules for storage, coins, display, clock, events, and other Sui-specific features available to every package."
---

# Sui 框架 (Sui Framework)

要在 Sui 上進行程式設計，您必須與 Sui 框架互動。它是一組定義了物件、其行為以及如何在系統內與其互動的模組。Sui 框架作為一個套件發佈，且對網路上的任何程式都可用（其地址為 `0x2`）。

*為了方便起見，我們將 Sui 框架中的模組分成了多個類別。但它們仍然是同一個框架的一部分。*

## 核心模組 (Core)

<!-- Custom CSS addition in the theme/custom.css  -->
<div class="modules-table">

| 模組 | 描述 | 章節 |
| :--- | :--- | :--- |
| [sui::address](https://docs.sui.io/references/framework/sui/address) | 為 [地址類型](./../move-basics/address) 添加轉換方法 | [地址](./../move-basics/address) |
| [sui::transfer](https://docs.sui.io/references/framework/sui/transfer) | 實作物件的存儲操作 | [存儲函式](./../storage/storage-functions.md) |
| [sui::tx_context](https://docs.sui.io/references/framework/sui/tx_context) | 包含 `TxContext` 結構及其讀取方法 | [交易上下文](./transaction-context) |
| [sui::object](https://docs.sui.io/references/framework/sui/object) | 定義建立物件所需的 `UID` 和 `ID` 類型 | [UID 與 ID](./../storage/uid-and-id.md) |
| [sui::derived_object](https://docs.sui.io/references/framework/sui/derived_object) | 允許透過密鑰衍生產生 `UID` | [UID 衍生](./../storage/uid-and-id.md#uid-derivation) |
| [sui::clock](https://docs.sui.io/references/framework/sui/clock) | 定義 `Clock` 類型及其方法 | [Epoch 與時間](./epoch-and-time) |
| [sui::dynamic_field](https://docs.sui.io/references/framework/sui/dynamic_field) | 實作新增、使用和移除動態欄位的方法 | [動態欄位](./dynamic-fields) |
| [sui::dynamic_object_field](https://docs.sui.io/references/framework/sui/dynamic_object_field) | 實作新增、使用和移除動態物件欄位的方法 | [動態物件欄位](./dynamic-object-fields) |
| [sui::event](https://docs.sui.io/references/framework/sui/event) | 允許為鏈外監聽器發送事件 | [事件](./events) |
| [sui::package](https://docs.sui.io/references/framework/sui/package) | 定義 `Publisher` 類型和套件升級方法 | [發佈者](./publisher), 套件升級 |
| [sui::display](https://docs.sui.io/references/framework/sui/display) | 實作 `Display` 物件及其建立與更新方式 | [顯示 (Display)](./display) |

</div>

## 集合模組 (Collections)

<div class="modules-table">

| 模組 | 描述 | 章節 |
| :--- | :--- | :--- |
| [sui::vec_set](https://docs.sui.io/references/framework/sui/vec_set) | 實作集合 (set) 類型 | [集合](./collections) |
| [sui::vec_map](https://docs.sui.io/references/framework/sui/vec_map) | 實作以向量為鍵的映射 (map) | [集合](./collections) |
| [sui::table](https://docs.sui.io/references/framework/sui/table) | 實作 `Table` 類型及其互動方法 | [動態集合](./dynamic-collections) |
| [sui::linked_table](https://docs.sui.io/references/framework/sui/linked_table) | 實作 `LinkedTable` 類型及其互動方法 | [動態集合](./dynamic-collections) |
| [sui::bag](https://docs.sui.io/references/framework/sui/bag) | 實作 `Bag` 類型及其互動方法 | [動態集合](./dynamic-collections) |
| [sui::object_table](https://docs.sui.io/references/framework/sui/object_table) | 實作 `ObjectTable` 類型及其互動方法 | [動態集合](./dynamic-collections) |
| [sui::object_bag](https://docs.sui.io/references/framework/sui/object_bag) | 實作 `ObjectBag` 類型及其互動方法 | [動態集合](./dynamic-collections) |

</div>

## 工具模組 (Utilities)

<div class="modules-table">

| 模組 | 描述 | 章節 |
| :--- | :--- | :--- |
| [sui::bcs](https://docs.sui.io/references/framework/sui/bcs) | 實作 BCS 編碼與解碼功能 | [二進位規範序列化 (BCS)](./bcs) |
| [sui::borrow](https://docs.sui.io/references/framework/sui/borrow) | 實作「按值借用」的借用機制 | [燙手山芋 (Hot Potato)](./hot-potato-pattern) |
| [sui::hex](https://docs.sui.io/references/framework/sui/hex) | 實作十六進位編碼與解碼功能 | - |
| [sui::types](https://docs.sui.io/references/framework/sui/types) | 提供檢查類型是否為 One-Time-Witness 的方法 | [一次性見證 (One-Time Witness)](./one-time-witness) |

</div>

## 導出的地址 (Exported Addresses)

Sui 框架導出了兩個具名地址：`sui = 0x2` 以及來自 std 依賴項的 `std = 0x1`。

```toml
[addresses]
sui = "0x2"

# 導自 MoveStdlib 依賴項
std = "0x1"
```

## 隱式導入 (Implicit Imports)

就像 [標準庫](./../move-basics/standard-library#implicit-imports) 一樣，Sui 框架中的某些模組和類型會被隱式導入。以下是無需顯式使用 `use` 導入即可使用的模組和類型清單：

- sui::object
- sui::object::ID
- sui::object::UID
- sui::tx_context
- sui::tx_context::TxContext
- sui::transfer

## 原始碼 (Source Code)

Sui 框架的原始碼可在 [Sui 儲存庫](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/sui-framework/sources) 中找到。
