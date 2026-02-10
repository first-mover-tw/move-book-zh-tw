// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: hero
module book::hero;

/// 代表英雄的結構體。
public struct Hero has drop {
    health: u8,
    mana: u8,
}

/// 建立新的英雄。
public fun new(): Hero { Hero { health: 100, mana: 100 } }

/// 施放法術的方法，消耗法力值。
public fun heal_spell(hero: &mut Hero) {
    hero.health = hero.health + 10;
    hero.mana = hero.mana - 10;
}

/// 回傳英雄生命值的方法。
public fun health(hero: &Hero): u8 { hero.health }

/// 回傳英雄法力值的方法。
public fun mana(hero: &Hero): u8 { hero.mana }

#[test_only]
use std::unit_test::assert_eq;

#[test]
// 測試 `Hero` 結構體的方法。
fun test_methods() {
    let mut hero = new();
    hero.heal_spell();

    assert_eq!(hero.health(), 110);
    assert_eq!(hero.mana(), 90);
}
// ANCHOR_END: hero
