// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
module book::copy_ability;

// ANCHOR: copyable
public struct Copyable has copy {}
// ANCHOR_END: copyable

#[test] fun test_copy() {

// ANCHOR: copyable_test
let a = Copyable {}; // 允許，因為 Copyable 結構具有 `copy` 能力
let b = a;   // `a` 被複製到 `b`
let c = *&b; // 透過解引用運算子進行顯式複製

// Copyable 沒有 `drop` 能力，所以每個實例 (a、b 和 c) 必須
// 被使用或顯式解構。`drop` 能力在下面說明。
let Copyable {} = a;
let Copyable {} = b;
let Copyable {} = c;
// ANCHOR_END: copyable_test
}

// ANCHOR: copy_drop
public struct Value has copy, drop {}
// ANCHOR_END: copy_drop
