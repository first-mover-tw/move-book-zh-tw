// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: grouped
module book::grouped_imports;

// 從 `module_one` 模組匯入 `new` 函式和 `Character` 結構
use book::module_one::{new, Character};

/// 呼叫 `module_one` 模組中的 `new` 函式。
public fun create_character(): Character {
    new()
}
// ANCHOR_END: grouped
