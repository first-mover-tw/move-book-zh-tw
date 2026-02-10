// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: user_builder
#[test_only]
module book::user_builder;

use book::user::{Self, User};
use std::string::String;

/// 用於在測試中建立 `User` 實例的建造器。
public struct UserBuilder has drop {
    name: Option<String>,
    age: Option<u8>,
    email: Option<String>,
    balance: Option<u64>,
    is_active: Option<bool>,
}

/// 建立一個空的建造器，所有欄位都未設定。
public fun new(): UserBuilder {
    UserBuilder {
        name: option::none(),
        age: option::none(),
        email: option::none(),
        balance: option::none(),
        is_active: option::none(),
    }
}

// === Setter 方法 - 每個都回傳建造器以便鏈接 ===

public fun name(mut self: UserBuilder, name: String): UserBuilder {
    self.name = option::some(name);
    self
}

public fun age(mut self: UserBuilder, age: u8): UserBuilder {
    self.age = option::some(age);
    self
}

public fun email(mut self: UserBuilder, email: String): UserBuilder {
    self.email = option::some(email);
    self
}

public fun balance(mut self: UserBuilder, balance: u64): UserBuilder {
    self.balance = option::some(balance);
    self
}

public fun is_active(mut self: UserBuilder, is_active: bool): UserBuilder {
    self.is_active = option::some(is_active);
    self
}

/// 建立 `User`，對於任何未設定的欄位使用預設值。
public fun build(self: UserBuilder): User {
    let UserBuilder { name, age, email, balance, is_active } = self;
    user::new(
        name.destroy_or!(b"Default User".to_string()),
        age.destroy_or!(18),
        email.destroy_or!(b"user@example.com".to_string()),
        balance.destroy_or!(0),
        is_active.destroy_or!(true),
    )
}
// ANCHOR_END: user_builder

// ANCHOR: test_without_builder
#[test]
fun test_balance_check_without_builder() {
    // 我們只關心 `balance`，但必須指定所有內容
    let user = user::new(
        b"Alice".to_string(),
        25,
        b"alice@example.com".to_string(),
        1000, // <-- 唯一我們關心的欄位
        true,
    );
    assert!(user.balance() == 1000);
}

#[test]
fun test_inactive_user_without_builder() {
    // 我們只關心 `is_active`，但必須指定所有內容
    let user = user::new(
        b"Bob".to_string(),
        30,
        b"bob@example.com".to_string(),
        500,
        false, // <-- 唯一我們關心的欄位
    );
    assert!(user.is_active() == false);
}
// ANCHOR_END: test_without_builder

// ANCHOR: test_with_builder
#[test]
fun test_balance_check() {
    // 只指定對這個測試重要的內容
    let user = new()
        .balance(1000)
        .build();

    assert!(user.balance() == 1000);
}

#[test]
fun test_inactive_user() {
    // 只指定對這個測試重要的內容
    let user = new()
        .is_active(false)
        .build();

    assert!(user.is_active() == false);
}

#[test]
fun test_underage_user() {
    // 測試年齡相關的邏輯
    let user = new()
        .age(16)
        .build();

    assert!(user.age() < 18);
}
// ANCHOR_END: test_with_builder
