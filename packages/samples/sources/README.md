# 管理範例

對於書中每一頁（位於 `src/` 目錄下），都有一個 `samples/` 目錄，其中包含該頁面的程式碼範例。`samples/` 目錄的組織方式與 `src/` 目錄相同，具有相同的目錄結構和檔案名稱。

## 規則

1. 書中每一頁都有一個 Move 檔案。
2. 檔案名稱與頁面名稱相同（或關鍵字類似）。
3. 該檔案可以包含多個模組。
4. 模組以頁面的子章節命名。
5. 應使用錨點指向 Move 檔案中的特定程式碼片段。

## 範例

例如，`src/basic-syntax/address.md` 頁面有對應的 `samples/guides/address.move` 檔案。該檔案包含頁面的程式碼範例，並以頁面的子章節命名的模組組織。

```bash
samples/
    basic-syntax/
        address.move
```
