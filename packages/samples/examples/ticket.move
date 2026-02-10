// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::ticket;

/// 一個活動或服務的票券。預設不可轉移，
/// 使用方式會根據應用程式而有所不同。
public struct Ticket<T: store + drop> has key {
    id: UID,
    used: bool,
    metadata: T
}

/// 使用中繼資料和上下文建立一個新的票券。
/// 不需要在此使用見證人！
public fun new<T: store + drop>(metadata: T, ctx: &mut TxContext): Ticket<T> {
    Ticket {
        id: object::new(ctx),
        used: false,
        metadata
    }
}

/// 消耗票券。需要中繼資料類型的見證人。
/// 可能由應用程式實現或可能不實現。
public fun consume<T: store + drop>(_meta: T, ticket: &mut Ticket<T>) {
    ticket.used = true;
}

/// 將票券轉移給另一個使用者。需要中繼資料類型的見證人。
/// 可能由應用程式實現或可能不實現。
public fun transfer<T: store + drop>(_meta: T, ticket: Ticket<T>, to: address) {
    transfer::transfer(ticket, to)
}

/// 取得票券的中繼資料。
public fun metadata<T: store + drop>(ticket: &Ticket<T>): &T {
    &ticket.metadata
}

/// 檢查票券是否已被使用。
public fun is_used<T: store + drop>(ticket: &Ticket<T>): bool {
    ticket.used
}
