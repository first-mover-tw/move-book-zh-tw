// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: enum_test
// 注意，模組已更改！
module book::segment_tests;

use book::segment;

#[test]
fun test_full_enum_cycle() {
    use std::unit_test::assert_eq;

    // 建立不同 Segment 變體的向量。
    let segments = vector[
        segment::new_empty(),
        segment::new_string(b"hello".to_string()),
        segment::new_special(b" ", 0), // 純文字
        segment::new_string(b"move".to_string()),
        segment::new_special(b"21", 1), // 十六進位
    ];

    // 使用 `vector::fold!` 巨集將所有區段聚集成最終字串。
    let result = segments.fold!(b"".to_string(), |mut acc, segment| {
        // 不追加空白區段，僅 `Special` 和 `String`。
        if (!segment.is_empty()) {
            acc.append(segment.to_string());
        };
        acc
    });

    // 檢查結果是否符合預期。
    assert_eq!(result, b"hello move!".to_string());
}
// ANCHOR_END: enum_test
