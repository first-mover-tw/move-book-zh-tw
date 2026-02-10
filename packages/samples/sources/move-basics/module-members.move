// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_function, unused_const, unused_use)]
// ANCHOR: members
module book::my_module_with_members;

// 匯入
use book::my_module;

// 一個常數
const CONST: u8 = 0;

// 一個結構
public struct Struct {}

// 方法別名
public use fun function as Struct.struct_fun;

// 函式
fun function(_: &Struct) { /* function body */ }
// ANCHOR_END: members
