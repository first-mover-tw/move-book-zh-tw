// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
module book::vector_syntax {
#[test_only]
use std::unit_test::assert_eq;
#[test] fun test_vector() {
// ANCHOR: literal
// 一個空的布林元素向量。
let empty: vector<bool> = vector[];

// 一個 u8 元素的向量。
let v: vector<u8> = vector[10, 20, 30];

// 一個 vector<u8> 元素的向量。
let vv: vector<vector<u8>> = vector[
    vector[10, 20],
    vector[30, 40]
];
// ANCHOR_END: literal
}

#[test] fun vector_methods() {
// ANCHOR: methods
let mut v = vector[10u8, 20, 30];

assert_eq!(v.length(), 3);
assert_eq!(v.is_empty(), false);

v.push_back(40);
let last_value = v.pop_back();

assert_eq!(last_value, 40);
// ANCHOR_END: methods
}
}


module book::non_droppable_vec {

// ANCHOR: no_drop
/// 沒有 `drop` 能力的結構體。
public struct NoDrop {}

#[test]
fun test_destroy_empty() {
    // 初始化一個 `NoDrop` 元素的向量。
    let v = vector<NoDrop>[];

    // 雖然我們知道 `v` 是空的，我們仍然需要呼叫
    // 明確的 `destroy_empty` 函式來丟棄向量。
    v.destroy_empty();
}
// ANCHOR_END: no_drop
}
