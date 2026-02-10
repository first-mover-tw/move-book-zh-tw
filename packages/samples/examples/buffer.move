// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::buffer;

/// 當緩衝區溢位時回傳的錯誤。
const EBufferOverflow: u64 = 0;

/// Buffer 結構體代表一個可增長的緩衝區。
public struct Buffer {
    data: vector<u8>,
    expected_len: Option<u64>
}

/// 建立一個新的空白緩衝區。
public fun new(): Buffer {
    Buffer { data: vector[], expected_len: option::none() }
}

/// 建立一個新的空白緩衝區，指定容量（以位元組為單位）。
/// 如果緩衝區溢位，交易會中止並回傳 `EBufferOverflow`。
public fun alloc(len: u64): Buffer {
    Buffer { data: vector[], expected_len: option::some(len) }
}

/// 將指定資料推入緩衝區的末尾。
public fun push(self: &mut Buffer, data: vector<u8>) {
    self.expected_len.do_ref!(|max_len| assert!(self.len() + data.length() <= *max_len, EBufferOverflow));
    self.data.append(data)
}

/// 解包緩衝區並回傳底層的向量。
public fun unwrap(self: Buffer): vector<u8> {
    let Buffer { data, expected_len: _ } = self;
    data
}

/// 回傳緩衝區的長度。
public fun len(self: &Buffer): u64 {
    self.data.length()
}

/// 如果緩衝區為空，回傳 `true`。
public fun is_empty(self: &Buffer): bool {
    self.data.is_empty()
}
