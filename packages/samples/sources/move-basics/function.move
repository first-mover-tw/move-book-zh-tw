// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_function, unused_let_mut)]
// ANCHOR: math
module book::math;

#[test_only]
use std::unit_test::assert_eq;

/// 函式接受 `u64` 類型的兩個引數並回傳它們的總和。
/// `public` 可見性修飾符使函式可從
/// 模組外部存取。
public fun add(a: u64, b: u64): u64 {
    a + b
}

#[test]
fun test_add() {
    let sum = add(1, 2);
    assert_eq!(sum, 3);
}
// ANCHOR_END: math

// ANCHOR: return_nothing
fun return_nothing() {
    // 空運算式，函式回傳 `()`
}
// ANCHOR_END: return_nothing

// ANCHOR: tuple_return
fun get_name_and_age(): (vector<u8>, u8) {
    (b"John", 25)
}
// ANCHOR_END: tuple_return

#[test] fun test_get_name_and_age() {
// ANCHOR: tuple_return_imm
// 必須解構元組以存取其元素。
// 名稱和年齡被宣告為不可變變數。
let (name, age) = get_name_and_age();
assert_eq!(name, b"John");
assert_eq!(age, 25);
// ANCHOR_END: tuple_return_imm

// ANCHOR: tuple_return_mut
// 將名稱宣告為可變，年齡為不可變
let (mut name, age) = get_name_and_age();
// ANCHOR_END: tuple_return_mut

// ANCHOR: tuple_return_ignore
// 忽略名稱，僅使用年齡
let (_, age) = get_name_and_age();
// ANCHOR_END: tuple_return_ignore
}
