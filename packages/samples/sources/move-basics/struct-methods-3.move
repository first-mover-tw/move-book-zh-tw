// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: hero_to_bytes
// TODO: better example (external module...)
module book::hero_to_bytes;

// Alias for the `bcs::to_bytes` method. Imported aliases should be defined
// in the top of the module.
// public use fun bcs::to_bytes as Hero.to_bytes;

/// 代表英雄的結構體。
public struct Hero has drop {
    health: u8,
    mana: u8,
}

/// 建立新的英雄。
public fun new(): Hero { Hero { health: 100, mana: 100 } }

// #[test_only]
// use std::unit_test::assert_eq;

#[test]
// 測試 `Hero` 結構體的方法。
fun test_hero_serialize() {
    // let mut hero = new();
    // let serialized = hero.to_bytes();
    // assert_eq!(serialized.length(), 3);
}
// ANCHOR_END: hero_to_bytes
