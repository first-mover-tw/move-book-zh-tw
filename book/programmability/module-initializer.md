---
description: Move (Move) 中的初始化函式 (init function)：在 Sui (Sui) 上發布模組 (module) 時執行一次性設定原始碼，包含規則與最佳實務。
title: 模組初始化器 (Module Initializer)
keywords:
  - Move
  - Sui
  - Move tutorial
  - module
  - initializer
  - modules
questions:
  - What is Module Initializer in Move?
  - How do I use Module Initializer in Move?
  - What is The init Rules in Move?
  - What is Trust and Security in Move?
answer: 'The init function in Move: run one-time setup code when a module is published on Sui, with rules and best practices.'
goal:
  description: 'Reader understands the init function in Move: run one-time setup code when a module is published on Sui, with rules and best practices'
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

# 模組初始化器 (Module Initializer) {#module-initializer}

許多應用程式的常見使用案例是在套件發布時僅執行一次特定程式碼。想像一個簡單的商店模組，需要在發布時建立主要的 `Shop` 物件。在 Sui 中，這可透過在模組內定義 `init` 函式來達成。發布模組時，此函式會自動被呼叫。

> 套件中每個模組的 `init` 函式都會在發布過程中被呼叫。此行為僅限於發布命令，並不會延伸至套件升級——在升級中新增的模組不會呼叫其 `init`。

```move file=packages/samples/sources/programmability/module-initializer.move anchor=main

```

在同一個套件中，另一個模組可以擁有自己的 `init` 函式，以封裝不同的邏輯。

```move file=packages/samples/sources/programmability/module-initializer-2.move anchor=other

```

## `init` 規則 (The `init` Rules) {#the-init-rules}

如果模組中存在該函式，且符合以下規則，則會在發布時呼叫：

- 函式必須命名為 `init`、為私有函式，且沒有回傳值；
- 不可宣告為 `entry`，也不可具有型別參數；
- 它接受一或兩個引數：可選的 [One Time Witness](./one-time-witness) 與 [TxContext](./transaction-context)，其中 `TxContext` 一律為最後一個引數。

```move
fun init(ctx: &mut TxContext) { /* ... */ }
fun init(otw: OTW, ctx: &mut TxContext) { /* ... */ }
```

這些規則並非慣例，而是由位元組碼驗證器強制執行。名為 `init` 但違反其中任一規則的函式將無法通過驗證，套件也無法發布。

`TxContext` 也可以採用不可變參考 `&TxContext`，但實務上應一律使用 `&mut TxContext`：`init` 函式無法存取鏈上狀態，因此建立新物件才是它的核心目的——而這需要情境的可變參考。

## 信任與安全性 (Trust and Security) {#trust-and-security}

雖然 `init` 函式可用於一次性建立敏感物件，但務必了解，同一個物件（例如第一個範例中的 `ShopOwnerCap`）仍可在其他函式中建立——尤其是因為可在升級期間將新函式加入模組。`init` 函式是設定模組初始狀態的合適位置，但它本身並不是一項安全措施。

有一些方法可保證物件只會建立一次，例如 [One Time Witness](./one-time-witness)。也有一些方法可限制或停用套件升級，詳見 Sui 文件中的 [Custom Upgrade Policies](https://docs.sui.io/concepts/sui-move-concepts/packages/custom-policies)。

## 測試初始化器 (Testing the Initializer) {#testing-the-initializer}

`init` 函式由執行階段呼叫，且無法在交易中呼叫。不過，它在其他所有方面都是一般函式，因此放在同一模組中的[測試](./../move-basics/testing)可以直接呼叫它：

```move file=packages/samples/sources/programmability/module-initializer.move anchor=test

```

對於接受 [One Time Witness](./one-time-witness) 的 `init` 函式，可在測試中使用僅供測試使用的 `sui::test_utils::create_one_time_witness` 函式建立 witness 值。而在情境式測試中，如 [Test Scenario](./../testing/test-scenario) 章節所述，也可以在呼叫後檢查由 `init` 建立的物件。

## 後續步驟 (Next Steps) {#next-steps}

如定義所述，模組發布時保證只會呼叫 `init` 函式一次。因此，這是放置初始化模組物件，以及設定環境與組態之程式碼的合適位置。

例如，如果某些動作需要 [Capability](./capability)，則應在 `init` 函式中建立它。在下一章中，我們將更詳細說明 `Capability` 模式。
