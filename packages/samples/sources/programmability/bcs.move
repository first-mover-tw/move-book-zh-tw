// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

#[allow(unused_variable, unused_field)]
module book::bcs {
    use std::string::String;

public struct CustomData has drop {
    num: u8,
    string: String,
    value: bool
}

public struct User has drop {
    age: u8,
    is_active: bool,
    name: String
}

#[test_only]
use std::unit_test::assert_eq;

#[test] fun test_encode() {
// ANCHOR: encode
use sui::bcs;

// 0x01 - 單個位元組，值為 1（或 false 為 0）
let bool_bytes = bcs::to_bytes(&true);
assert_eq!(bool_bytes, x"01");

// 0x2a - 只是單個位元組
let u8_bytes = bcs::to_bytes(&42u8);
assert_eq!(u8_bytes, x"2A");

// 0x2a00000000000000 - 8 個位元組
let u64_bytes = bcs::to_bytes(&42u64);
assert_eq!(u64_bytes, x"2A00000000000000");

// 位址是 32 個位元組的固定序列
// 0x0000000000000000000000000000000000000000000000000000000000000002
let addr = bcs::to_bytes(&@sui);
assert_eq!(addr, x"0000000000000000000000000000000000000000000000000000000000000002");
// ANCHOR_END: encode

// ANCHOR: encode_struct
let data = CustomData {
    num: 42,
    string: b"hello, world!".to_string(),
    value: true
};

let struct_bytes = bcs::to_bytes(&data);

let mut custom_bytes = vector[];
custom_bytes.append(bcs::to_bytes(&42u8));
custom_bytes.append(bcs::to_bytes(&b"hello, world!".to_string()));
custom_bytes.append(bcs::to_bytes(&true));

// 結構只是欄位的序列，所以位元組應該相同！
assert_eq!(struct_bytes, custom_bytes);
// ANCHOR_END: encode_struct
}

#[test] fun test_bcs() {
// ANCHOR: decode
use sui::bcs;

// BCS 實例應該總是宣告為可變
let mut bcs = bcs::new(x"010000000000000000");

// 相同的位元組可以以不同方式讀取，例如：Option<u64>
let value: Option<u64> = bcs.peel_option_u64();

assert_eq!(value.is_some(), true);
assert_eq!(*value.borrow(), 0);

let remainder = bcs.into_remainder_bytes();

assert_eq!(remainder.length(), 0);
// ANCHOR_END: decode

// ANCHOR: chain_decode
let mut bcs = bcs::new(x"0101010F0000000000F00000000000");

// 注意順序！！！
// 提取多個值的便利方式
let (bool_value, u8_value, u64_value) = (
    bcs.peel_bool(),
    bcs.peel_u8(),
    bcs.peel_u64()
);
// ANCHOR_END: chain_decode

// ANCHOR: decode_vector
let mut bcs = bcs::new(x"0101010F0000000000F00000000000");

// bcs.peel_vec_length() 提取向量的長度 :)
let mut len = bcs.peel_vec_length();
let mut vec = vector[];

// 然後根據資料型別迭代
while (len > 0) {
    vec.push_back(bcs.peel_u64()); // 或任何其他型別
    len = len - 1;
};

assert_eq!(vec.length(), 1);

// 上面的 `while` 可以使用 `巨集` 簡化並使其更易讀。
// bcs.peel_vec!(|bcs| bcs.peel_u64()) 等效於上面的 `while` 迴圈。
// ANCHOR_END: decode_vector

// ANCHOR: decode_option
let mut bcs = bcs::new(x"00");
let is_some = bcs.peel_bool();

assert_eq!(is_some, false);

let mut bcs = bcs::new(x"0101");
let is_some = bcs.peel_bool();
let value = bcs.peel_u8();

assert_eq!(is_some, true);
assert_eq!(value, 1);
// ANCHOR_END: decode_option

// ANCHOR: decode_struct
let mut bcs = bcs::new(x"0101010F0000000000F00000000000");

// 注意：順序很重要！
let user = User {
    age: bcs.peel_u8(),
    is_active: bcs.peel_bool(),
    name: bcs.peel_vec_u8().to_string()
};
// ANCHOR_END: decode_struct
}
}
