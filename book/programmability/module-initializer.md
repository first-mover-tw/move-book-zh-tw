# 模組初始化器 (Module Initializer)

許多應用程式中一個常見的使用案例是在套件發佈時僅執行一次某些程式碼。想像一個簡單的商店模組，它需要在發佈時建立主要的「商店 (Store)」物件。在 Sui 中，這是透過在模組內定義 `init` 函式來實現的。該函式將在模組發佈時自動被呼叫。

> 所有模組的 `init` 函式都會在發佈過程中被呼叫。目前，此行為僅限於發佈 (publish) 指令，並不延伸到套件升級。
>
> <!-- [package upgrades]() -->

```move file=packages/samples/sources/programmability/module-initializer.move anchor=main

```

在同一個套件中，另一個模組也可以有自己的 `init` 函式，封裝不同的邏輯。

```move file=packages/samples/sources/programmability/module-initializer-2.move anchor=other

```

## `init` 的特性

如果模組中存在該函式並遵循以下規則，則會在發佈時被呼叫：

- 函式名稱必須為 `init`，為私有 (private) 且沒有傳回值。
- 接收一或二個參數：[一次性見證 One Time Witness](./one-time-witness)（選填）以及 [TxContext](./transaction-context)。`TxContext` 始終作為最後一個參數。

```move
fun init(ctx: &mut TxContext) { /* ... */}
fun init(otw: OTW, ctx: &mut TxContext) { /* ... */ }
```

TxContext 也可以作為不可變參考傳遞：`&TxContext`。然而，從實際操作來看，它應該始終是 `&mut TxContext`，因為 `init` 函式無法存取鏈上狀態，且建立新物件需要對上下文的可變參考。

```move
fun init(ctx: &TxContext) { /* ... */}
fun init(otw: OTW, ctx: &TxContext) { /* ... */ }
```

## 信任與安全 (Trust and Security)

雖然 `init` 函式可以用於一次性建立敏感物件，但重要的是要了解同一個物件（例如第一個範例中的 `StoreOwnerCap`）仍然可以在另一個函式中建立。特別是考慮到在升級期間可以向模組添加新函式。因此，`init` 函式是設置模組初始狀態的好地方，但它本身並非一種安全措施。

有一些方法可以保證物件僅被建立一次，例如 [一次性見證 (One Time Witness)](./one-time-witness)。此外，也有一些方法可以限制或停用模組的升級，我們將在「套件升級 (Package Upgrades)」章節中討論。

## 下一步 (Next Steps)

根據定義，`init` 函式保證在模組發佈時僅被呼叫一次。因此，它是放置初始化模組物件、設置環境和配置的程式碼的好地方。

例如，如果某個操作需要 [能力 (Capability)](./capability)，則應在 `init` 函式中建立它。在下一章中，我們將詳細討論 `Capability` 模式。
