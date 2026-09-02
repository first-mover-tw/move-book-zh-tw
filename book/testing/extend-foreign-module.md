---
description: 在 Move 測試中擴充外部模組 (Extend foreign modules in Move tests)：為外部套件新增僅供測試使用的函式，用於建立測試資料與模擬物件 (mock objects)。
---

# Extending Modules 擴充模組 (Extending Modules) {#extending-modules}

在測試依賴外部套件的程式碼時,你經常需要為這些套件中定義的型別建立測試資料。然而,許多函式庫並未提供測試工具,導致你無法建構測試所需的物件。模組擴充功能(Module extensions)透過允許你為外部模組新增僅供測試使用的函式,解決了這個問題。

> 此功能目前僅在 `2024.alpha` edition 中提供。
> 若要使用,你需要在 `Move.toml` 中指定 edition:
>
> ```toml
> [package]
> edition = "2024.alpha"
> ```

## 問題所在 (The Problem) {#the-problem}

考慮一個使用 [Pyth Network](https://pyth.network/) 取得價格資訊的應用程式。你的程式碼依賴 Pyth 套件中的 `PriceInfoObject` 來取得資產價格:

```move
module app::trading;

use pyth::price_info::PriceInfoObject;
use pyth::price::{Self, Price};

/// 使用來自 Pyth oracle 的當前價格執行交易
public fun execute_trade(/* ... */ price_info: &PriceInfoObject, amount: u64): u64 {
    let price = get_price(price_info);
    // ... 使用價格的交易邏輯
    amount * price / 1_000_000
}

fun get_price(price_info: &PriceInfoObject): u64 {
    // 從 oracle 物件中提取價格
    // ...
    0 // 佔位符
}
```

要測試 `execute_trade`,你需要一個 `PriceInfoObject`。但 Pyth 的 Sui 實作並未提供 `create_price_info_for_testing` 函式——取得 `PriceInfoObject` 的唯一方式是透過實際的 oracle 更新,而這在單元測試中並不實際可行。

沒有擴充功能的情況下,你的選項相當有限:

- 略過測試依賴價格的邏輯(危險)
- Fork 並修改 Pyth 套件(維護負擔)

## 什麼是擴充功能? (What is an Extension?) {#what-is-an-extension}

擴充功能允許你為既有模組——即使是來自外部套件的模組——新增函式。被擴充的函式可以存取該模組的私有型別,並能建立、讀取或修改它們。這是用 `extend` 關鍵字來表達的:

```move
#[test_only]
extend module pyth::price_info;

// 現在你可以定義能夠存取
// pyth::price_info 私有型別與函式的函式
```

擴充功能具有以下特性:

- **僅限新增**:擴充功能只能新增新的宣告;它們不能修改或移除目標模組中的既有項目
- **侷限於你的套件**:它們不會影響下游依賴或原始套件。只有定義在根套件(root package)中的擴充功能才會被套用——依賴套件中的擴充功能會被忽略
- **模式限制**:擴充功能需要一個模式屬性(mode attribute),最常見的是用於測試的 `#[test_only]`
- **功能強大**:它們對被擴充模組的內部具有完整存取權,就如同這些程式碼是直接寫在該模組中一樣

## 解決 Pyth 問題 (Solving the Pyth Problem) {#solving-the-pyth-problem}

以下說明如何使用擴充功能為 `PriceInfoObject` 建立測試輔助函式。首先,建立一個擴充檔案:

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

現在你可以撰寫正規的單元測試:

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

將擴充功能整理在專屬的資料夾中是良好的實務作法:

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

這使測試工具與正式程式碼保持分離,並清楚標示哪些模組已被擴充。

## 擴充你自己的模組 (Extending Your Own Modules) {#extending-your-own-modules}

擴充功能不僅限於外部套件——你也可以擴充自己套件中的模組。這對於新增測試輔助函式而不讓正式程式碼中充斥 `#[test_only]` 函式很有幫助:

```move
#[test_only]
extend module app::trading;

/// 用於檢查內部狀態的測試輔助函式
public fun get_internal_value(/* ... */): u64 {
    // 為測試存取私有欄位
}

#[test]
fun test_internal_invariant() {
    // 測試可以與輔助函式一同存在於擴充功能中
}
```

## 其他使用情境 (Other Use Cases) {#other-use-cases}

除了 oracle mock 之外,擴充功能還適用於:

- **建立與銷毀具有私有欄位的物件**:當依賴套件未曝露其型別的建構函式時
- **透過公開存取函式曝露內部狀態**:當你需要在測試中驗證內部不變數(invariant)時
- **模擬行為**:當你需要模擬難以在正常情況下觸及的特定狀態時
- **測試錯誤情況**:當你需要建立無效狀態以測試錯誤處理時

## 限制 (Limitations) {#limitations}

擴充功能有一些需要注意的重要限制:

- **需要模式屬性**:擴充功能必須具有像 `#[test_only]` 這樣的模式屬性。使用 `#[test_only]` 時,擴充功能只在執行 `sui move test` 時運作,無法用於正式環境的建置。
- **僅限新增**:你只能新增新的宣告(函式、型別、常數、use 陳述式)。你無法修改、覆寫或遮蔽(shadow)目標模組中的既有項目。
- **僅限根套件**:只有定義在你根套件中的擴充功能才會被套用。若某個依賴套件定義了擴充功能,在你的建置中會被忽略。
- **Edition 相容性**:擴充功能程式碼受目標模組相同的 edition 功能所限制。若目標模組使用較舊的 edition,你的擴充功能程式碼必須與該 edition 相容。
- **Edition 要求**:擴充功能目前僅在 `2024.alpha` edition 中提供。請確認你的 `Move.toml` 已指定該 edition。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Module Extensions | Reference](./../../reference/extensions) - 擴充功能語法與語意的詳細規格
- [Integrating Pyth in Sui](https://docs.pyth.network/price-feeds/core/use-real-time-data/pull-integration/sui)
