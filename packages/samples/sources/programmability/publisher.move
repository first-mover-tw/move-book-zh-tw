// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
// ANCHOR: publisher
module book::publisher;

use sui::package::{Self, Publisher};

/// 在模組中定義的某種類型。
public struct Book {}

/// 模組的 OTW (One Time Witness)。
public struct PUBLISHER has drop {}

/// 使用 One Time Witness 來宣告 Publisher 物件。
fun init(otw: PUBLISHER, ctx: &mut TxContext) {
    // 宣告 Publisher 物件。
    let publisher: Publisher = sui::package::claim(otw, ctx);

    // 通常會轉移給發送者。
    // 它也可以存儲在另一個物件中。
    transfer::public_transfer(publisher, ctx.sender())
}
// ANCHOR_END: publisher

public struct USE_PUBLISHER has drop {}

const ENotAuthorized: u64 = 1;


#[test]
fun test_publisher() {
let ctx = &mut tx_context::dummy();
let publisher = package::test_claim(USE_PUBLISHER {}, ctx);
// ANCHOR: use_publisher
// 檢查該類型是否來自同一模組，因此 `Publisher` 對它有權限。
assert!(publisher.from_module<Book>());

// 檢查該類型是否來自同一套件，因此 `Publisher` 對它有權限。
assert!(publisher.from_package<Book>());
// ANCHOR_END: use_publisher
std::unit_test::destroy(publisher);
}

// ANCHOR: publisher_as_admin
/// 應用程式中由 Publisher 物件控制的某個操作。
public fun admin_action(cap: &Publisher, /* app objects... */ param: u64) {
    assert!(cap.from_module<Book>(), ENotAuthorized);

    // 執行應用程式特定的操作
}
// ANCHOR_END: publisher_as_admin
