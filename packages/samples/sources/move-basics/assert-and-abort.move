// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::assert_abort;

#[test, expected_failure(abort_code = 1, location=Self)]
fun test_abort() {

// ANCHOR: abort
let user_has_access = false;

// 如果 `user_has_access` 為 false，則以預定義常數中止
if (!user_has_access) {
    abort 1
};
// ANCHOR_END: abort
}

#[test]
fun show_assert() {
let user_has_access = true;
// ANCHOR: assert
// 如果 `user_has_access` 為 `false`，則以中止碼 0 中止
assert!(user_has_access, 0);

// 展開為：
if (!user_has_access) {
    abort 0
};
// ANCHOR_END: assert
}

// ANCHOR: error_const
/// 使用者無存取權限時的錯誤碼。
const ENoAccess: u64 = 0;
/// 嘗試存取不存在的欄位。
const ENoField: u64 = 1;

/// 更新一筆記錄。
public fun update_record(/* ... , */ user_has_access: bool, field_exists: bool) {
    // 現在 assert 會更容易閱讀
    assert!(user_has_access, ENoAccess);
    assert!(field_exists, ENoField);

    /* ... */
}
// ANCHOR_END: error_const

public struct User { is_authorized: bool, value: u64 }

// ANCHOR: error_attribute
#[error]
const ENotAuthorized: vector<u8> = b"The user is not authorized to perform this action";

#[error]
const EValueTooLow: vector<u8> = b"The value is too low, it should be at least 10";

/// 代表使用者執行操作。
public fun update_value(user: &mut User, value: u64) {
    assert!(user.is_authorized, ENotAuthorized);
    assert!(value >= 10, EValueTooLow);

    user.value = value;
}
// ANCHOR_END: error_attribute
}
