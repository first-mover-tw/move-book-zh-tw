---
description: "Move 測試的建構器模式：使用合理的預設值和方法鏈來構建複雜的測試物件，提高可讀性。"
---

# 模式：建構器 (Builder Pattern)

建構器模式用於以靈活且可讀的方式構建具有許多參數的複雜物件。建構器不是要求預先提供所有參數，而是通過方法呼叫累積設定，並在呼叫 `build()` 時產生最終的物件。這個模式在測試中特別有用，因為你經常需要建立只有細微差異的物件，同時保持大多數欄位使用合理的預設值。

> 在已發佈的程式碼中，建構器模式可能會因為中間結構體和多個函式呼叫而引入額外的 gas 成本。這個模式最適合用於測試，其中 gas 考量不是問題，而可讀性和可維護性是必需的。

## 定義建構器

建構器結構體鏡像目標物件的欄位，但將它們包裝在 `Option` 類型中。這允許每個欄位保持未設定狀態，直到顯式配置。典型的建構器提供：

- 一個 `new()` 函式，用來建立一個空的建構器
- 設定器方法，用來配置個別欄位並返回建構器以進行鏈式呼叫
- 一個 `build()` 函式，使用預設值為未設定的欄位構建最終物件

```move file=packages/samples/sources/testing/builder_pattern.move anchor=user

```

對應的建構器：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=user_builder

```

這裡，`new()` 函式初始化所有欄位為 `option::none()`，表示「未配置」狀態。每個設定器方法將提供的值包裝在 `option::some()` 中並將其存儲在對應的欄位中。這個模式的關鍵是 `build()` 函式，它使用 `destroy_or!` 巨集來展開每個 `Option`：如果一個欄位已被配置，就使用它的值；否則，巨集返回作為第二個參數提供的預設值。這個方法讓測試只需要指定它們關心的欄位，同時確保最終物件始終完全初始化。

## 使用範例

沒有建構器時，每個測試必須指定所有欄位，即使只有一個欄位與測試相關：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_without_builder

```

使用建構器時，測試變得專注且自我記述：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_with_builder

```

每個測試清楚地顯示哪個欄位重要。向 `User` 添加新欄位時只需更新建構器的 `build()` 函式中的預設值 - 現有測試保持不變。

## 方法鏈

流暢的建構器語法的關鍵是方法鏈。每個設定器方法按值取得 `mut self`，修改它並返回修改後的建構器。這是一個非常常見的例子：

```move
public fun is_active(mut self: UserBuilder, is_active: bool): UserBuilder {
    self.is_active = option::some(is_active);
    self
}
```

因為方法取得 `self` 的所有權並返回 `UserBuilder`，你可以鏈式連接多個呼叫：

```move
let user = user_builder::new()
    .name("Alice")
    .balance(1000)
    .is_active(true)
    .build();
```

鏈中的每個方法消費前一個建構器並返回一個新的。最終的 `build()` 呼叫消費建構器並產生目標物件。

## 在系統套件中的使用

Sui 框架和 Sui 系統套件在測試中廣泛使用建構器。最值得注意的例子是：

### Sui 系統中的 ValidatorBuilder

`sui-system` 套件中的 [`ValidatorBuilder`][validator-builder] 展示了一個複雜類型（具有許多欄位 - 密碼學金鑰、網路位址和經濟參數）的全面建構器：

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

    // 測試驗證器操作...
}
```

`preset()` 函式返回一個預先填充有效測試預設值的建構器，因此測試只覆蓋它們關心的欄位。

### Sui 框架中的 TxContextBuilder

[`TxContextBuilder`][tx-context-builder] 允許為特定測試情景自訂交易上下文：

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

    // 測試依賴於 epoch 的邏輯...

    test.end();
}
```

## 總結

- 建構器通過設定器方法累積設定，並通過 `build()` 產生最終物件。
- 使用 `Option` 欄位使設定為可選，在 `build()` 中使用合理的預設值。
- 方法鏈（`fun method(mut self, ...): Self`）建立流暢的 API。
- 建構器減少測試樣板程式碼並隔離測試，使其不受目標結構體變更的影響。
- 在可讀性比 gas 成本更重要的測試工具中保留此模式。

[validator-builder]:
  https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-system/tests/builders/validator_builder.move
[tx-context-builder]:
  https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-framework/sources/test/test_scenario.move
