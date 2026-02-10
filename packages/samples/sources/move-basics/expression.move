// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable)]
module book::expression;

#[test]
fun expression_examples() {

// ANCHOR: empty
// 變數 `a` 沒有值；
let a;
// ANCHOR_END: empty

// ANCHOR: literals
let b = true;     // true 是一個字面值
let n = 1000;     // 1000 是一個字面值
let h = 0x0A;     // 0x0A 是一個字面值
let v = b"hello"; // b"hello" 是一個位元組向量字面值
let x = x"0A";    // x"0A" 是一個位元組向量字面值
let c = vector[1, 2, 3]; // vector[] 是一個向量字面值
// ANCHOR_END: literals

// ANCHOR: operators
let sum = 1 + 2;   // 1 + 2 是一個運算式
let sum = (1 + 2); // 相同的運算式，加上括號
let is_true = true && false; // true && false 是一個運算式
let is_true = (true && false); // 相同的運算式，加上括號
// ANCHOR_END: operators

// ANCHOR: block
// 具有空運算式的區塊，但編譯器會
// 自動插入空運算式：`let none = { () }`
// let none = {};

// 具有 let 陳述式和運算式的區塊。
let sum = {
    let a = 1;
    let b = 2;
    a + b // 最後的運算式是區塊的值
};

// 區塊是一個運算式，因此可以在運算式中使用，並且
// 不一定要指派給變數。
{
    let a = 1;
    let b = 2;
    a + b; // 未回傳 - 分號。
    // 編譯器自動插入空運算式 `()`
};
// ANCHOR_END: block
}

// ANCHOR: fun_call
fun add(a: u8, b: u8): u8 {
    a + b
}

#[test]
fun some_other() {
    let sum = add(1, 2); // 由於分號，不會回傳。
    // 編譯器自動插入空運算式 `()` 作為區塊的回傳值
}
// ANCHOR_END: fun_call


#[test] fun control_flow() {

let expr = false;
let expr1 = false;
let expr2 = false;
let bool_expr = false;

// ANCHOR: control_flow
// if 是一個運算式，因此它回傳一個值；如果有 2 個分支，
// 分支的類型必須匹配。
if (bool_expr) expr1 else expr2;

// while 是一個運算式，但它回傳 `()`。
while (bool_expr) { expr; };

// loop 是一個運算式，但也回傳 `()`。
loop { expr; break };
// ANCHOR_END: control_flow
}
