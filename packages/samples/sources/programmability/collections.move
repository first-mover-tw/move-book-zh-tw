// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_field)]
// ANCHOR: vector
module book::collections_vector;

use std::string::String;

/// 可由 `BookStore` 銷售的書籍
public struct Book has key, store {
    id: UID,
    name: String
}

/// 販售 `Book` 的書店
public struct BookStore has key, store {
    id: UID,
    books: vector<Book>
}
// ANCHOR_END: vector
