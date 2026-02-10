---
description: "在 Move 測試中擴展外部模組：為外部套件新增僅測試用函式，以建立測試資料和模擬物件。"
---

# 擴展模組 (Extending Modules)

當測試依賴外部套件的程式碼時，你經常需要為這些套件中定義的型別建立測試資料。然而，許多程式庫並未提供測試工具，使你無法建構測試所需的物件。模組擴展透過允許你為外部模組新增僅測試用函式來解決此問題。

## 問題陳述 (The Problem)

考慮一個使用 [Pyth Network](https://pyth.network/) 進行價格饋送的應用程式。你的程式碼依賴 Pyth 套件中的 `PriceInfoObject` 來取得資產價格：

```move
module app::trading;

use pyth::price_info::PriceInfoObject;
use pyth::price::{Self, Price};

/// 使用 Pyth 預言機的目前價格執行交易
public fun execute_trade(/* ... */ price_info: &PriceInfoObject, amount: u64): u64 {
    let price = get_price(price_info);
    // ... 使用價格進行交易邏輯
    amount * price / 1_000_000
}

fun get_price(price_info: &PriceInfoObject): u64 {
    // 從預言機物件提取價格
    // ...
    0 // 佔位符
}
```

若要測試 `execute_trade`，你需要一個 `PriceInfoObject`。但 Pyth 的 Sui 實作並未提供 `create_price_info_for_testing` 函式——獲得 `PriceInfoObject` 的唯一方式是透過實際預言機更新，這在單元測試中並不實用。

沒有擴展的情況下，你的選擇有限：

- 跳過測試與價格相關的邏輯（危險）
- 分叉並修改 Pyth 套件（維護負擔）

## 什麼是擴展？ (What is an Extension?)

擴展允許你為現有模組新增函式——即使是來自外部套件的模組。擴展函式可存取模組的私有型別，並可建立、讀取或修改它們。這是透過 `extend` 關鍵字表達的：

```move
#[test_only]
extend module pyth::price_info;

// 現在你可以定義函式，可存取
// pyth::price_info 的私有型別和函式
```

擴展具有以下特性：

- **僅增加型**：擴展只能新增宣告；無法修改或刪除目標模組中的現有項目
- **本地於你的套件**：它們不影響下游依賴或原始套件。只有根套件中定義的擴展才會被套用——依賴中的擴展會被忽略
- **模式限制**：擴展需要模式屬性，最常見的是用於測試的 `#[test_only]`
- **強大**：它們對擴展模組的內部有完整存取權限，如同程式碼直接寫在該模組中一樣

## 解決 Pyth 問題 (Solving the Pyth Problem)

以下是如何使用擴展為 `PriceInfoObject` 建立測試輔助函式。首先，建立一個擴展檔案：

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

現在你可以編寫正確的單元測試：

```move
#[test_only]
module app::trading_tests;

use app::trading;
use pyth::price_info;
use std::unit_test::{Self, assert_eq};

#[test]
fun test_execute_trade_with_price() {
    let ctx = &mut tx_context::dummy();

    // 使用我們的擴展建立測試價格資料
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

## 專案結構 (Project Structure)

將擴展組織在專用資料夾中是一個好實踐：

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

這樣可以將測試工具與生產程式碼分開，並清楚地表明哪些模組已被擴展。

## 擴展自己的模組 (Extending Your Own Modules)

擴展不限於外部套件——你也可以擴展自己套件中的模組。這在新增測試輔助函式時很有用，無需用 `#[test_only]` 函式污染生產程式碼：

```move
#[test_only]
extend module app::trading;

/// 測試輔助函式以檢查內部狀態
public fun get_internal_value(/* ... */): u64 {
    // 存取私有欄位進行測試
}

#[test]
fun test_internal_invariant() {
    // 測試可與擴展中的輔助函式並存
}
```

## 其他用途 (Other Use Cases)

除了預言機模擬外，擴展還用於：

- **建立和銷毀具有私有欄位的物件**：當依賴未暴露其型別的建構函式時
- **透過公開存取子暴露內部狀態**：當你需要驗證測試中的內部不變式時
- **模擬行為**：當你需要模擬通常難以到達的特定狀態時
- **測試錯誤條件**：當你需要建立無效狀態以測試錯誤處理時

## 限制 (Limitations)

擴展有重要的限制需要注意：

- **需要模式屬性**：擴展必須具有模式屬性，如 `#[test_only]`。使用 `#[test_only]` 時，擴展僅在執行 `sui move test` 時有效，無法用於生產構建。
- **僅增加型**：你只能新增宣告（函式、型別、常數、使用陳述式）。無法修改、覆蓋或遮蔽目標模組中的現有項目。
- **僅根套件**：只有根套件中定義的擴展才會被套用。如果依賴定義了擴展，它們在你的構建中會被忽略。
- **版本相容性**：擴展程式碼受到與目標模組相同的版本功能限制。如果目標模組使用較舊版本，你的擴展程式碼必須與該版本相容。
- **版本要求**：擴展需要 `2024.alpha` 版本或更新版本。確保你的 `Move.toml` 指定了相容的版本。

## 進一步閱讀 (Further Reading)

- [模組擴展 | 參考資料](./../../reference/extensions) - 擴展語法和語義的詳細規範
- [在 Sui 中整合 Pyth](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/sui)
- [應用示例：預言機](https://docs.sui.io/guides/developer/app-examples/oracle)
