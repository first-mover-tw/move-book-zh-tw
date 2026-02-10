// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
module book::epoch_and_time {

// ANCHOR: epoch
public fun current_epoch(ctx: &TxContext) {
    let epoch = ctx.epoch();
    // ...
}
// ANCHOR_END: epoch

// ANCHOR: epoch_start
public fun current_epoch_start(ctx: &TxContext) {
    let epoch_start = ctx.epoch_timestamp_ms();
    // ...
}
// ANCHOR_END: epoch_start

// ANCHOR: clock
use sui::clock::Clock;

/// Clock 需要作為不可變參考傳遞。
public fun current_time(clock: &Clock) {
    let time = clock.timestamp_ms();
    // ...
}
// ANCHOR_END: clock

// ANCHOR: test
#[test_only]
use sui::clock;
#[test_only]
use std::unit_test::assert_eq;

#[test]
fun use_clock_in_test() {
    // 取得 `ctx` 並建立 `Clock` 以進行測試
    let ctx = &mut tx_context::dummy();
    let mut clock = clock::create_for_testing(ctx);
    assert_eq!(clock.timestamp_ms(), 0);

    // 將值加入儲存在 `Clock` 中的時間戳記
    clock.increment_for_testing(2_000_000_000);
    assert_eq!(clock.timestamp_ms(), 2_000_000_000);

    // 設定時間戳記，但設定的時間不能小於儲存在 `Clock` 中的值
    clock.set_for_testing(3_000_000_000);
    assert_eq!(clock.timestamp_ms(), 3_000_000_000);

    // 下列設定將失敗，因為設定的時間必須至少為儲存在 `Clock` 中的時間戳記
    // clock.set_for_testing(1_000_000_000);
    // assert_eq!(clock.timestamp_ms(), 1_000_000_000);

    // 如果需要共用的 `Clock` 以進行測試，可以透過此函式設定
    // clock.share_for_testing();

    // `Clock` 沒有 `drop` 能力，所以需要在測試結束時手動銷毀
    clock.destroy_for_testing();
}
// ANCHOR_END: test

}
