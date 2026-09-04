---
description: Sui Move 中的一次性見證 (One Time Witness, OTW)：保證只會被具現化一次的型別，用於建立發布者 (Publisher) 與代幣 (Coin)。
title: 一次性見證 (One Time Witness)
keywords:
  - Move
  - Sui
  - Move tutorial
  - one
  - time
  - witness
  - witness pattern
questions:
  - What is One Time Witness in Move?
  - How do I use One Time Witness in Move?
  - What is Background in Move?
  - What is Definition in Move?
answer: 'One Time Witness (OTW) in Sui Move: a type guaranteed to be instantiated only once, used for Publisher and Coin creation.'
goal:
  description: 'Reader understands one Time Witness (OTW) in Sui Move: a type guaranteed to be instantiated only once, used for Publisher and Coin creation'
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

# 一次性見證 (One Time Witness) {#one-time-witness}

一般的 [Witness](./witness-pattern) 是靜態證明型別所有權的絕佳方式，但在某些情況下，我們需要確保見證只會被具現化一次——這正是一次性見證（One Time Witness，OTW）的用途。

## 背景 (Background) {#background}

為了解 OTW 所解決的問題，讓我們嘗試使用現有工具建置一個簡單的泛型代幣實作。`TreasuryCap<T>` 控制型別為 `T` 的代幣供應量，而建立它需要 `T` 的 [見證](./witness-pattern)：

```move
module book::simple_coin;

/// 控制 Coin 的供應量。
public struct TreasuryCap<phantom T> has key, store {
    id: UID,
    total_supply: u64,
}

/// 使用見證建立新的 `TreasuryCap`。
/// 弱點：沒有任何機制能阻止呼叫端使用相同見證建立
/// 多個 `TreasuryCap<T>`！
public fun new<T: drop>(_witness: T, ctx: &mut TxContext): TreasuryCap<T> {
    TreasuryCap { id: object::new(ctx), total_supply: 0 }
}
```

一般見證可證明呼叫模組擁有型別 `T`，但無法證明見證已經或將會被建構 _多少次_。不誠實的開發者可以直接呼叫 `new` 兩次，並將第二個金庫留給自己：

```move
module book::simple_coin_cheater;

/// Coin 見證……使用了兩次。>_<
public struct MOVE has drop {}

fun init(ctx: &mut TxContext) {
    let treasury = book::simple_coin::new(MOVE {}, ctx);
    let secret_treasury = book::simple_coin::new(MOVE {}, ctx);

    transfer::public_transfer(treasury, ctx.sender());
    transfer::public_transfer(secret_treasury, ctx.sender());
}
```

任何人在決定是否信任以此方式建置的代幣時，都必須稽核一整套條件：指定 `T` 是否只存在一個 `TreasuryCap`、模組是否沒有能額外發行代幣的後門，以及未來升級是否無法加入此類後門。這些條件無法從 Move 原始碼內部檢查——驗證它們需要信任作者，並仔細且重複檢閱原始碼。

為了不再需要這種信任，Sui 引入了一次性見證——由系統本身保證恰好只會具現化一次，且可於執行階段檢查的見證。

## 定義 (Definition) {#definition}

OTW 是只能使用一次的特殊見證型別。它無法手動建立，且保證在每個模組中都是唯一的。如果型別符合以下規則，Sui 執行環境會將其視為 OTW：

1. 僅具有 `drop` 能力。
2. 沒有欄位。
3. 不是泛型型別。
4. 名稱與模組名稱相同，且全部使用大寫字母。

以下是 OTW 的範例：

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=definition

```

OTW 無法手動建構，任何嘗試這麼做的原始碼都會導致編譯錯誤。OTW 可作為第一個引數傳入 [模組初始化函式](./module-initializer)。由於每個模組的 `init` 函式只會呼叫一次，因此 OTW 保證只會具現化一次。

## 強制執行 OTW (Enforcing the OTW) {#enforcing-the-otw}

為了檢查型別是否為 OTW，[Sui Framework](./sui-framework) 的 `sui::types` 模組提供了特殊函式 `is_one_time_witness`。這是上述規則在執行階段的對應機制：預期接收 OTW 的函式庫函式應呼叫它，以確認接收到的見證是真正的一次性見證，而不是僅具有 `drop` 能力的一般型別。

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=usage

```

這個單一的 `assert!` 修正了[背景](#background)章節中的代幣範例：若 `simple_coin::new` 要求的是 OTW 而非一般見證，作弊模組中的第二次呼叫便會失敗，因為 OTW 執行個體只存在一次——也就是第一次呼叫時。

## 總結 (Summary) {#summary}

OTW 模式是確保型別只會使用一次的絕佳方法。大多數開發者只需要知道如何定義及接收 OTW，而檢查與強制執行大多是函式庫與框架需要處理的事。例如，`sui::coin` 模組要求在 `coin::create_currency` 方法中使用 OTW，因此可強制確保 `coin::TreasuryCap` 只會建立一次——恰好解決了我們在[背景](#background)章節中描述的問題。

OTW 是強大的工具，為 [Publisher](./publisher) 物件奠定基礎；我們將在下一節介紹它。
