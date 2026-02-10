// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: address_literal
module 0x0::address_literal { /* ... */ }
module book::named_address { /* ... */ }
// ANCHOR_END: address_literal

#[allow(unused_function, unused_const, unused_use)]
// ANCHOR: members
module book::my_block_module_with_members {
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
}

// 模組區塊允許在同一檔案中定義多個模組，
// 但這不是推薦的做法
module book::another_module_in_the_file {
    // ...
}
// ANCHOR_END: members
