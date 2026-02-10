// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: members
module book::more_imports;

use book::module_one::new;       // 從 `module_one` 模組匯入 `new` 函式
use book::module_one::Character; // 從 `module_one` 模組匯入 `Character` 結構

/// 呼叫 `module_one` 模組中的 `new` 函式。
public fun create_character(): Character {
    new()
}
// ANCHOR_END: members
