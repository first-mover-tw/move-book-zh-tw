// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_function)]
// ANCHOR: main
module book::comments_block;

fun /* 您可以在任何地方注釋 */ go_wild() {
    /* 這裡
        那裡
        到處都是 */ let a = 10;
    let b = /* 甚至在這裡 */ 10; /* 然後再次 */
    a + b;
}
/* 您可以使用它來移除某些表達式或定義
fun empty_commented_out() {

}
*/
// ANCHOR_END: main
