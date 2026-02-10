// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::capability;

use std::string::String;
use sui::event;

/// 能力授予應用程式管理員在系統中建立新
/// 帳戶的權限。
public struct AdminCap has key, store { id: UID }

/// 系統中的使用者帳戶。
public struct Account has key, store {
    id: UID,
    name: String
}

/// 一個簡單的 `Ping` 事件，無任何資料。
public struct Ping has copy, drop { by: ID }

/// 在系統中建立新帳戶。需要將 `AdminCap` 能力
/// 作為第一個引數傳遞。
public fun new(_: &AdminCap, name: String, ctx: &mut TxContext): Account {
    Account {
        id: object::new(ctx),
        name,
    }
}

/// 帳戶和任何其他物件也可以在應用程式中用作能力。
/// 例如，用來發出事件。
public fun send_ping(acc: &Account) {
    event::emit(Ping {
        by: acc.id.to_inner()
    })
}

/// 更新帳戶名稱。只能由 `Account` 所有者呼叫。
public fun update(account: &mut Account, name: String) {
    account.name = name;
}
// ANCHOR_END: main
