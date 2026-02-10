// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::shop;

/// 授予商店所有者管理權限的能力
/// 商店。
public struct ShopOwnerCap has key, store { id: UID }

/// 在 `init` 函式中建立的單數商店。
public struct Shop has key {
    id: UID,
    /* ... */
}

// 僅在模組發佈時呼叫一次。它必須
// 是私有的以防止外部呼叫。
fun init(ctx: &mut TxContext) {
    // 將 ShopOwnerCap 轉移至傳送者（發佈者）。
    transfer::transfer(ShopOwnerCap {
        id: object::new(ctx)
    }, ctx.sender());

    // 共用商店物件。
    transfer::share_object(Shop {
        id: object::new(ctx)
    });
}
// ANCHOR_END: main
