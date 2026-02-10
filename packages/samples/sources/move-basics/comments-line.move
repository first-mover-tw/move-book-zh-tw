// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_function, unused_variable)]
// ANCHOR: main
module book::comments_line;

// 讓我們為所有東西加上說明！
fun some_function_with_numbers() {
    let a = 10;
    // let b = 10 這一行已註釋，不會執行
    let b = 5; // 這裡註釋是放在程式碼之後
    a + b; // 結果是 15，不是 10！
}
// ANCHOR_END: main
