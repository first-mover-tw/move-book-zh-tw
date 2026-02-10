// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::addr_vs_cap;

public struct User has key, store { id: UID }

// ANCHOR: with_address
/// 未授權存取的錯誤代碼。
const ENotAuthorized: u64 = 0;

/// 應用程式管理員位址。
const APPLICATION_ADMIN: address = @0xa11ce;

/// 在系統中建立新使用者。需要寄件者為應用程式
/// 管理員。
public fun new(ctx: &mut TxContext): User {
    assert!(ctx.sender() == APPLICATION_ADMIN, ENotAuthorized);
    User { id: object::new(ctx) }
}
// ANCHOR_END: with_address

