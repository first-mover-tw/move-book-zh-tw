---
description: init 函式 (init function) in Move：在 Sui 上模組發布時執行一次性初始化程式碼，包含規則與最佳實踐。
---

# 模組初始化函式 (Module Initializer) {#module-initializer}

在許多應用中,常見的使用情境是在套件發布時只執行某段程式碼一次。想像一個簡單的商店模組,需要在發布時建立主要的 `Shop` 物件。在 Sui 中,這是透過在模組內定義 `init` 函式來達成的。此函式會在模組發布時自動被呼叫。

> 套件中每個模組的 `init` 函式都會在發布過程中被呼叫。這個行為僅限於 publish 指令,不會延伸到套件升級 —— 升級時新增的模組不會呼叫其 `init`。

```move file=packages/samples/sources/programmability/module-initializer.move anchor=main

```

在同一個套件中,另一個模組可以有自己的 `init` 函式,封裝各自不同的邏輯。

```move file=packages/samples/sources/programmability/module-initializer-2.move anchor=other

```

## `init` 規則 (The `init` Rules) {#the-init-rules}

若模組中存在此函式,則會在發布時被呼叫,並遵循以下規則:

- 函式必須命名為 `init`、必須是 private,且不能有回傳值;
- 不能宣告為 `entry`,也不能有型別參數;
- 接受一個或兩個參數:一個選用的 [One Time Witness](./one-time-witness) 以及
  [TxContext](./transaction-context),`TxContext` 永遠是最後一個參數。

```move
fun init(ctx: &mut TxContext) { /* ... */ }
fun init(otw: OTW, ctx: &mut TxContext) { /* ... */ }
```

這些規則不只是慣例 —— 它們由 bytecode verifier 強制執行。任何違反這些規則的 `init` 函式都會驗證失敗,套件將無法發布。

`TxContext` 也可以以不可變參考 `&TxContext` 的形式傳入,但實務上應該一律使用 `&mut TxContext`:`init` 函式無法存取鏈上狀態,因此建立新物件正是它存在的意義所在 —— 而這需要對 context 的可變參考。

## 信任與安全性 (Trust and Security) {#trust-and-security}

雖然 `init` 函式可以用來只建立一次敏感物件,但重要的是要知道,同一個物件(例如第一個範例中的 `ShopOwnerCap`)仍然可以在另一個函式中被建立 —— 特別是因為在升級過程中可以為模組新增新函式。`init` 函式很適合用來設定模組的初始狀態,但它本身並不是一種安全措施。

有一些方法可以保證物件只被建立一次,例如 [One Time Witness](./one-time-witness)。也有一些方法可以限制或停用套件升級,詳見 Sui 文件中的
[自訂升級策略 (Custom Upgrade Policies)](https://docs.sui.io/concepts/sui-move-concepts/packages/custom-policies)。

## 測試初始化函式 (Testing the Initializer) {#testing-the-initializer}

`init` 函式由 runtime 呼叫,無法在交易中被呼叫。然而,就其他方面而言它是一個一般的函式,因此位於同一模組中的[測試](./../move-basics/testing)可以直接呼叫它:

```move file=packages/samples/sources/programmability/module-initializer.move anchor=test

```

對於接受 [One Time Witness](./one-time-witness) 的 `init` 函式,可以在測試中使用僅供測試使用的 `sui::test_utils::create_one_time_witness` 函式來建立 witness 值。而在 [Test Scenario](./../testing/test-scenario) 章節所描述的以情境為基礎的測試中,由 `init` 建立的物件也可以在呼叫後被檢查。

## 下一步 (Next Steps) {#next-steps}

如同其定義所述,`init` 函式保證只會在模組發布時被呼叫一次。因此它很適合用來放置初始化模組物件、設定環境與組態的程式碼。

舉例來說,如果某項操作需要一個 [Capability](./capability),它應該要在 `init` 函式中被建立。在下一章中,我們將更詳細地討論 `Capability` 模式。
