// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_field)]
module book::struct_syntax;

use std::string::String;

// ANCHOR: def
/// 代表藝術家的結構體。
public struct Artist {
    /// 藝術家的名字。
    name: String,
}

/// 代表音樂唱片的結構體。
public struct Record {
    /// 唱片的標題。
    title: String,
    /// 唱片的藝術家。使用 `Artist` 型別。
    artist: Artist,
    /// 唱片發行的年份。
    year: u16,
    /// 唱片是否為首張專輯。
    is_debut: bool,
    /// 唱片的版本。
    edition: Option<u16>,
}
// ANCHOR_END: def

#[test_only]
use std::unit_test::assert_eq;

#[test] fun test_pack_unpack() {

// ANCHOR: pack
let mut artist = Artist {
    name: b"The Beatles".to_string()
};
// ANCHOR_END: pack

// ANCHOR: access
// 存取 `Artist` 結構體的 `name` 欄位。
let artist_name = artist.name;

// 存取 `Artist` 結構體的欄位。
assert_eq!(artist.name, b"The Beatles".to_string());

// 修改 `Artist` 結構體的 `name` 欄位。
artist.name = b"Led Zeppelin".to_string();

// 檢查 `name` 欄位已被修改。
assert_eq!(artist.name, b"Led Zeppelin".to_string());
// ANCHOR_END: access

// ANCHOR: unpack
// 解開 `Artist` 結構體並建立新的 `name` 變數
// 其值為 `name` 欄位的值。
let Artist { name } = artist;
// ANCHOR_END: unpack

let artist = Artist {
    name: b"The Beatles".to_string()
};

// ANCHOR: unpack_ignore
// 解開 `Artist` 結構體並忽略 `name` 欄位。
let Artist { name: _ } = artist;
// ANCHOR_END: unpack_ignore
}
