---
title: 'Unit Tests | Reference'
description: 'Move unit testing reference: #[test], #[expected_failure], #[test_only] annotations, test flags, and execution options.'
---

# 單元測試 (Unit Testing)

單元測試是確保 Move 程式碼正確性的關鍵。Move 支持在一個專用模組中編寫測試，或者在現有模組中添加測試。

## 測試註解 (Test Annotations)

- `#[test]`: 將函數標記為測試。
- `#[test_only]`: 將模組或成員標記為僅用於測試。
- `#[expected_failure]`: 指示測試預期會失敗。

## 範例

```move
#[test]
fun test_success() {
    let result = add(1, 1);
    assert!(result == 2);
}

#[test, expected_failure(abort_code = EError)]
fun test_failure() {
    abort EError
}
```

## 執行測試

使用 `sui move test` 命令來運行測試。

```bash
$ sui move test
```

## 測試旗標 (Test Flags)

- `--help`: 顯示幫助。
- `-s` 或 `--statistics`: 顯示測試統計資訊（時間和 Gas 使用量）。
- `-i <bound>`: 限制單筆測試的 Gas 消耗。

## 常見實踐

- 為測試提供描述性名稱。
- 使用 `assert_eq!`（如果可用）來比較值。
- 使用 `sui::test_utils::destroy` 來銷毀測試中的物件。
