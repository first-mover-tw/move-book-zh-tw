// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::wrapper_type_pattern;

/// 使用 wrapper 類型模式的非常簡單的棧實現。不允許
/// 存取元素，除非它們被彈出。
public struct Stack<T>(vector<T>) has copy, store, drop;

/// 透過包裝值來建立新實例。
public fun new<T>(value: vector<T>): Stack<T> {
    Stack(value)
}

/// 將一個元素推入棧。
public fun push_back<T>(v: &mut Stack<T>, el: T) {
    v.0.push_back(el);
}

/// 從棧中彈出一個元素。不同於 `vector`，如果棧為空，
/// 此函式不會失敗，並將回傳 `None`。
public fun pop_back<T>(v: &mut Stack<T>): Option<T> {
    if (v.0.length() == 0) option::none()
    else option::some(v.0.pop_back())
}

/// 取得棧的大小。
public fun size<T>(v: &Stack<T>): u64 {
    v.0.length()
}
// ANCHOR_END: main

// ANCHOR: common
/// 允許讀取 `Stack` 的內容。
public fun inner<T>(v: &Stack<T>): &vector<T> { &v.0 }

/// 允許可變存取 `Stack` 的內容。
public fun inner_mut<T>(v: &mut Stack<T>): &mut vector<T> { &mut v.0 }

/// 將 `Stack` 解包成底層 `vector`。
public fun into_inner<T>(v: Stack<T>): vector<T> {
    let Stack(inner) = v;
    inner
}
// ANCHOR_END: common
