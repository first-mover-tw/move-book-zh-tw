---
description: Move 測試的建構器模式 (Builder pattern)：以合理預設值與方法鏈 (method chaining) 建構複雜的測試物件，讓測試更易讀。
---

# Pattern: Builder 建構器模式 (Pattern: Builder) {#pattern-builder}

builder 模式用於以彈性且可讀的方式建構具有許多參數的複雜物件。builder 不需要一開始就提供所有參數，而是透過方法呼叫累積設定，並在呼叫 `build()` 時產生最終物件。這個模式在測試中特別有用，因為你經常需要建立帶有些微差異的物件，同時讓大部分欄位保持在合理的預設值。

> 在正式發布的程式碼中，builder 模式可能因為中間結構與多次函式呼叫而引入額外的 gas 成本。這個模式最適合用在不需要考慮 gas、且需要可讀性與可維護性的測試中。

## 定義 Builder (Defining a Builder) {#defining-a-builder}

builder 結構會鏡射目標物件的欄位，但將它們包在 `Option` 型別中。這讓每個欄位在明確設定前都能維持未設定狀態。典型的 builder 會提供：

- 一個建立空 builder 的 `new()` 函式
- 設定個別欄位並回傳 builder 以便鏈式呼叫的 setter 方法
- 一個 `build()` 函式，會為未設定的欄位使用預設值來建構最終物件

```move file=packages/samples/sources/testing/builder_pattern.move anchor=user

```

對應的 builder：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=user_builder

```

在這裡，`new()` 函式將所有欄位初始化為 `option::none()`，代表「未設定」狀態。每個 setter 方法會將傳入的值包在 `option::some()` 中，並儲存到對應的欄位。這個模式的關鍵在於 `build()` 函式，它使用 `destroy_or!` 巨集來解開每個 `Option`：如果欄位已被設定，就使用其值；否則巨集會回傳作為第二個引數提供的預設值。這種做法讓測試只需指定它們關心的欄位，同時確保最終物件永遠完全初始化。

## 使用範例 (Example Usage) {#example-usage}

如果沒有 builder，每個測試都必須指定所有欄位，即使只有一個欄位與該測試相關：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_without_builder

```

有了 builder，測試變得聚焦且能自我說明：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_with_builder

```

每個測試都清楚顯示哪個欄位是重點。為 `User` 新增欄位時，只需要更新 builder 的 `build()` 函式加入預設值——既有的測試維持不變。

## 方法鏈式呼叫 (Method Chaining) {#method-chaining}

流暢 builder 語法的關鍵在於方法鏈式呼叫。每個 setter 方法以值的方式接收 `mut self`，修改後回傳修改過的 builder。以下是一個很常見的範例：

```move
public fun is_active(mut self: UserBuilder, is_active: bool): UserBuilder {
    self.is_active = option::some(is_active);
    self
}
```

因為該方法取得 `self` 的所有權並回傳 `UserBuilder`，你可以將多個呼叫鏈接在一起：

```move
let user = user_builder::new()
    .name("Alice")
    .balance(1000)
    .is_active(true)
    .build();
```

鏈式呼叫中的每個方法都會消耗前一個 builder 並回傳一個新的 builder。最後的 `build()` 呼叫會消耗 builder 並產生目標物件。

## 在系統套件中的使用 (Usage in system packages) {#usage-in-system-packages}

Sui Framework 與 Sui System 套件廣泛使用 builder 進行測試。最值得注意的範例是：

### Sui System 中的 ValidatorBuilder (ValidatorBuilder in Sui System) {#validatorbuilder-in-sui-system}

`sui-system` 套件中的 [`ValidatorBuilder`][validator-builder] 展示了一個針對具有許多欄位（加密金鑰、網路位址、經濟參數）的複雜型別的完整 builder：

```move
use sui_system::validator_builder;

#[test]
fun test_validator_operations() {
    let ctx = &mut tx_context::dummy();
    let validator = validator_builder::preset(1)
        .name("My Validator")
        .gas_price(1000)
        .commission_rate(500) // 5%
        .initial_stake(100_000_000)
        .build(ctx);

    // 測試 validator 操作...
}
```

`preset(index)` 函式會回傳一個預先填入有效測試預設值——金鑰、位址與經濟參數——的 builder，對應數個預先定義的 validator 之一，所以測試只需覆寫它們關心的欄位。

### Sui Framework 中的 TxContextBuilder (TxContextBuilder in Sui Framework) {#txcontextbuilder-in-sui-framework}

[`TxContextBuilder`][tx-context-builder] 允許為特定測試情境自訂交易上下文。這個 builder 會被傳給 `begin_with_context()` 以開始一個情境，或傳給 `next_with_context()` 以推進既有的情境：

```move
use sui::test_scenario as ts;

#[test]
fun test_epoch_dependent_logic() {
    let mut test = ts::begin_with_context(
        ts::ctx_builder_from_sender(@0x1)
            .set_epoch(100)
            .set_epoch_timestamp(1_000_000),
    );

    // 依賴 epoch 的測試邏輯...

    test.end();
}
```

## 總結 (Summary) {#summary}

- builder 透過 setter 方法累積設定，並透過 `build()` 產生最終物件。
- 使用 `Option` 欄位讓設定成為可選項，並在 `build()` 中提供合理的預設值。
- 方法鏈式呼叫（`fun method(mut self, ...): Self`）建立了流暢的 API。
- builder 減少測試樣板程式碼，並將測試與目標結構的變動隔離開來。
- 將這個模式保留給可讀性比 gas 成本更重要的測試工具使用。

[validator-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-system/tests/builders/validator_builder.move
[tx-context-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-framework/sources/test/test_scenario.move
