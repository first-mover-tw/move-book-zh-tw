---

description: "One Time Witness (OTW) in Sui Move: a type guaranteed to be instantiated only once, used for Publisher and Coin creation."
---

# 一次性見證 (One Time Witness)

雖然一般的 [見證 (Witness)](./witness-pattern) 是靜態證明類型所有權的一種絕佳方式，但在某些情況下，我們需要確保見證僅被實例化一次。這就是「一次性見證 (One Time Witness, OTW)」的用途。

<!--
Notes to self:
  - background first or definition first
 - which one is better?                   - why would someone read this section?
  - if we removed the OTW from docs, then we should give definition first.      -->

## 定義

OTW 是一種特殊的見證類型，只能使用一次。它無法手動建立，且保證在每個模組中都是唯一的。如果一個類型遵循以下規則，Sui 適配器 (Adapter) 就會將其視為 OTW：

1. 僅具有 `drop` 能力。
2. 沒有任何欄位。
3. 不是泛型類型。
4. 名稱與模組名稱相同，但全為大寫字母。

以下是 OTW 的範例：

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=definition

```

OTW 無法手動建構，任何嘗試建構它的程式碼都會導致編譯錯誤。OTW 可以作為 [模組初始化器 (module initializer)](./module-initializer) 的第一個參數接收。由於 `init` 函式在每個模組中僅被呼叫一次，因此保證了 OTW 僅被實例化一次。

## 強制執行 OTW

要檢查一個類型是否為 OTW，[Sui 框架](./sui-framework) 的 `sui::types` 模組提供了一個特殊的函式 `is_one_time_witness`，可以用來驗證該類型是否為 OTW。

```move file=packages/samples/sources/programmability/one-time-witness.move anchor=usage

```

<!-- ## Background

Before we get to actual definition of the OTW, let's consider a simple example. We want to build a generic implementation of a Coin type, which can be initialized with a witness. A instance of a witness `T` is used to create a new `TreasuryCap<T>` which is then used to mint a new `Coin<T>`.                             
```move
module book::simple_coin {

    /// Controls the supply of the Coin.
    public struct TreasuryCap<phantom T> has key, store {
        id: UID,
        total_supply: u64,
    }

    /// The Coin type where the `T` is a witness.
    public struct Coin<phantom T> has key, store {
        id: UID,
        value: u64,
    }

    /// Create a new TreasuryCap with a witness.
    /// Vulnerable: we can create multiple TreasuryCap<T> with the same witness.
    public fun new<T: drop>(_: T, ctx: &mut TxContext): TreasuryCap<T> {
        TreasuryCap { id: object::new(ctx), total_supply: 0 }
    }

    /// We use a regular witness to authorize the minting.
    public fun mint<T>(
        treasury: &mut TreasuryCap<T>,
        value: u64,
        ctx: &mut TxContext
    ) {
        treasury.total_supply = treasury.total_supply + value;
        Coin { id: object::new(ctx), value }
    }
}
```

A dishonest developer would be able to create multiple `TreasuryCap`s with the same witness, and mint more `Coin`s than expected. Here is an example of such a malicious module:                        
```move
module book::simple_coin_cheater {
    /// The Coin witness.
    public struct Move has drop {}

    /// Initialize the TreasuryCap with the Move witness.
    /// ...and do it twice! >_<
    fun init(ctx: &mut TxContext) {
        let treasury_cap = book::simple_coin::new(Move {}, ctx);
        let secret_treasury = book::simple_coin::new(Move {}, ctx);
             
        transfer::public_transfer(treasury_cap, ctx.sender())
        transfer::public_transfer(secret_treasury, ctx.sender())
    }
}

```

The example above has no protection against issuing multiple `TreasuryCap`s with the same witness, and in real-world application, this creates a problem of trust. If it was a human decision to support a Coin based on this implementation, they would have to make sure that:        
- there is only one `TreasuryCap` for a given `T`.
- the module cannot be upgraded to issue more `TreasuryCap`s.
- the module code does not contain any backdoors to issue more `TreasuryCap`s.
  
However, it is not possible to check any of these conditions inside the Move code. And to prevent the need for trust, Sui introduces the OTW pattern.           
## Solving the Coin Problem

To solve the case of multiple `TreasuryCaps`, we can use the OTW pattern. By defining the `COIN_OTW` type as an OTW, we can ensure that the `COIN_OTW` is used only once. The `COIN_OTW` is then used to create a new `TreasuryCap` and mint a new `Coin`.                              
```move

With

```move
module book::coin_otw {

    /// The OTW for the `book::coin_otw` module.
    struct COIN_OTW has drop {}

    /// Receive the instance of `COIN_OTW` as the first argument.
    fun init(otw: COIN_OTW, ctx: &mut TxContext) {
        let treasury_cap = book::simple_coin::new(COIN_OTW {}, ctx);
        transfer::public_transfer(treasury_cap, ctx.sender())
    }
}
```


 -->

<!-- ## Case Study: Coin

TODO: add a story behind TreasuryCap and Coin                                   
-->

## 總結

OTW 模式是確保某種類型僅被使用一次的絕佳方式。大多數開發人員應該理解如何定義和接收 OTW，而 OTW 的檢查和強制執行主要出現在函式庫和框架中。例如，`sui::coin` 模組在 `coin::create_currency` 方法中要求傳入 OTW，從而強制確保 `coin::TreasuryCap` 僅被建立一次。

OTW 是一個強大的工具，它為 [發佈者 (Publisher)](./publisher) 物件奠定了基礎，我們將在下一節中介紹。

<!--

## Questions
- What other ways could be used to prevent multiple `TreasuryCaps`?
- Are there any other ways to use the OTW?                                      
 -->
