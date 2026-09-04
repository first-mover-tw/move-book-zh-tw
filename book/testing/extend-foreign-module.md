---
description: 在 Move (Move) 測試中擴充外部模組：將僅供測試使用的函式新增至外部套件，以建立測試資料與模擬物件。
title: 擴充模組 (Modules)
keywords:
  - Move
  - Sui
  - Move tutorial
  - extending
  - modules
questions:
  - What is Extending Modules in Move?
  - How do I use Extending Modules in Move?
  - What is The Problem in Move?
  - What is an Extension?
answer: 'Extend foreign modules in Move tests: add test-only functions to external packages for creating test data and mock objects.'
goal:
  description: 'Reader understands extend foreign modules in Move tests: add test-only functions to external packages for creating test data and mock objects'
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

# 擴充模組 (Extending Modules) {#extending-modules}

測試依賴外部套件的程式碼時，你通常需要為這些套件中定義的型別建立測試資料。然而，許多函式庫未提供測試工具，導致你無法建構測試所需的物件。模組擴充功能可讓你將僅供測試使用的函式新增至外部模組，以解決此問題。

> 此功能目前僅適用於 `2024.alpha` 版本。
> 若要使用此功能，你需要在 `Move.toml` 中指定版本：
>
> ```toml
> [package]
> edition = "2024.alpha"
> ```

## 問題 (The Problem) {#the-problem}

假設某個應用程式使用 [Pyth Network](https://pyth.network/) 取得價格饋送。你的程式碼依賴 Pyth 套件中的 `PriceInfoObject` 來取得資產價格：

```move
module app::trading;

use pyth::price_info::PriceInfoObject;
use pyth::price::{Self, Price};

/// 使用來自 Pyth 預言機的目前價格執行交易
public fun execute_trade(/* ... */ price_info: &PriceInfoObject, amount: u64): u64 {
    let price = get_price(price_info);
    // ... 使用價格的交易邏輯
    amount * price / 1_000_000
}

fun get_price(price_info: &PriceInfoObject): u64 {
    // 從預言機物件擷取價格
    // ...
    0 // 佔位值
}
```

若要測試 `execute_trade`，你需要一個 `PriceInfoObject`。但 Pyth 的 Sui 實作沒有提供
`create_price_info_for_testing` 函式；取得 `PriceInfoObject` 的唯一方式是透過實際的預言機更新，這在單元測試中並不實際。

若沒有擴充功能，你的選項有限：

- 略過價格相依邏輯的測試（危險）
- 分支並修改 Pyth 套件（維護負擔）

## 什麼是擴充功能？ (What is an Extension?) {#what-is-an-extension}

擴充功能可讓你將函式新增至現有模組，即使該模組來自外部套件也可以。
擴充的函式可存取模組的私有型別，並可建立、讀取或修改這些型別。
這會使用 `extend` 關鍵字表示：

```move
#[test_only]
extend module pyth::price_info;

// 現在你可以定義能夠存取
// pyth::price_info 私有型別與函式的函式
```

擴充功能具有以下特性：

- **僅可新增**：擴充功能只能新增宣告；無法修改或移除目標模組中的既有項目
- **僅限你的套件**：不會影響下游依賴項或原始套件。只有根套件中定義的擴充功能會被套用；依賴項中的擴充功能會被忽略
- **受模式限制**：擴充功能需要模式屬性，最常見的是用於測試的 `#[test_only]`
- **功能強大**：它們能完整存取被擴充模組的內部項目，如同程式碼直接寫在該模組中

## 解決 Pyth 問題 (Solving the Pyth Problem) {#solving-the-pyth-problem}

以下說明如何使用擴充功能為 `PriceInfoObject` 建立測試輔助工具。首先，建立一個擴充檔案：

```move
// tests/extensions/pyth_price_info_ext.move
#[test_only]
extend module pyth::price_info;

public fun new_price_info_object_for_testing(
    price_info: PriceInfo,
    ctx: &mut TxContext,
): PriceInfoObject {
    PriceInfoObject {
        id: object::new(ctx),
        price_info,
    }
}
```

現在你可以撰寫適當的單元測試：

```move
#[test_only]
module app::trading_tests;

use app::trading;
use pyth::price_info;
use std::unit_test::{Self, assert_eq};

#[test]
fun test_execute_trade_with_price() {
    let ctx = &mut tx_context::dummy();

    // 使用我們的擴充功能建立測試價格資料
    let price_info = price_info::new_price_info_object_for_testing(
        /* ... */
        ctx,
    );

    // 測試交易邏輯
    let result = trading::execute_trade(&price_info, 1000);
    assert_eq!(result, 50_000);

    // 清理
    unit_test::destroy(price_info);
}
```

## 專案結構 (Project Structure) {#project-structure}

最佳實務是將擴充功能整理至專用資料夾：

```
my_project/
├── sources/
│   └── trading.move
├── tests/
│   ├── extensions/
│   │   └── pyth_price_info_ext.move
│   └── trading_tests.move
└── Move.toml
```

這能讓測試工具與正式環境程式碼分開，並清楚表明哪些模組已被擴充。

## 擴充你自己的模組 (Extending Your Own Modules) {#extending-your-own-modules}

擴充功能不限於外部套件；你也可以擴充自己套件中的模組。
這對於新增測試輔助工具很有用，不必在正式環境程式碼中加入 `#[test_only]`
函式而造成雜亂：

```move
#[test_only]
extend module app::trading;

/// 用於檢查內部狀態的測試輔助工具
public fun get_internal_value(/* ... */): u64 {
    // 存取私有欄位以進行測試
}

#[test]
fun test_internal_invariant() {
    // 測試可與擴充功能中的輔助工具放在一起
}
```

## 其他使用案例 (Other Use Cases) {#other-use-cases}

除了預言機模擬物件以外，擴充功能也適用於：

- **建立及銷毀具有私有欄位的物件**：當依賴項未公開其型別的建構子時
- **透過公開存取子公開內部狀態**：當你需要在測試中驗證內部不變數時
- **模擬行為**：當你需要模擬平時難以達成的特定狀態時
- **測試錯誤條件**：當你需要建立無效狀態來測試錯誤處理時

## 限制 (Limitations) {#limitations}

擴充功能有一些重要限制需要留意：

- **需要模式屬性**：擴充功能必須具有如 `#[test_only]` 的模式屬性。使用
  `#[test_only]` 時，擴充功能僅能在執行 `sui move test` 時運作，且不能用於正式環境建置。
- **僅可新增**：你只能新增宣告（函式、型別、常數、use
  陳述式）。你無法修改、覆寫或遮蔽目標模組中的既有項目。
- **僅限根套件**：只有根套件中定義的擴充功能會被套用。若依賴項定義了擴充功能，則會在你的建置中被忽略。
- **版本相容性**：擴充功能程式碼須遵循與目標模組相同的版本功能。若目標模組使用較舊版本，你的擴充功能程式碼必須與該版本相容。
- **版本需求**：擴充功能目前僅適用於 `2024.alpha` 版本。
  請確認你的 `Move.toml` 已指定該版本。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Module Extensions | Reference](./../../reference/extensions) - 擴充功能語法與語意的詳細規格
- [Integrating Pyth in Sui](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/sui)
