// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::witness_definition;

// ANCHOR: definition
/// Witness 的規範定義 - 一個具有 `drop` 能力的類型。
public struct MyWitness has drop {}
// ANCHOR_END: definition

// ANCHOR: regulated_coin
/// 一個可實現函式的自訂 RegulatedCoin 類型。
public struct RegulatedCoin<phantom T> has key {
    id: UID,
    value: u64
}

/// 受保護的函式 - 需要一個 Witness。
/// 鑄造一個新的 `RegulatedCoin`，具有指定的值。
public fun mint<T: drop>(_: T, value: u64, ctx: &mut TxContext): RegulatedCoin<T> {
    RegulatedCoin { id: object::new(ctx), value }
}

/// 受保護的函式 - 需要一個 Witness。
/// 銷毀 `RegulatedCoin` 並回傳其值。
public fun burn<T: drop>(_: T, coin: RegulatedCoin<T>): u64 {
    let RegulatedCoin { id, value } = coin;
    id.delete();
    value
}

/// 受保護的函式 - 需要一個 Witness。
public fun transfer<T: drop>(_: T, coin: RegulatedCoin<T>, to: address) {
    transfer::transfer(coin, to)
}

/// 公開 API - 不需要 Witness。
public fun join<T>(coin: &mut RegulatedCoin<T>, other: RegulatedCoin<T>) {
    let RegulatedCoin { id, value } = other;
    coin.value = coin.value + value;
    id.delete();
}
// ANCHOR_END: regulated_coin
