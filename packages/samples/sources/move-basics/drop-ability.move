// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::drop_ability;

/// 此結構具有 `drop` 能力。
public struct IgnoreMe has drop {
    a: u8,
    b: u8,
}

/// 此結構沒有 `drop` 能力。
public struct NoDrop {}

#[test]
// 建立 `IgnoreMe` 結構的實例並忽略它。
// 即使我們構造了該實例，我們也不需要解構它。
fun test_ignore() {
    let no_drop = NoDrop {};
    let _ = IgnoreMe { a: 1, b: 2 }; // 不需要解構

    // 該值必須被解構才能使程式碼編譯。
    let NoDrop {} = no_drop; // 確認
}
// ANCHOR_END: main
