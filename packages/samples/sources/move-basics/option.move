// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
// ANCHOR: registry
module book::user_registry;

use std::string::String;

/// 代表使用者記錄的結構。
public struct User has drop {
    first_name: String,
    middle_name: Option<String>,
    last_name: String,
}

/// 使用給定的欄位建立新的 `User` 結構。
public fun register(
    first_name: String,
    middle_name: Option<String>,
    last_name: String,
): User {
    User { first_name, middle_name, last_name }
}
// ANCHOR_END: registry

#[test_only]
use std::unit_test::{assert_eq, assert_ref_eq};

#[test] fun use_option() {

// ANCHOR: usage
// `option::some` 建立包含值的 `Option` 值。
let mut opt = option::some(b"Alice");

// `option::none` 建立不含值的 `Option`。我們需要指定類型，
// 因為無法從上下文推斷。
let empty : Option<u64> = option::none();

// `option.is_some()` 如果 option 包含值，則回傳 true。
assert_eq!(opt.is_some(), true);
assert_eq!(empty.is_none(), true);

// 內部值可以被 `borrow` 和 `borrow_mut`。
assert_ref_eq!(opt.borrow(), &b"Alice");

// `option.extract` 從 option 中取出值，留下空的 option。
let inner = opt.extract();

// `option.is_none()` 如果 option 是 None，則回傳 true。
assert_eq!(opt.is_none(), true);
// ANCHOR_END: usage
}
