// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

module book::constants;

const MAX: u64 = 100;

// 但是你可以使用函式將常數傳遞到外部
public fun max(): u64 {
    MAX
}

// 或者使用
public fun is_max(num: u64): bool {
    num == MAX
}
