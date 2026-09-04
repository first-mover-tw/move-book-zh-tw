---
description: Move 測試的建造者模式 (Builder pattern)：使用合理的預設值與方法串鏈建立複雜的測試物件，提升測試可讀性。
title: 模式：建造者 (Builder)
keywords:
  - Move
  - Sui
  - Move tutorial
  - pattern
  - builder
  - design patterns
questions:
  - 'What is Pattern: Builder in Move?'
  - 'How do I use Pattern: Builder in Move?'
  - What is Defining a Builder in Move?
  - What is Method Chaining in Move?
answer: 'The Builder pattern for Move tests: construct complex test objects with sensible defaults and method chaining for readable tests.'
goal:
  description: 'Reader understands the Builder pattern for Move tests: construct complex test objects with sensible defaults and method chaining for readable tests'
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

# 模式：建造者 (Pattern: Builder) {#pattern-builder}

建造者模式用於以靈活且易讀的方式建構具有許多參數的複雜物件。建造者不需要預先提供所有參數，而是透過函式呼叫累積設定，並在呼叫 `build()` 時產生最終物件。此模式尤其適合測試，因為你經常需要建立僅有些微差異的物件，同時讓大多數欄位維持合理的預設值。

> 在已發布的原始碼中，建造者模式可能因中介 struct 與多次函式呼叫而增加額外的 gas 成本。此模式最適合 gas 考量無須顧慮、但需要可讀性與可維護性的測試。

## 定義建造者 (Defining a Builder) {#defining-a-builder}

建造者 struct 會對應目標物件的欄位，但會將其包裝為 `Option` 型別。這讓每個欄位都能維持未設定狀態，直到明確完成設定。典型的建造者會提供：

- 用於建立空白建造者的 `new()` 函式
- 用於設定個別欄位並回傳建造者以便鏈結呼叫的 setter 方法
- 使用未設定欄位的預設值建構最終物件的 `build()` 函式

```move file=packages/samples/sources/testing/builder_pattern.move anchor=user

```

對應的建造者：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=user_builder

```

此處的 `new()` 函式會將所有欄位初始化為 `option::none()`，代表「未設定」狀態。每個 setter 方法都會將提供的值包裝為 `option::some()`，並儲存在對應欄位中。此模式的關鍵是 `build()` 函式，它使用 `destroy_or!` 巨集解包每個 `Option`：若欄位已設定，便使用其值；否則，巨集會回傳第二個引數提供的預設值。此方式讓測試只需指定所關心的欄位，同時確保最終物件一律會完整初始化。

## 使用範例 (Example Usage) {#example-usage}

未使用建造者時，每個測試都必須指定所有欄位，即使測試只與其中一個欄位有關：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_without_builder

```

使用建造者後，測試會更聚焦且具自我說明性：

```move file=packages/samples/sources/testing/builder_pattern_builder.move anchor=test_with_builder

```

每個測試都能清楚顯示哪個欄位重要。若要為 `User` 新增欄位，只需更新建造者的 `build()` 函式並加入預設值——既有測試無須變更。

## 方法鏈結 (Method Chaining) {#method-chaining}

流暢建造者語法的關鍵是方法鏈結。每個 setter 方法會依值接收 `mut self`、修改它，並回傳修改後的建造者。以下是非常常見的範例：

```move
public fun is_active(mut self: UserBuilder, is_active: bool): UserBuilder {
    self.is_active = option::some(is_active);
    self
}
```

因為此方法取得 `self` 的所有權並回傳 `UserBuilder`，你可以將多個呼叫串連在一起：

```move
let user = user_builder::new()
    .name("Alice")
    .balance(1000)
    .is_active(true)
    .build();
```

鏈結中的每個方法都會消耗前一個建造者，並回傳新的建造者。最終的 `build()` 呼叫會消耗建造者並產生目標物件。

## 在系統套件中的使用方式 (Usage in system packages) {#usage-in-system-packages}

Sui Framework 與 Sui System 套件廣泛使用建造者進行測試。最顯著的範例如下：

### Sui System 中的 ValidatorBuilder (ValidatorBuilder in Sui System) {#validatorbuilder-in-sui-system}

`Sui System` 套件中的 [`ValidatorBuilder`][validator-builder] 展示了適用於多欄位複雜型別的完整建造者——包含密碼學金鑰、網路地址與經濟參數：

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

    // 測試驗證器操作……
}
```

`preset(index)` 函式會針對數個預先定義驗證器中的其中一個，回傳已預先填入有效測試預設值——金鑰、地址與經濟參數——的建造者，因此測試只需覆寫所關心的欄位。

### Sui Framework 中的 TxContextBuilder (TxContextBuilder in Sui Framework) {#txcontextbuilder-in-sui-framework}

[`TxContextBuilder`][tx-context-builder] 可讓你針對特定測試情境自訂交易 context。建造者會傳遞給 `begin_with_context()` 以啟動情境，或傳遞給 `next_with_context()` 以推進既有情境：

```move
use sui::test_scenario as ts;

#[test]
fun test_epoch_dependent_logic() {
    let mut test = ts::begin_with_context(
        ts::ctx_builder_from_sender(@0x1)
            .set_epoch(100)
            .set_epoch_timestamp(1_000_000),
    );

    // 測試依賴 epoch 的邏輯……

    test.end();
}
```

## 總結 (Summary) {#summary}

- 建造者會透過 setter 方法累積設定，並透過 `build()` 產生最終物件。
- 使用 `Option` 欄位讓設定成為選用項目，並在 `build()` 中提供合理的預設值。
- 方法鏈結（`fun method(mut self, ...): Self`）可建立流暢 API。
- 建造者可減少測試樣板程式碼，並將測試與目標 struct 的變更隔離。
- 將此模式保留給可讀性比 gas 成本更重要的測試公用程式。

[validator-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-system/tests/builders/validator_builder.move
[tx-context-builder]: https://github.com/MystenLabs/sui/blob/main/crates/sui-framework/packages/sui-framework/sources/test/test_scenario.move
