// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_use)]
// ANCHOR: usage
module book::dynamic_object_field;

use std::string::String;

// 長模組名稱有兩個常見別名：`dof` 和
// `ofield`。兩者都常用並在不同專案中遇到。
use sui::dynamic_object_field as dof;
use sui::dynamic_field as df;

/// 用於範例的 `Character`
public struct Character has key { id: UID }

/// 沒有 `key` 能力的中繼資料
public struct Metadata has store, drop { name: String }

/// 具有 `key` 和 `store` 能力的配飾。
public struct Accessory has key, store { id: UID }

#[test]
fun equip_accessory() {
    let ctx = &mut tx_context::dummy();
    let mut character = Character { id: object::new(ctx) };

    // 建立配飾並將其附加至角色
    let hat = Accessory { id: object::new(ctx) };

    // 將帽子加入角色。就像使用 `dynamic_fields` 一樣
    dof::add(&mut character.id, b"hat_key", hat);

    // 但是對於非鍵結構，我們只能使用 `dynamic_field`
    df::add(&mut character.id, b"metadata_key", Metadata {
        name: b"John".to_string()
    });

    // 從角色借用帽子
    let hat_id = dof::id(&character.id, b"hat_key").extract(); // Option<ID>
    let hat_ref: &Accessory = dof::borrow(&character.id, b"hat_key");
    let hat_mut: &mut Accessory = dof::borrow_mut(&mut character.id, b"hat_key");
    let hat: Accessory = dof::remove(&mut character.id, b"hat_key");

    // 清理，中繼資料現在成為孤兒。
    std::unit_test::destroy(hat);
    std::unit_test::destroy(character);
}
// ANCHOR_END: usage
