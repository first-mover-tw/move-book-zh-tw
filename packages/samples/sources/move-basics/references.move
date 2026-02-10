// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::references;
// ANCHOR: header_new
/// 卡片為空時的錯誤代碼。
const ENoUses: u64 = 0;
/// 卡片不為空時的錯誤代碼。
const EHasUses: u64 = 1;

/// 捷運通行卡的使用次數。
const USES: u8 = 3;

/// 捷運通行卡
public struct Card { uses: u8 }

/// 購買捷運通行卡。
public fun purchase(/* pass a Coin */): Card {
    Card { uses: USES }
}
// ANCHOR_END: header_new

// ANCHOR: immutable
/// 向檢查員出示捷運通行卡。
public fun is_valid(card: &Card): bool {
    card.uses > 0
}
// ANCHOR_END: immutable

// ANCHOR: mutable
/// 在驗票口使用捷運通行卡進入捷運。
public fun enter_metro(card: &mut Card) {
    assert!(card.uses > 0, ENoUses);
    card.uses = card.uses - 1;
}
// ANCHOR_END: mutable

// ANCHOR: move
/// 回收捷運通行卡。
public fun recycle(card: Card) {
    assert!(card.uses == 0, EHasUses);
    let Card { uses: _ } = card;
}
// ANCHOR_END: move

// ANCHOR: test
#[test]
fun test_card() {
    // 將變數宣告為可變因為我們要修改它
    let mut card = purchase();

    enter_metro(&mut card);

    assert!(is_valid(&card)); // 讀取卡片！

    enter_metro(&mut card); // 修改卡片但不移動它
    enter_metro(&mut card); // 修改卡片但不移動它

    recycle(card); // 將卡片移出作用域
}
// ANCHOR_END: test

// ANCHOR: move_2024
#[test]
fun test_card_2024() {
    // 將變數宣告為可變因為我們要修改它
    let mut card = purchase();

    card.enter_metro(); // 修改卡片但不移動它
    assert!(card.is_valid()); // 讀取卡片！

    card.enter_metro(); // 修改卡片但不移動它
    card.enter_metro(); // 修改卡片但不移動它

    card.recycle(); // 將卡片移出作用域
}
// ANCHOR_END: move_2024
// ANCHOR_END: main
