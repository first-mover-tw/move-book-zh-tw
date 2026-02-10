// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: config
module book::config;

const ITEM_PRICE: u64 = 100;
const TAX_RATE: u64 = 10;
const SHIPPING_COST: u64 = 5;

/// 回傳商品的價格。
public fun item_price(): u64 { ITEM_PRICE }
/// 回傳稅率。
public fun tax_rate(): u64 { TAX_RATE }
/// 回傳運送成本。
public fun shipping_cost(): u64 { SHIPPING_COST }
// ANCHOR_END: config
