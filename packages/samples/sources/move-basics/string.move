// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
// ANCHOR: custom
module book::custom_string;

/// 任何人都可以藉由包裝向量來實作自訂字串型別。
public struct MyString {
    bytes: vector<u8>,
}

/// 實作 `from_bytes` 函式以將位元組向量轉換為字串。
public fun from_bytes(bytes: vector<u8>): MyString {
    MyString { bytes }
}

/// 實作 `bytes` 函式以將字串轉換為位元組向量。
public fun bytes(self: &MyString): &vector<u8> {
    &self.bytes
}
// ANCHOR_END: custom

// use std::ascii::String;

#[allow(unused_variable)]
#[test]
fun using_strings() {
// ANCHOR: ascii
// 模組是 `std::ascii` 而型別是 `String`
use std::ascii::{Self, String};

// 字串可以使用 `string` 函式建立
// 型別宣告非必要，我們在這裡加上是為了清楚起見
let hey: String = ascii::string(b"Hey");

// 在 `vector<u8>` 型別上有個便利的別名 `.to_ascii_string()`
let hey = b"Hey".to_ascii_string();

// ANCHOR_END: ascii
}

#[test] fun using_strings_utf8() {
// ANCHOR: utf8
// 模組是 `std::string` 而型別是 `String`
use std::string::{Self, String};

// 字串通常使用 `utf8` 函式建立
// 型別宣告非必要，我們在這裡加上是為了清楚起見
let hello: String = string::utf8(b"Hello");

// `vector<u8>` 上的 `.to_string()` 別名更方便
let hello = b"Hello".to_string();
// ANCHOR_END: utf8
}

#[test] fun safe_strings() {
// ANCHOR: safe_utf8
// 這是個有效的 UTF-8 字串
let hello = b"Hello".try_to_string();

assert!(hello.is_some()); // 如果值不是有效的 UTF-8 則中止

// 這不是個有效的 UTF-8 字串
let invalid = b"\xFF".try_to_string();

assert!(invalid.is_none()); // 如果值是有效的 UTF-8 則中止
// ANCHOR_END: safe_utf8
}
