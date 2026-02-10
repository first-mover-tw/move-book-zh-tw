// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

/// 此模組包含一個回傳字串「Hello, World!」的函式。
module book::hello_world_docs;

use std::string::String;

/// 如名稱所說：回傳字串「Hello, World!」。
public fun hello_world(): String {
    b"Hello, World!".to_string()
}

#[test_only]
use std::unit_test::assert_eq;

#[test]
/// 這是對 `hello_world` 函式的測試。
fun test_is_hello_world() {
    let expected = b"Hello, World!".to_string();
    let actual = hello_world();

    assert_eq!(actual, expected);
}
