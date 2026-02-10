// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_field, unused_use)]
// ANCHOR: vec_set
module book::collections_vec_set;

use sui::vec_set::{Self, VecSet};

public struct App has drop {
    /// 在結構定義中使用的 `VecSet`
    subscribers: VecSet<address>
}

#[test_only]
use std::unit_test::assert_eq;

#[test]
fun vec_set_playground() {
    let set = vec_set::empty<u8>(); // 建立一個空集合
    let mut set = vec_set::singleton(1); // 建立一個包含單一項目的集合

    set.insert(2); // 將項目新增至集合
    set.insert(3);

    assert!(set.contains(&1)); // 檢查項目是否在集合中
    assert!(set.length() == 3); // 取得集合中的項目數
    assert!(!set.is_empty()); // 檢查集合是否為空

    set.remove(&2); // 從集合中移除項目
}
// ANCHOR_END: vec_set
