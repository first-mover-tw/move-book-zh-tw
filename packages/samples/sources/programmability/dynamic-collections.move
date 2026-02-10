// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use, unused_field, unused_variable)]
module book::dynamic_collections {
use std::string::String;

// ANCHOR: bag_struct
/// 從 `sui::bag` 模組匯入。
use sui::bag::{Self, Bag};

/// 以結構欄位形式使用 `Bag` 的範例。
public struct Carrier has key {
    id: UID,
    bag: Bag
}
// ANCHOR_END: bag_struct

#[test_only]
use std::unit_test::assert_eq;

#[test] fun test_bag() {
let ctx = &mut tx_context::dummy();

// ANCHOR: bag_usage
let mut bag = bag::new(ctx);

// bag 有 `length` 函式來取得元素個數
assert_eq!(bag.length(), 0);

bag.add(b"my_key", b"my_value".to_string());

// 長度已變更為 1
assert_eq!(bag.length(), 1);

// 依序：`borrow`、`borrow_mut` 及 `remove`
// 必須指定值的類型
let field_ref: &String = &bag[b"my_key"];
let field_mut: &mut String = &mut bag[b"my_key"];
let field: String = bag.remove(b"my_key");

// 長度回到 0 - 我們可以解包
bag.destroy_empty();
// ANCHOR_END: bag_usage
}

// ANCHOR: table_struct
/// 從 `sui::table` 模組匯入。
use sui::table::{Self, Table};

/// 具有 `store` 的某個記錄類型
public struct Record has store { /* ... */ }

/// 以結構欄位形式使用 `Table` 的範例。
public struct UserRegistry has key {
    id: UID,
    table: Table<address, Record>
}
// ANCHOR_END: table_struct

#[test] fun test_table() {
let ctx = &mut tx_context::dummy();

// ANCHOR: table_usage
// Table 需要在初始化時明確指定鍵和值的類型參數。
// ...但只需在初始化時指定一次。
let mut table = table::new<address, String>(ctx);

// table 有 `length` 函式來取得元素個數
assert_eq!(table.length(), 0);

table.add(@0xa11ce, b"my_value".to_string());
table.add(@0xb0b, b"another_value".to_string());

// 長度已變更為 2
assert_eq!(table.length(), 2);

// 依序：`borrow`、`borrow_mut` 及 `remove`
let value_ref = &table[@0xa11ce];
let value_mut = &mut table[@0xa11ce];

// 移除兩個值
let _value = table.remove(@0xa11ce);
let _another_value = table.remove(@0xb0b);

// 長度回到 0 - 我們可以解包
table.destroy_empty();
// ANCHOR_END: table_usage
}

// ANCHOR: linked_table_struct
/// 從 `sui::linked_table` 模組匯入。
use sui::linked_table::{Self, LinkedTable};

/// 具有 `store` 的某個權限類型
public struct Permissions has store { /* ... */ }

/// 以結構欄位形式使用 `LinkedTable` 的範例。
public struct AdminRegistry has key {
    id: UID,
    linked_table: LinkedTable<address, Permissions>
}
// ANCHOR_END: linked_table_struct

#[test] fun test_linked_table() {
let ctx = &mut tx_context::dummy();

// ANCHOR: linked_table_usage
// LinkedTable 需要在初始化時明確指定鍵和值的類型參數。
// ...但只需在初始化時指定一次。
let mut linked_table = linked_table::new<address, String>(ctx);

// linked_table 有 `length` 函式來取得元素個數
assert_eq!(linked_table.length(), 0);

linked_table.push_front(@0xa0a, b"first_value".to_string());
linked_table.push_back(@0xb1b, b"second_value".to_string());
linked_table.push_back(@0xc2c, b"third_value".to_string());

// 長度已變更為 3
assert_eq!(linked_table.length(), 3);

// 依序：`borrow`、`borrow_mut` 及 `remove`
let first_value_ref = &linked_table[@0xa0a];
let second_value_mut = &mut linked_table[@0xb1b];

// 按鍵移除，從開始或從末尾
let _second_value = linked_table.remove(@0xb1b);
let (_first_addr, _first_value) = linked_table.pop_front();
let (_third_addr, _third_value) = linked_table.pop_back();

// 長度回到 0 - 我們可以解包
linked_table.destroy_empty();
// ANCHOR_END: linked_table_usage
}
}
