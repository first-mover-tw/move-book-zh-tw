// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0
#[allow(unused_variable, unused_field)]
module book::generics;

#[test_only]
use std::unit_test::assert_eq;

// ANCHOR: container
/// 任何類型 `T` 的容器。
public struct Container<T> has drop {
    value: T,
}

/// 使用泛型值 `T` 建立新 `Container` 的函式。
public fun new<T>(value: T): Container<T> {
    Container { value }
}
// ANCHOR_END: container

// ANCHOR: test_container
#[test]
fun test_container() {
    // 這三行是等價的
    let container: Container<u8> = new(10); // 類型推論
    let container = new<u8>(10); // 建立具有 `u8` 值的新 `Container`
    let container = new(10u8);

    assert_eq!(container.value, 10);

    // 只有當值具有 `drop` 能力時才能忽略它。
    let Container { value: _ } = container;
}
// ANCHOR_END: test_container

// ANCHOR: pair
/// 任何類型 `T` 和 `U` 的值對。
public struct Pair<T, U> {
    first: T,
    second: U,
}

/// 使用兩個泛型值 `T` 和 `U` 建立新 `Pair` 的函式。
public fun new_pair<T, U>(first: T, second: U): Pair<T, U> {
    Pair { first, second }
}
// ANCHOR_END: pair

// ANCHOR: test_pair
#[test]
fun test_generic() {
    // 這三行是等價的
    let pair_1: Pair<u8, bool> = new_pair(10, true); // 類型推論
    let pair_2 = new_pair<u8, bool>(10, true); // 建立具有 `u8` 和 `bool` 值的新 `Pair`
    let pair_3 = new_pair(10u8, true);

    assert_eq!(pair_1.first, 10);
    assert_eq!(pair_1.second, true);

    // 解構是相同的。
    let Pair { first: _, second: _ } = pair_1;
    let Pair { first: _, second: _ } = pair_2;
    let Pair { first: _, second: _ } = pair_3;

}
// ANCHOR_END: test_pair

// ANCHOR: test_pair_swap
#[test]
fun test_swap_type_params() {
    let pair1: Pair<u8, bool> = new_pair(10u8, true);
    let pair2: Pair<bool, u8> = new_pair(true, 10u8);

    // 此行將無法編譯
    // assert_eq!(pair1, pair2);

    let Pair { first: pf1, second: ps1 } = pair1; // first1: u8, second1: bool
    let Pair { first: pf2, second: ps2 } = pair2; // first2: bool, second2: u8

    assert_eq!(pf1, ps2); // 10 == 10
    assert_eq!(ps1, pf2); // true == true
}
// ANCHOR_END: test_pair_swap

use std::string::String;

// ANCHOR: user
/// 具有名稱、年齡和某些泛型中繼資料的使用者記錄
public struct User<T> {
    name: String,
    age: u8,
    /// 根據應用程式而異。
    metadata: T,
}
// ANCHOR_END: user

// ANCHOR: update_user
/// 更新使用者的名稱。
public fun update_name<T>(user: &mut User<T>, name: String) {
    user.name = name;
}

/// 更新使用者的年齡。
public fun update_age<T>(user: &mut User<T>, age: u8) {
    user.age = age;
}
// ANCHOR_END: update_user

// ANCHOR: phantom
/// 具有虛擬類型參數的泛型類型。
public struct Coin<phantom T> {
    value: u64
}
// ANCHOR_END: phantom

// ANCHOR: test_phantom
public struct USD {}
public struct EUR {}

#[test]
fun test_phantom_type() {
    let coin1: Coin<USD> = Coin { value: 10 };
    let coin2: Coin<EUR> = Coin { value: 20 };

    // 解構是相同的，因為未使用虛擬類型參數。
    let Coin { value: _ } = coin1;
    let Coin { value: _ } = coin2;
}
// ANCHOR_END: test_phantom

// ANCHOR: constraints
/// 具有具有 `drop` 能力的類型參數的泛型類型。
public struct Droppable<T: drop> {
    value: T,
}

/// 具有具有 `copy` 和 `drop` 能力的類型參數的泛型結構。
public struct CopyableDroppable<T: copy + drop> {
    value: T, // T 必須具有 `copy` 和 `drop` 能力
}
// ANCHOR_END: constraints

// ANCHOR: test_constraints
/// 沒有任何能力的類型。
public struct NoAbilities {}

#[test]
fun test_constraints() {
    // 失敗 - `NoAbilities` 沒有 `drop` 能力
    // let droppable = Droppable<NoAbilities> { value: 10 };

    // 失敗 - `NoAbilities` 沒有 `copy` 和 `drop` 能力
    // let copyable_droppable = CopyableDroppable<NoAbilities> { value: 10 };
}
// ANCHOR_END: test_constraints
