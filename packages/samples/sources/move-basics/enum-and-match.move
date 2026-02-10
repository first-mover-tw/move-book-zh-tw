// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: definition
module book::segment;

use std::string::String;

/// `Segment` 列舉定義。
/// 定義各種字串區段。
public enum Segment has copy, drop {
    /// 空變體，無值。
    Empty,
    /// 具有值的變體 (位置式風格)。
    String(String),
    /// 具有具名欄位的變體。
    Special {
        content: vector<u8>,
        encoding: u8, // 編碼標籤。
    },
}
// ANCHOR_END: definition

// ANCHOR: constructors
/// 構造一個 `Empty` 區段。
public fun new_empty(): Segment { Segment::Empty }

/// 使用 `str` 值構造一個 `String` 區段。
public fun new_string(str: String): Segment { Segment::String(str) }

/// 使用 `content` 和 `encoding` 值構造一個 `Special` 區段。
public fun new_special(content: vector<u8>, encoding: u8): Segment {
    Segment::Special {
        content,
        encoding,
    }
}
// ANCHOR_END: constructors

// ANCHOR: struct
/// 一個用於展示列舉能力的結構。
public struct Segments(vector<Segment>) has copy, drop;

#[test]
fun test_segments() {
    let _ = Segments(vector[
        Segment::Empty,
        Segment::String(b"hello".to_string()),
        Segment::String(b" move".to_string()),
        Segment::Special { content: b"21", encoding: 1 },
    ]);
}
// ANCHOR_END: struct

// ANCHOR: is_empty
/// 此是否為 `Empty` 區段。
public fun is_empty(s: &Segment): bool {
    // match 是一個運算式，因此我們可以將其用於回傳值。
    match (s) {
        Segment::Empty => true,
        Segment::String(_str) => false,
        Segment::Special { content: _, encoding: _ } => false,
    }
}
// ANCHOR_END: is_empty

public fun is_empty_(s: &Segment): bool {
    // ANCHOR: is_empty_2
    match (s) {
        Segment::Empty => true,
        _ => false, // 其他任何內容都回傳 `false`。
    }
}
// ANCHOR_END: is_empty_2

// ANCHOR: accessors
/// 此是否為 `Special` 區段。
public fun is_special(s: &Segment): bool {
    match (s) {
        // 提示：`..` 忽略內部欄位
        Segment::Special { .. } => true,
        _ => false,
    }
}

/// 此是否為 `String` 區段。
public fun is_string(s: &Segment): bool {
    match (s) {
        Segment::String(_) => true,
        _ => false,
    }
}
// ANCHOR_END: accessors

// ANCHOR: try_into_inner_string
/// 如果 `Segment` 是 `String` 則回傳 `Some(String)`，否則回傳 `None`。
public fun try_into_inner_string(s: Segment): Option<String> {
    match (s) {
        Segment::String(str) => option::some(str),
        _ => option::none(),
    }
}
// ANCHOR_END: try_into_inner_string

// ANCHOR: to_string
/// 回傳區段的 `String` 表示。
public fun to_string(s: &Segment): String {
    match (*s) {
        // 回傳空字串。
        Segment::Empty => b"".to_string(),
        // 回傳內部字串。
        Segment::String(str) => str,
        // 根據編碼回傳解碼的內容。
        Segment::Special { content, encoding } => {
            // 對編碼進行 match，我們僅支援 0 - utf8、1 - 十六進位。
            match (encoding) {
                // 純文字編碼，回傳內容。
                0 => content.to_string(),
                // 十六進位編碼，解碼並回傳。
                1 => sui::hex::decode(content).to_string(),
                // 我們必須提供萬用字元模式，因為 `u8` 的值範圍是 0-255。
                _ => abort,
            }
        },
    }
}
// ANCHOR_END: to_string
