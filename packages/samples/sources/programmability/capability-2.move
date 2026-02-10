// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: admin_cap
module book::admin_cap;

/// 授予系統中管理員權限的能力。
/// 僅在 `init` 函式中建立一次。
public struct AdminCap has key { id: UID }

/// 在套件發佈時建立 AdminCap 物件，並將其轉移至
/// 套件所有者。
fun init(ctx: &mut TxContext) {
    transfer::transfer(
        AdminCap { id: object::new(ctx) },
        ctx.sender()
    )
}
// ANCHOR_END: admin_cap
