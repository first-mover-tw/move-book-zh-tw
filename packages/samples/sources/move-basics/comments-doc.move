// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_function, unused_const, unused_variable, unused_field)]
// ANCHOR: main
/// 模組有文件說明！
module book::comments_doc;

/// 這是一個 0x0 位址常數！
const AN_ADDRESS: address = @0x0;

/// 這是一個結構體！
public struct AStruct {
    /// 這是結構體的一個欄位！
    a_field: u8,
}

/// 此函式執行某些操作！
/// 並且它有文件說明！
fun do_something() {}
// ANCHOR_END: main
