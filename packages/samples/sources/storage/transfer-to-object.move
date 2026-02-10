// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::receiving;

use sui::derived_object;
use sui::transfer::Receiving; // 預設未匯入！

/// 用於建立衍生 `PostBox` 的基礎衍生物件。
public struct PostOffice has key { id: UID }

/// 具有衍生 UID 的物件，接收發送到某個位址的物件。
public struct PostBox has key { id: UID, owner: address }

/// 轉移功能。任何人都可以來 PostOffice 並發送到特定
/// 收件者的 PostBox。收件者可以從 `PostBox` 接收項目。
public fun send<T: key + store>(office: &PostOffice, parcel: T, recipient: address) {
    let postbox = derived_object::derive_address(office.id.to_inner(), recipient);
    transfer::public_transfer(parcel, postbox)
}

/// 接收包裹。需要發送者是 `PostBox` 的擁有者！
public fun receive<T: key + store>(
    box: &mut PostBox,
    to_receive: Receiving<T>,
    ctx: &TxContext
): T {
    assert!(box.owner == ctx.sender());

    // 從 `PostBox` 接收 `to_receive`。
    let parcel = transfer::public_receive(&mut box.id, to_receive);
    parcel
}

/// 如果使用者還沒有宣告他們的 `PostBox`，就建立它。
/// 注意：這不是轉移資產的要求！
/// 甚至可以將包裹發送到未註冊的郵箱，詳見 `send` 實現。
public fun register_address(office: &mut PostOffice, ctx: &mut TxContext) {
    transfer::share_object(PostBox {
        id: derived_object::claim(&mut office.id, ctx.sender()),
        owner: ctx.sender()
    })
}

// 在模組發佈時建立一個 PostOffice。
fun init(ctx: &mut TxContext) {
    transfer::share_object(PostOffice { id: object::new(ctx) });
}
// ANCHOR_END: main
