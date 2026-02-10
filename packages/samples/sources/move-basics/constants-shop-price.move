// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: shop_price
module book::shop_price;

use sui::{coin::Coin, sui::SUI};

/// 試圖以不正確的價格購買商品。
const EWrongPrice: u64 = 0;

/// 商店中商品的價格。
const ITEM_PRICE: u64 = 100;
/// 商店的所有者，一個位址。
const SHOP_OWNER: address = @0xa11ce;

/// 在商店中銷售的商品。
public struct Item {}

/// 從商店購買商品。
public fun purchase(coin: Coin<SUI>): Item {
    assert!(coin.value() == ITEM_PRICE, EWrongPrice);

    transfer::public_transfer(coin, SHOP_OWNER);

    Item {}
}
// ANCHOR_END: shop_price
