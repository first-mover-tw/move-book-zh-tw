// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: module_one
module book::module_one;

/// 在同一模組中定義的結構。
public struct Character has drop {}

/// 建立新 `Character` 實例的簡單函式。
public fun new(): Character { Character {} }
// ANCHOR_END: module_one
