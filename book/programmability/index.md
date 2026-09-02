---
description: Sui 進階可程式化性 (Advanced Sui Programmability)：Move 中的模式、事件、動態欄位、能力 (capabilities)、BCS 序列化與設計模式。
---

# 進階可程式化性 (Advanced Programmability) {#advanced-programmability}

在前面的章節中，我們已經介紹了 [Move 基礎](./../move-basics) 與
[Sui 儲存模型](./../storage)。現在是時候更深入探討 Sui
可程式化性的進階主題了。本章介紹更複雜的概念、實務作法與 Move 及
Sui 的功能，這些是建構更複雜應用程式所必需的。

各小節依照前後銜接的順序排列，但它們也構成幾條大致獨立的線索，你可以只跟隨目前需要的那條：

- **執行環境 (The execution environment)** - 程式可以從其執行的交易與周圍系統中得知什麼，以及如何與外部世界溝通：
  [Sui Framework](./sui-framework)、[Transaction Context](./transaction-context)、
  [Module Initializer](./module-initializer)、[Epoch and Time](./epoch-and-time)、
  [Events](./events)，以及 [Binary Canonical Serialization](./bcs)。

- **大規模儲存 (Storage at scale)** - 從簡單的以 vector 為基礎的集合，到動態欄位這種能將任意資料附加到物件上並解除靜態型別與大小限制的基礎機制：
  [Collections](./collections)、[Wrapper Type](./wrapper-type-pattern)、
  [Dynamic Fields](./dynamic-fields)、[Dynamic Object Fields](./dynamic-object-fields)，以及
  [Dynamic Collections](./dynamic-collections)。

- **權限模式 (Patterns of authority)** - Move 對存取控制的解法：從作為權限的擁有物件，到系統背書的保證，以及建構於其上的功能：
  [Capability](./capability)、[Witness](./witness-pattern)、
  [One Time Witness](./one-time-witness)、[Publisher](./publisher)、[Display](./display)，以及
  [Hot Potato](./hot-potato-pattern)。

- **資產與資金 (Assets and funds)** - 可替代價值以及持有它的兩種方式，作為物件或作為直接附加在地址上的餘額：[Balance and Coin](./balance-and-coin) 與
  [Address Balances](./address-balances)。

- **程式碼演進 (Code evolution)** - 程式碼上線後會發生什麼事：發布套件的新版本、保護共享狀態不受舊版本影響，以及遷移資料：
  [Package Upgrades](./package-upgrades)。

> 本章中的許多程式碼範例都是以 [tests](./../move-basics/testing) 的形式撰寫，並使用框架中僅供測試使用的輔助函式：`tx_context::dummy()` 會建立一個佔位用的交易情境，而 `std::unit_test::destroy` 會在測試結束時消耗掉任何值。我們會在 [Testing](./../testing) 章節詳細介紹測試技巧。
