// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0


#[allow(unused_field)]
// ANCHOR: hero
module book::arena;

use std::string::String;
use sui::package;
use sui::display;

/// 用於領取 `Publisher` 物件的單次見證。
public struct ARENA has drop {}

/// 將被顯示的某個物件。
public struct Hero has key {
    id: UID,
    class: String,
    level: u64,
}

/// 在模組初始化器中，我們建立 `Publisher` 物件，然後
/// 建立 `Hero` 類型的 Display。
fun init(otw: ARENA, ctx: &mut TxContext) {
    let publisher = package::claim(otw, ctx);
    let mut display = display::new<Hero>(&publisher, ctx);

    display.add(
        b"name".to_string(),
        b"{class} (lvl. {level})".to_string()
    );

    display.add(
        b"description".to_string(),
        b"One of the greatest heroes of all time. Join us!".to_string()
    );

    display.add(
        b"link".to_string(),
        b"https://example.com/hero/{id}".to_string()
    );

    display.add(
        b"image_url".to_string(),
        b"https://example.com/hero/{class}.jpg".to_string()
    );

    // 用新資料更新顯示。
    // 必須呼叫以應用變更。
    display.update_version();

    transfer::public_transfer(publisher, ctx.sender());
    transfer::public_transfer(display, ctx.sender());
}
// ANCHOR_END: hero

// ANCHOR: background
/// 嘗試標準化顯示的物件結構。
public struct CounterWithDisplay has key {
    id: UID,
    /// 如果存在此欄位，將在 UI 中顯示為 `name`。
    name: String,
    /// 如果存在此欄位，將在 UI 中顯示為 `description`。
    description: String,
    // ...
    image: String,
    /// 物件的實際欄位。
    counter: u64,
    // ...
}
// ANCHOR_END: background

// ANCHOR: nested
/// 物件的某些常見中繼資料。
public struct Metadata has store {
    name: String,
    description: String,
    published_at: u64
}

/// 具有巢狀 Metadata 欄位的類型。
public struct LittlePony has key, store {
    id: UID,
    image_url: String,
    metadata: Metadata
}
// ANCHOR_END: nested
