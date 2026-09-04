---
description: Sui 框架 (Sui Framework)：每個套件皆可使用的內建模組，提供儲存、代幣、顯示、時鐘、事件及其他 Sui 專屬功能。
title: Sui 框架 (Sui Framework)
keywords:
  - Move
  - Sui
  - Move tutorial
  - sui
  - framework
questions:
  - What is Sui Framework in Move?
  - How do I use Sui Framework in Move?
  - What is Core in Move?
  - What is Collections in Move?
answer: 'The Sui Framework: built-in modules for storage, coins, display, clock, events, and other Sui-specific features available to every package.'
goal:
  description: 'Reader understands the Sui Framework: built-in modules for storage, coins, display, clock, events, and other Sui-specific features available to every package'
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

# Sui Framework 框架 (Sui Framework) {#sui-framework}

Sui Framework 是 [套件清單](./../concepts/manifest)中的一組預設依賴項。它
依賴[標準函式庫](./../move-basics/standard-library)，並提供 Sui 專屬的
功能：儲存操作、原生型別，以及本章其餘內容所建構於其上的模組。

_為了方便起見，我們將 Sui Framework 中的模組分成多個類別。但它們仍然
屬於同一個框架。_

## 核心 (Core) {#core}

<!-- 在 theme/custom.css 中新增自訂 CSS -->
<div class="modules-table">

| 模組                                                                                           | 說明                                                   | 章節                                                  |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| [sui::address](https://docs.sui.io/references/framework/sui/address)                           | 為[address 型別](./../move-basics/address)新增轉換方法 | [地址](./../move-basics/address)                      |
| [sui::transfer](https://docs.sui.io/references/framework/sui/transfer)                         | 實作物件的儲存操作                                     | [儲存函式](./../storage/storage-functions.md)         |
| [sui::tx_context](https://docs.sui.io/references/framework/sui/tx_context)                     | 包含 `TxContext` 結構與讀取它的方法                    | [交易情境](./transaction-context)                     |
| [sui::object](https://docs.sui.io/references/framework/sui/object)                             | 定義建立物件所需的 `UID` 與 `ID` 型別                  | [UID 與 ID](./../storage/uid-and-id.md)               |
| [sui::derived_object](https://docs.sui.io/references/framework/sui/derived_object)             | 允許透過金鑰衍生產生 `UID`                             | [UID 衍生](./../storage/uid-and-id.md#uid-derivation) |
| [sui::clock](https://docs.sui.io/references/framework/sui/clock)                               | 定義 `Clock` 型別及其方法                              | [Epoch 與時間](./epoch-and-time)                      |
| [sui::dynamic_field](https://docs.sui.io/references/framework/sui/dynamic_field)               | 實作新增、使用及移除動態欄位的方法                     | [動態欄位](./dynamic-fields)                          |
| [sui::dynamic_object_field](https://docs.sui.io/references/framework/sui/dynamic_object_field) | 實作新增、使用及移除動態物件欄位的方法                 | [動態物件欄位](./dynamic-object-fields)               |
| [sui::event](https://docs.sui.io/references/framework/sui/event)                               | 允許為鏈下監聽器發出事件                               | [事件](./events)                                      |
| [sui::package](https://docs.sui.io/references/framework/sui/package)                           | 定義 `Publisher` 型別與套件升級方法                    | [發布者](./publisher)                                 |
| [sui::display](https://docs.sui.io/references/framework/sui/display)                           | 實作 `Display` 物件及建立與更新它的方式                | [顯示](./display)                                     |

</div>

## 集合 (Collections) {#collections}

<div class="modules-table">

| 模組                                                                           | 說明                                    | 章節                              |
| ------------------------------------------------------------------------------ | --------------------------------------- | --------------------------------- |
| [sui::vec_set](https://docs.sui.io/references/framework/sui/vec_set)           | 實作集合型別                            | [集合](./collections)             |
| [sui::vec_map](https://docs.sui.io/references/framework/sui/vec_map)           | 實作具有向量金鑰的映射                  | [集合](./collections)             |
| [sui::table](https://docs.sui.io/references/framework/sui/table)               | 實作 `Table` 型別及與其互動的方法       | [動態集合](./dynamic-collections) |
| [sui::linked_table](https://docs.sui.io/references/framework/sui/linked_table) | 實作 `LinkedTable` 型別及與其互動的方法 | [動態集合](./dynamic-collections) |
| [sui::bag](https://docs.sui.io/references/framework/sui/bag)                   | 實作 `Bag` 型別及與其互動的方法         | [動態集合](./dynamic-collections) |
| [sui::object_table](https://docs.sui.io/references/framework/sui/object_table) | 實作 `ObjectTable` 型別及與其互動的方法 | [動態集合](./dynamic-collections) |
| [sui::object_bag](https://docs.sui.io/references/framework/sui/object_bag)     | 實作 `ObjectBag` 型別及與其互動的方法   | [動態集合](./dynamic-collections) |

</div>

## 代幣與資產 (Coins and Assets) {#coins-and-assets}

<div class="modules-table">

| 模組                                                                     | 說明                              | 章節                                  |
| ------------------------------------------------------------------------ | --------------------------------- | ------------------------------------- |
| [sui::balance](https://docs.sui.io/references/framework/sui/balance)     | `Balance` 型別 — 價值的底層儲存體 | [Balance 與 Coin](./balance-and-coin) |
| [sui::coin](https://docs.sui.io/references/framework/sui/coin)           | `Coin` 型別 — 可轉移的可替代資產  | [Balance 與 Coin](./balance-and-coin) |
| [sui::sui](https://docs.sui.io/references/framework/sui/sui)             | SUI 代幣型別                      | [Balance 與 Coin](./balance-and-coin) |
| [sui::pay](https://docs.sui.io/references/framework/sui/pay)             | 用於分割及合併代幣的輔助函式      | -                                     |
| [sui::deny_list](https://docs.sui.io/references/framework/sui/deny_list) | 受監管代幣型別的拒絕清單          | -                                     |
| [sui::token](https://docs.sui.io/references/framework/sui/token)         | 封閉迴路代幣標準                  | -                                     |

</div>

## 工具程式 (Utilities) {#utilities}

<div class="modules-table">

| 模組                                                               | 說明                                       | 章節                             |
| ------------------------------------------------------------------ | ------------------------------------------ | -------------------------------- |
| [sui::bcs](https://docs.sui.io/references/framework/sui/bcs)       | 實作 BCS 編碼與解碼函式                    | [二進位標準序列化](./bcs)        |
| [sui::borrow](https://docs.sui.io/references/framework/sui/borrow) | 實作依 _值_ 借用的借用機制                 | [燙手山芋](./hot-potato-pattern) |
| [sui::hex](https://docs.sui.io/references/framework/sui/hex)       | 實作十六進位編碼與解碼函式                 | -                                |
| [sui::random](https://docs.sui.io/references/framework/sui/random) | `Random` 物件與安全的鏈上隨機性            | [隨機性](./randomness)           |
| [sui::types](https://docs.sui.io/references/framework/sui/types)   | 提供檢查型別是否為 One-Time-Witness 的方式 | [一次性見證](./one-time-witness) |

</div>

此框架也包含本書未涵蓋的模組：商務基元
([sui::kiosk](https://docs.sui.io/references/framework/sui/kiosk),
[sui::transfer_policy](https://docs.sui.io/references/framework/sui/transfer_policy))、一組
密碼學函式（[sui::hash](https://docs.sui.io/references/framework/sui/hash)、
[sui::ed25519](https://docs.sui.io/references/framework/sui/ed25519)、
[sui::bls12381](https://docs.sui.io/references/framework/sui/bls12381)及其他），以及各種
工具程式，例如 [sui::url](https://docs.sui.io/references/framework/sui/url) 和
[sui::versioned](https://docs.sui.io/references/framework/sui/versioned)。如需完整清單，請參考
[框架文件](https://docs.sui.io/references/framework)。

## 匯出的地址 (Exported Addresses) {#exported-addresses}

Sui Framework 從 std 依賴項匯出兩個具名地址：`sui = 0x2` 與 `std = 0x1`。

## 隱含匯入 (Implicit Imports) {#implicit-imports}

如同[標準函式庫](./../move-basics/standard-library#implicit-imports)，Sui Framework 中的部分
模組與型別會被隱含匯入。以下是無須明確使用 `use` 匯入即可使用的模組與
型別清單：

- sui::object
- sui::object::ID
- sui::object::UID
- sui::tx_context
- sui::tx_context::TxContext
- sui::transfer

## 原始碼 (Source Code) {#source-code}

Sui Framework 的原始碼可於
[Sui 儲存庫](https://github.com/MystenLabs/sui/tree/main/crates/sui-framework/packages/sui-framework/sources)取得。
