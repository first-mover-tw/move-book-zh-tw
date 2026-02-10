// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: emit
module book::events;

use sui::coin::Coin;
use sui::sui::SUI;
use sui::event;

/// 可購買的項目。
public struct Item has key { id: UID }

/// 購買項目時發出的事件。包含項目的 ID 和
/// 購買價格。
public struct ItemPurchased has copy, drop {
    item: ID,
    price: u64
}

/// 執行項目購買的市場函式。
public fun purchase(coin: Coin<SUI>, ctx: &mut TxContext) {
    let item = Item { id: object::new(ctx) };

    // 建立 `ItemPurchased` 的實例並將其傳遞給 `event::emit`。
    event::emit(ItemPurchased {
        item: object::id(&item),
        price: coin.value()
    });

    // 省略實現的其餘部分以保持範例簡潔。
    abort
}
// ANCHOR_END: emit
