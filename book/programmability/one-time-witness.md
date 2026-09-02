---
description: Sui Move 中的一次性見證 (One Time Witness, OTW)：保證只能被實例化一次的型別，用於建立 Publisher 與 Coin。
---

# One Time Witness 一次性見證 (One Time Witness) {#one-time-witness}

雖然一般的 [Witness](./witness-pattern) 是靜態證明型別所有權的好方法，但有些情況我們需要確保某個 witness 只會被實例化一次——這正是一次性見證（One Time Witness，OTW）存在的目的。

## 背景 (Background) {#background}

為了了解 OTW 要解決的問題，讓我們試著用現有的工具建構一個簡單的泛型 coin 實作。`TreasuryCap<T>` 控制型別 `T` 的 coin 供應量，而建立一個 `TreasuryCap<T>` 需要 `T` 的 [witness](./witness-pattern)：

```move
module book::simple_coin;

/// 控制 Coin 的供給。
public struct TreasuryCap<phantom T> has key, store {
    id: UID,
    total_supply: u64,
}

/// 用 witness 建立一個新的 `TreasuryCap`。
/// 有漏洞：沒有任何機制阻止呼叫者用同一個 witness
/// 建立多個 `TreasuryCap<T>`！
public fun new<T: drop>(_witness: T, ctx: &mut TxContext): TreasuryCap<T> {
    TreasuryCap { id: object::new(ctx), total_supply: 0 }
}
```

一般的 witness 證明了呼叫模組擁有型別 `T`，但它並不能證明這個 witness 曾經——或未來將——被建構了*幾次*。一個不誠實的開發者可以直接呼叫 `new` 兩次，把第二個 treasury 留給自己：

```move
module book::simple_coin_cheater;

/// Coin witness……被用了兩次。>_<
public struct MOVE has drop {}

fun init(ctx: &mut TxContext) {
    let treasury = book::simple_coin::new(MOVE {}, ctx);
    let secret_treasury = book::simple_coin::new(MOVE {}, ctx);

    transfer::public_transfer(treasury, ctx.sender());
    transfer::public_transfer(secret_treasury, ctx.sender());
}
```

對於任何要決定是否信任以這種方式建構出來的 coin 的人來說，有一整份清單需要稽核：確認針對給定的 `T` 只存在一個 `TreasuryCap`、確認該模組沒有後門可以發行更多、以及確認未來的升級不會新增這樣的後門。這些條件沒有一個能在 Move 程式碼內被檢查——要驗證它們，必須信任作者，並且反覆仔細審查原始碼。

為了消除這種信任需求，Sui 引入了一次性見證——一種由系統本身保證只會被實例化恰好一次、且可在執行期檢查的 witness。

## 定義 (Definition) {#definition}

OTW 是一種特殊的 witness，只能被使用一次。它無法手動建立，並且保證在每個模組中都是唯一的。只要符合以下規則，Sui 執行環境就會將某個型別視為 OTW：

1. 只具有 `drop` 能力。
2. 沒有欄位。
3. 不是泛型型別。
4. 以全大寫字母命名，且與模組同名。

以下是 OTW 的範例：

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=definition

```

OTW 無法手動建構，任何嘗試這麼做的程式碼都會導致編譯錯誤。OTW 可以作為 [模組初始化函式](./module-initializer) 的第一個引數被接收。而由於 `init` 函式在每個模組中只會被呼叫一次，因此可以保證 OTW 也只會被實例化一次。

## 強制檢查 OTW (Enforcing the OTW) {#enforcing-the-otw}

要檢查某個型別是否為 OTW，[Sui Framework](./sui-framework) 的 `sui::types` 模組提供了一個特殊函式 `is_one_time_witness`。這是上述規則在執行期的對應：一個預期接收 OTW 的函式庫函式應該呼叫它，以確保收到的 witness 是真正的一次性 witness，而不是一個只是具有 `drop` 能力的一般型別。

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=usage

```

正是這一行 `assert!` 修正了 [背景](#background) 小節中的 coin 範例的問題：如果 `simple_coin::new` 要求的是 OTW 而非一般的 witness，那麼 cheater 模組中的第二次呼叫就會失敗，因為 OTW 實例只會存在一次——也就是第一次呼叫時。

## 總結 (Summary) {#summary}

OTW 模式是確保某個型別只被使用一次的絕佳方法。大多數開發者只需要知道如何定義與接收 OTW，而檢查與強制執行則主要是函式庫與框架需要關心的事。舉例來說，`sui::coin` 模組在 `coin::create_currency` 方法中要求提供 OTW，藉此強制 `coin::TreasuryCap` 只會被建立一次——這正好解決了我們在 [背景](#background) 小節中描述的問題。

OTW 是一項強大的工具，為 [Publisher](./publisher) 物件奠定了基礎，我們將在下一節介紹它。
