// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: self
module book::self_imports;

// 匯入 `Character` 結構和 `module_one` 模組
use book::module_one::{Self, Character};

/// 呼叫 `module_one` 模組中的 `new` 函式。
public fun create_character(): Character {
    module_one::new()
}
// ANCHOR_END: self
