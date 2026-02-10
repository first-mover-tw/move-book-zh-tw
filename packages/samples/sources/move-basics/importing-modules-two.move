// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: module_two
module book::module_two;

use book::module_one; // 從同一套件匯入 module_one

/// 呼叫 `module_one` 模組中的 `new` 函式。
public fun create_and_ignore() {
    let _ = module_one::new();
}
// ANCHOR_END: module_two
