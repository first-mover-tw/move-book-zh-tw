// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::hot_potato_pattern {

// ANCHOR: definition
public struct Request {}
// ANCHOR_END: definition

// ANCHOR: new_request
/// 構造新的 `Request`
public fun new_request(): Request { Request {} }

/// 解包 `Request`。由於熱馬鈴薯的性質，必須呼叫此函式
/// 以避免交易中止。
public fun confirm_request(request: Request) {
    let Request {} = request;
}
// ANCHOR_END: new_request

}

module book::container_borrow {

// ANCHOR: container_borrow
/// 嘗試將值回傳至不正確的容器。
const ENotCorrectContainer: u64 = 0;
/// 嘗試回傳不正確的值。
const ENotCorrectValue: u64 = 1;

/// 任何具有 `key + store` 的物件的通用容器。Option 類型
/// 用於允許取出和放回值。
public struct Container<T: key + store> has key {
    id: UID,
    value: Option<T>,
}

/// 用於確保回傳借用值的熱馬鈴薯結構。
public struct Promise {
    /// 借用物件的 ID。確保沒有發生值交換。
    id: ID,
    /// 容器的 ID。確保借用的值被回傳至
    /// 正確的容器。
    container_id: ID,
}

/// 允許從容器借用值的函式。
public fun borrow_val<T: key + store>(container: &mut Container<T>): (T, Promise) {
    let value = container.value.extract();
    let id = object::id(&value);
    (value, Promise { id, container_id: object::id(container) })
}

/// 將取出的項目放回容器。
public fun return_val<T: key + store>(
    container: &mut Container<T>, value: T, promise: Promise
) {
    let Promise { id, container_id } = promise;
    assert!(object::id(container) == container_id, ENotCorrectContainer);
    assert!(object::id(&value) == id, ENotCorrectValue);
    container.value.fill(value);
}
// ANCHOR_END: container_borrow
}

module book::phone_shop {

use sui::coin::Coin;

public struct USD has drop {}
public struct BONUS has drop {}

// ANCHOR: phone_shop
/// 嘗試用不正確的 `BonusPoints` 或 `USD` 價格購買 `Phone`。
const ENotCorrectPrice: u64 = 0;

/// 可在商店購買的 `Phone`。
public struct Phone has key, store { id: UID }

/// 購買 `Phone` 必須支付的票據。
public struct Ticket { amount: u64 }

/// 回傳 `Phone` 和購買它必須支付的 `Ticket`。
public fun purchase_phone(ctx: &mut TxContext): (Phone, Ticket) {
    (
        Phone { id: object::new(ctx) },
        Ticket { amount: 100 }
    )
}

/// 客戶可以用 `BonusPoints` 支付 `Phone` 費用。
public fun pay_in_bonus_points(ticket: Ticket, payment: Coin<BONUS>) {
    let Ticket { amount } = ticket;
    assert!(payment.value() == amount, ENotCorrectPrice);
    abort // 省略函式的其餘部分
}

/// 客戶可以用 `USD` 支付 `Phone` 費用。
public fun pay_in_usd(ticket: Ticket, payment: Coin<USD>) {
    let Ticket { amount } = ticket;
    assert!(payment.value() == amount, ENotCorrectPrice);
    abort // 省略函式的其餘部分
}
// ANCHOR_END: phone_shop
}
