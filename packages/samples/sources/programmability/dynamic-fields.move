// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_field)]
// ANCHOR: usage
module book::dynamic_fields;

// `dynamic_field` 的常見別名是 `df`，因為
// 模組名稱相當長
use sui::dynamic_field as df;
use std::string::String;

/// 我們將附加動態欄位的物件。
public struct Character has key {
    id: UID
}

// 可附加至角色的各種配飾清單。
// 它們必須具有 `store` 能力。
public struct Hat has key, store { id: UID, color: u32 }
public struct Mustache has key, store { id: UID }

#[test]
fun test_character_and_accessories() {
    let ctx = &mut tx_context::dummy();
    let mut character = Character { id: object::new(ctx) };

    // 將帽子附加至角色的 UID
    df::add(
        &mut character.id,
        b"hat_key",
        Hat { id: object::new(ctx), color: 0xFF0000 }
    );

    // 類似地，將鬍子附加至角色的 UID
    df::add(
        &mut character.id,
        b"mustache_key",
        Mustache { id: object::new(ctx) }
    );

    // 檢查帽子和鬍子是否附加至角色
    assert!(df::exists_(&character.id, b"hat_key"));
    assert!(df::exists_(&character.id, b"mustache_key"));

    // 修改帽子的顏色
    let hat: &mut Hat = df::borrow_mut(&mut character.id, b"hat_key");
    hat.color = 0x00FF00;

    // 從角色移除帽子和鬍子
    let hat: Hat = df::remove(&mut character.id, b"hat_key");
    let mustache: Mustache = df::remove(&mut character.id, b"mustache_key");

    // 檢查帽子和鬍子是否不再附加至角色
    assert!(!df::exists_(&character.id, b"hat_key"));
    assert!(!df::exists_(&character.id, b"mustache_key"));

    std::unit_test::destroy(character);
    std::unit_test::destroy(mustache);
    std::unit_test::destroy(hat);
}
// ANCHOR_END: usage


#[test] fun foreign_types() {
let ctx = &mut tx_context::dummy();
// ANCHOR: foreign_types
let mut character = Character { id: object::new(ctx) };

// 透過 `vector<u8>` 名稱附加 `String`
df::add(&mut character.id, b"string_key", b"Hello, World!".to_string());

// 透過 `u32` 名稱附加 `u64`
df::add(&mut character.id, 1000u32, 1_000_000_000u64);

// 透過 `bool` 名稱附加 `bool`
df::add(&mut character.id, true, false);
// ANCHOR_END: foreign_types
std::unit_test::destroy(character);
}

#[test] fun orphan_fields() {
let ctx = &mut tx_context::dummy();
// ANCHOR: orphan_fields
let hat = Hat { id: object::new(ctx), color: 0xFF0000 };
let mut character = Character { id: object::new(ctx) };

// 透過 `vector<u8>` 名稱附加 `Hat`
df::add(&mut character.id, b"hat_key", hat);

// ! 不要在你的程式碼中執行此操作
// ! 危險 - 刪除父物件
let Character { id } = character;
id.delete();

// ...`Hat` 現在卡在虛無中，將永遠無法再被存取
// ANCHOR_END: orphan_fields
}

// ANCHOR: exposed_uid
/// 公開角色的 UID，使其他模組可以讀取
/// 動態欄位。
public fun uid(c: &Character): &UID {
    &c.id
}
// ANCHOR_END: exposed_uid

// ANCHOR: exposed_uid_measures
/// 僅允許同一套件中的模組存取 UID。
public(package) fun uid_package(c: &Character): &UID {
    &c.id
}

/// 允許從角色借用動態欄位。
public fun borrow<Name: copy + store + drop, Value: store>(
    c: &Character,
    n: Name
): &Value {
    df::borrow(&c.id, n)
}
// ANCHOR_END: exposed_uid_measures

// ANCHOR: custom_type
/// 包含欄位的自訂類型。
public struct AccessoryKey has copy, drop, store { name: String }

/// 空鍵，只能附加一次。
public struct MetadataKey has copy, drop, store {}
// ANCHOR_END: custom_type

#[test] fun use_custom_types() {
let ctx = &mut tx_context::dummy();
// ANCHOR: custom_type_usage
let mut character = Character { id: object::new(ctx) };

// 透過 `AccessoryKey { name: b"hat" }` 附加
df::add(
    &mut character.id,
    AccessoryKey { name: b"hat".to_string() },
    Hat { id: object::new(ctx), color: 0xFF0000 }
);
// 透過 `AccessoryKey { name: b"mustache" }` 附加
df::add(
    &mut character.id,
    AccessoryKey { name: b"mustache".to_string() },
    Mustache { id: object::new(ctx) }
);

// 透過 `MetadataKey` 附加
df::add(&mut character.id, MetadataKey {}, 42);
// ANCHOR_END: custom_type_usage
std::unit_test::destroy(character);
}
