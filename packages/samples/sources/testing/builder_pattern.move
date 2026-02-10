// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: user
module book::user;

use std::string::String;

/// 具有多個屬性的使用者帳戶。
public struct User has drop {
    name: String,
    age: u8,
    email: String,
    balance: u64,
    is_active: bool,
}

/// 建立新使用者 - 需要所有欄位。
public fun new(
    name: String,
    age: u8,
    email: String,
    balance: u64,
    is_active: bool,
): User {
    User { name, age, email, balance, is_active }
}

public fun balance(self: &User): u64 { self.balance }
public fun is_active(self: &User): bool { self.is_active }
public fun age(self: &User): u8 { self.age }
// ANCHOR_END: user
