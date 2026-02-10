// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: hero_and_villain
module book::hero_and_villain;

/// 代表英雄的結構體。
public struct Hero has drop {
    health: u8,
}

/// 代表反派的結構體。
public struct Villain has drop {
    health: u8,
}

/// 建立新的英雄。
public fun new_hero(): Hero { Hero { health: 100 } }

/// 建立新的反派。
public fun new_villain(): Villain { Villain { health: 200 } }

// `hero_health` 方法的別名。在模組被導入時將自動被導入。
public use fun hero_health as Hero.health;

public fun hero_health(hero: &Hero): u8 { hero.health }

// `villain_health` 方法的別名。在模組被導入時將自動被導入。
public use fun villain_health as Villain.health;

public fun villain_health(villain: &Villain): u8 { villain.health }

#[test_only]
use std::unit_test::assert_eq;

#[test]
// 測試 `Hero` 和 `Villain` 結構體的方法。
fun test_associated_methods() {
    let hero = new_hero();
    assert_eq!(hero.health(), 100);

    let villain = new_villain();
    assert_eq!(villain.health(), 200);
}
// ANCHOR_END: hero_and_villain
