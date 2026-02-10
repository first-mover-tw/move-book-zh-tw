// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_use)]
// ANCHOR: conflict
module book::conflict_resolution;

// `as` 可以放在任何 import 後面，包括分組 import
use book::module_one::{Self as mod, Character as Char};

/// 呼叫 `module_one` 模組中的 `new` 函式。
public fun create(): Char {
    mod::new()
}
// ANCHOR_END: conflict
