// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_function)]
// ANCHOR: module
module book::control_flow;
// ANCHOR_END: module

#[test_only]
use std::unit_test::assert_eq;

// ANCHOR: if_condition
#[test]
fun test_if() {
    let x = 5;

    // `x > 0` 是一個布林運算式。
    if (x > 0) {
        std::debug::print(&b"X is bigger than 0".to_string())
    };
}
// ANCHOR_END: if_condition
// ANCHOR: if_else
#[test]
fun test_if_else() {
    let x = 5;
    let y = if (x > 0) {
        1
    } else {
        0
    };

    assert_eq!(y, 1);
}
// ANCHOR_END: if_else
// ANCHOR: while_loop
// 此函式會迭代 `x` 變數直到達到 10，
// 回傳值是達到 10 所需的迭代次數。
//
// 如果 `x` 是 0，則函式會回傳 10。
// 如果 `x` 是 5，則函式會回傳 5。
fun while_loop(mut x: u8): u8 {
    let mut y = 0;

    // 此迴圈會執行直到 `x` 是 10。
    // 如果 `x` 是 10 或更大則永遠不會執行。
    while (x < 10) {
        y = y + 1;
        x = x + 1;
    };

    y
}

#[test]
fun test_while() {
    assert_eq!(while_loop(0), 10); // 10 次
    assert_eq!(while_loop(5), 5); // 5 次
    assert_eq!(while_loop(10), 0); // 迴圈從未執行
}
// ANCHOR_END: while_loop
// ANCHOR: infinite_while
#[test, expected_failure(out_of_gas, location=Self)]
fun test_infinite_while() {
    let mut x = 0;

    // 此迴圈會無限迴圈。
    while (true) {
        x = x + 1;
    };

    // 此行永遠不會被執行。
    assert_eq!(x, 5);
}
// ANCHOR_END: infinite_while
#[allow(dead_code)]
// ANCHOR: infinite_loop
#[test, expected_failure(out_of_gas, location=Self)]
fun test_infinite_loop() {
    let mut x = 0;

    // 此迴圈會無限迴圈。
    loop {
        x = x + 1;
    };

    // 此行永遠不會被執行。
    assert_eq!(x, 5);
}
// ANCHOR_END: infinite_loop
// ANCHOR: break_loop
#[test]
fun test_break_loop() {
    let mut x = 0;

    // 此迴圈會執行直到 `x` 是 5。
    loop {
        x = x + 1;

        // 如果 `x` 是 5，則退出迴圈。
        if (x == 5) {
            break // 退出迴圈。
        }
    };

    assert_eq!(x, 5);
}
// ANCHOR_END: break_loop
// ANCHOR: continue_loop
#[test]
fun test_continue_loop() {
    let mut x = 0;

    // 此迴圈會執行直到 `x` 是 10。
    loop {
        x = x + 1;

        // 如果 `x` 是奇數，則跳過迭代的其餘部分。
        if (x % 2 == 1) {
            continue // 跳過迭代的其餘部分。
        };

        std::debug::print(&x);

        // 如果 `x` 是 10，則退出迴圈。
        if (x == 10) {
            break // 退出迴圈。
        }
    };

    assert_eq!(x, 10) // 10
}
// ANCHOR_END: continue_loop
// ANCHOR: return_statement
/// 如果 `x` 大於 0 且不是 5 則此函式回傳 `true`，
/// 否則回傳 `false`。
fun is_positive(x: u8): bool {
    if (x == 5) {
        return false
    };

    if (x > 0) {
        return true
    };

    false
}

#[test]
fun test_return() {
    assert_eq!(is_positive(5), false);
    assert_eq!(is_positive(0), false);
    assert_eq!(is_positive(1), true);
}
// ANCHOR_END: return_statement
