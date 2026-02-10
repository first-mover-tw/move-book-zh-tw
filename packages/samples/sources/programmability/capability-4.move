// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::cap_vs_addr;

public struct User has key, store { id: UID }

// ANCHOR: with_capability
/// 授予所有者在系統中建立新使用者的權限。
public struct AdminCap {}

/// 在系統中建立新使用者。需要將 `AdminCap` 能力
/// 作為第一個引數傳遞。
public fun new(_: &AdminCap, ctx: &mut TxContext): User {
    User { id: object::new(ctx) }
}
// ANCHOR_END: with_capability
