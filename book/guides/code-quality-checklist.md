# 程式碼品質檢查清單 (Code Quality Checklist)

本指南提供了一份針對 Move 2024 的程式碼品質檢查清單，旨在幫助開發者編寫更乾淨、更高效且更易於維護的 Move 程式碼。

## 函式語法

### 避免 `public(friend)`，改用 `public(package)`
### 元組解構使用 `let mut` 或 `let (.., x)`
### 方法呼叫優先於靜態呼叫

## 結構與方法

### 公開欄位應謹慎使用
### 為常見操作實作方法 (Methods)
### `UID` 具有 `delete()` 方法

## 測試 (Testing)

### 使用 `assert_eq!`
### 使用 `destroy` 進行清理
### 測試名稱應具有描述性

（詳細內容請參閱英文原始版本的範例代碼）
