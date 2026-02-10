// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_field, unused_variable, unused_use)]
// ANCHOR: vec_map
module book::collections_vec_map;

use std::string::String;
use sui::vec_map::{Self, VecMap};

public struct Metadata has drop {
    name: String,
    /// 在結構定義中使用的 `VecMap`
    attributes: VecMap<String, String>
}

#[test]
fun vec_map_playground() {
    let mut map = vec_map::empty(); // 建立一個空映射

    map.insert(2, b"two".to_string()); // 將鍵值對新增至映射
    map.insert(3, b"three".to_string());

    assert!(map.contains(&2)); // 檢查鍵是否在映射中

    map.remove(&2); // 從映射中移除鍵值對
}
// ANCHOR_END: vec_map
