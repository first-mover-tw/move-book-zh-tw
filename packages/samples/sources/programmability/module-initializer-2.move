// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: other
// 在與 `shop` 模組相同的套件中
module book::bank;

public struct Bank has key {
    id: UID,
    /* ... */
}

fun init(ctx: &mut TxContext) {
    transfer::share_object(Bank {
        id: object::new(ctx)
    });
}
// ANCHOR_END: other
