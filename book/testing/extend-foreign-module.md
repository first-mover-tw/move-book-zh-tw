---
description: '在 Move 測試中擴充外部模組：向外部套件添加測試專用函式，以建立測試數據和模擬物件。'
---

# 擴充模組 (Extending Modules)

在測試依賴於外部套件的程式碼時，你經常需要為這些套件中定義的型別建立測試數據。然而，許多函式庫不提供測試工具，讓你無法建構測試所需的物件。模組擴充透過允許你向外部模組添加測試專用 (test-only) 函式來解決這個問題。

## 問題

考慮一個使用 [Pyth Network](https://pyth.network/) 進行價格餵價的應用程式。你的程式碼依賴於 Pyth 套件中的 `PriceInfoObject` 來獲取資產價格：

```move
module app::trading;

use pyth::price_info::PriceInfoObject;
use pyth::price::{Self, Price};

/// 使用來自 Pyth 預言機的當前價格執行交易
public fun execute_trade(/* ... */ price_info: &PriceInfoObject, amount: u64): u64 {
    let price = get_price(price_info);
    // ... 使用價格的交易邏輯
    amount * price / 1_000_000
}

fun get_price(price_info: &PriceInfoObject): u64 {
    // 從預言機物件中提取價格
    // ...
    0 // 佔位符
}
```

要測試 `execute_trade`，你需要一個 `PriceInfoObject`。但 Pyth 的 Sui 實作沒有提供 `create_price_info_for_testing` 函式 —— 獲取 `PriceInfoObject` 的唯一方法是透過實際的預言機更新，這在單元測試中是不切實際的。

如果沒有擴充，你的選擇很有限：

- 跳過依賴價格的邏輯測試 (危險)
- Fork 並修改 Pyth 套件 (維護負擔)

## 什麼是擴充？

擴充允許你向現有模組添加函式 —— 即使是來自外部套件的模組。擴充後的函式可以存取該模組的私有型別，並且可以建立、讀取或修改它們。這是使用 `extend` 關鍵字來表達的：

```move
#[test_only]
extend module pyth::price_info;

// 現在你可以定義能夠存取 pyth::price_info 私有型別和函式的函式了
```

擴充具有以下特點：

- **僅限添加**：擴充只能添加新的宣告；它們不能修改或刪除目標模組中的現有項目
- **套件本地性**：它們不會影響下游依賴或原始套件。只有在根套件中定義的擴充才會被應用 —— 依賴項中的擴充會被忽略
- **模式限制**：擴充需要模式屬性，最常見的是用於測試的 `#[test_only]`
- **強大**：它們具有對被擴充模組內部的完全存取權限，就像程式碼直接寫在該模組中一樣

## 解決 Pyth 問題

以下是如何使用擴充為 `PriceInfoObject` 建立測試輔助工具。首先，建立一個擴充檔案：

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

    // 使用我們的擴充建立測試價格數據
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

## 專案結構

將擴充組織在專用資料夾中是一個好的做法：

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

這將測試工具與生產程式碼分開，並清楚表明哪些模組已被擴充。

## 擴充你自己的模組

擴充不僅限於外部套件 —— 你也可以擴充自己套件中的模組。這對於添加測試輔助工具很有用，而無需使用 `#[test_only]` 函式弄亂你的生產程式碼：

```move
#[test_only]
extend module app::trading;

/// 用於檢查內部狀態的測試輔助工具
public fun get_internal_value(/* ... */): u64 {
    // 為測試存取私有欄位
}

#[test]
fun test_internal_invariant() {
    // 測試可以與擴充中的輔助工具並存
}
```

## 其他使用案例

除了預言機 Mock 之外，擴充還適用於：

- **建立和銷毀具有私有欄位的物件**：當依賴項未公開其型別的建構子時
- **透過公開存取器暴露內部狀態**：當你需要在測試中驗證內部不變量 (internal invariants) 時
- **模擬行為**：當你需要模擬難以正常達到的特定狀態時
- **測試錯誤條件**：當你需要建立無效狀態以測試錯誤處理時

## 限制

擴充有一些需要注意的重要限制：

- **需要模式屬性**：擴充必須具有像 `#[test_only]` 這樣的模式屬性。使用 `#[test_only]` 時，擴充僅在執行 `sui move test` 時起作用，無法在生產構建中使用。
- **僅限添加**：你只能添加新的宣告 (函式、型別、常數、use 語句)。你不能修改、覆蓋或遮蔽目標模組中的現有項目。
- **僅限根套件**：只有在你的根套件中定義的擴充才會被應用。如果依賴項定義了擴充，它們在你的構建中會被忽略。
- **版本相容性**：擴充程式碼受制於與目標模組相同的版本 (edition) 功能。如果目標模組使用較舊的版本，你的擴充程式碼必須與該版本相容。
- **版本要求**：擴充需要 `2024.alpha` 版本或更高版本。確保你的 `Move.toml` 指定了相容的版本。

## 延伸閱讀

- [模組擴充 | 參考](./../../reference/extensions) - 擴充語法和語義的詳細規範
- [在 Sui 中整合 Pyth](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/sui)
- [應用程式範例：預言機](https://docs.sui.io/guides/developer/app-examples/oracle)
