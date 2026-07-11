---
description: 'Move 測試的 Builder 模式：建構具有合理預設值的複雜測試物件，並使用方法鏈 (method chaining) 撰寫可讀的測試。'
---

# 模式：Builder (Builder Pattern)

Builder 模式用於以靈活且可讀的方式建構具有許多參數的複雜物件。Builder 不需要預先提供所有參數，而是透過方法調用累積配置，並在調用 `build()` 時生成最終物件。這種模式在測試中特別有用，因為你經常需要建立物件的細微變體，同時保持大多數字元段為合理的預設值。

> 在已發布的程式碼中，Builder 模式可能會因為中間結構體 (structs) 和多個函式調用而引入額外的 Gas 成本。此模式最適合用於不用顧慮 Gas 考量的測試中，並且要求可讀性和可維護性。

## 定義 Builder

Builder 結構體映射目標物件的欄位，但將它們包裝在 `Option` 型別中。這允許每個欄位保持未設定狀態，直到明確配置。一個典型的 Builder 提供：

- `new()` 函式，建立一個空的 builder
- Setter 方法，配置個別欄位並回傳 builder 以進行鏈式調用
- `build()` 函式，使用未設定欄位的預設值來建構最終物件

```move file=packages/samples/sources/testing/builder_pattern.move anchor=user

```

對應的 builder：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=user_builder

```

在這裡，`new()` 函式將所有欄位初始化為 `option::none()`，代表「未配置」狀態。每個 setter 方法將提供的值包裝在 `option::some()` 中並將其存儲在相應的欄位中。該模式的關鍵在於 `build()` 函式，它使用 `destroy_or!` 巨集來解包每個 `Option`：如果欄位已配置，則使用其值；否則，該巨集會回傳作為第二個參數提供的預設值。這種方法讓測試只指定它們關心的欄位，同時確保最終物件始終完全初始化。

## 使用範例

如果沒有 Builder，每個測試都必須指定所有欄位，即使只有一個欄位與測試相關：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_without_builder

```

有了 Builder，測試變得專注且自我文檔化 (self-documenting)：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_with_builder

```

每個測試都清楚地顯示哪個欄位重要。向 `User` 添加新欄位只需要更新 builder 的 `build()` 函式並提供預設值 —— 現有的測試保持不變。

## 方法鏈 (Method Chaining)

流暢的 Builder 語法的關鍵是方法鏈。每個 setter 方法按值 (by value) 接收 `mut self`，修改它，並回傳修改後的 builder。這是一個非常常見的例子：

```move
public fun is_active(mut self: UserBuilder, is_active: bool): UserBuilder {
    self.is_active = option::some(is_active);
    self
}
```

因為該方法取得了 `self` 的所有權並回傳 `UserBuilder`，你可以將多個調用鏈接在一起：

```move
let user = user_builder::new()
    .name("Alice")
    .balance(1000)
    .is_active(true)
    .build();
```

鏈中的每個方法消耗前一個 builder 並回傳一個新的。最後的 `build()` 調用消耗 builder 並生成目標物件。

## 在系統套件中的使用

Sui Framework 和 Sui System 套件在測試中廣泛使用 builders。最顯著的例子是：

### Sui System 中的 ValidatorBuilder

`sui-system` 套件中的 [`ValidatorBuilder`][validator-builder] 展示了一個用於具有許多欄位的複雜型別（加密密鑰、網路地址和經濟參數）的綜合 builder：

```move
use sui_system::validator_builder;

#[test]
fun test_validator_operations() {
    let validator = validator_builder::preset()
        .name("My Validator")
        .gas_price(1000)
        .commission_rate(500) // 5%
        .initial_stake(100_000_000)
        .build(ctx);

    // 測試驗證者操作...
}
```

`preset()` 函式回傳一個預填了有效測試預設值的 builder，因此測試只需要覆蓋它們關心的欄位。

### Sui Framework 中的 TxContextBuilder

[`TxContextBuilder`][tx-context-builder] 允許為特定測試場景自定義交易上下文：

```move
use sui::test_scenario as ts;

#[test]
fun test_epoch_dependent_logic() {
    let mut test = ts::begin(@0x1);
    let ctx = test
        .ctx_builder()
        .set_epoch(100)
        .set_epoch_timestamp(1000000)
        .build();

    // 依賴於 epoch 的測試邏輯...

    test.end();
}
```

## 總結

- Builder 透過 setter 方法累積配置，並透過 `build()` 生成最終物件。
- 使用 `Option` 欄位使配置可選，並在 `build()` 中提供合理的預設值。
- 方法鏈 (`fun method(mut self, ...): Self`) 創建流暢的 API。
- Builders 減少了測試樣板代碼 (boilerplate)，並將測試與目標結構體的變更隔離開來。
- 將此模式保留給測試工具，在這些工具中可讀性比 Gas 成本更重要。

[validator-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-system/tests/builders/validator_builder.move
[tx-context-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-framework/sources/test/test_scenario.move
