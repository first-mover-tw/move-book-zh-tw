// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_mut_parameter)]
// ANCHOR: definition
module book::one_time;

/// `book::one_time` 模組的 OTW。
/// 僅 `drop`，沒有欄位，沒有泛型，全部大寫。
public struct ONE_TIME has drop {}

/// 以 OTW 實例作為第一個引數接收。
fun init(otw: ONE_TIME, ctx: &mut TxContext) {
    // 對 OTW 進行某些操作
}
// ANCHOR_END: definition

// ANCHOR: usage
use sui::types;

const ENotOneTimeWitness: u64 = 1;

/// 以 OTW 作為引數，如果類型不是 OTW 則中止。
public fun takes_witness<T: drop>(otw: T) {
    assert!(types::is_one_time_witness(&otw), ENotOneTimeWitness);
}
// ANCHOR_END: usage
