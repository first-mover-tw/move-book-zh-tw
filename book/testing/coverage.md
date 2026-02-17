---
description: "為 Move 測試生成程式碼覆蓋率報告：使用 --coverage 標誌和 sui move coverage 來識別未測試的程式碼路徑。"
---

# 生成覆蓋率報告 (Generating Coverage Reports)

程式碼覆蓋率是一個指標，顯示你的程式碼有哪些部分在測試期間被執行了。它有助於識別未測試的程式碼路徑，確保你的測試是全面的。`sui move test` 上的 `--coverage` 標誌會生成覆蓋率數據，而 `sui move coverage` 提供了分析這些數據的工具。

## 執行帶有覆蓋率的測試

要生成覆蓋率數據，請使用 `--coverage` 標誌執行你的測試：

```bash
sui move test --coverage
```

這將執行所有測試並收集覆蓋率資訊。覆蓋率數據存儲在 `build` 目錄中，並可以使用 `sui move coverage` 子命令進行分析。

## 覆蓋率摘要

`sui move coverage summary` 命令顯示所有模組覆蓋率的高層次概覽：

```bash
sui move coverage summary
```

這會輸出一個表格，顯示每個模組的覆蓋率百分比：

```
+-------------------------+
| Move Coverage Summary   |
+-------------------------+
| Module 0x0::my_module   |
| >>> % Module coverage: 85.71 |
| Module 0x0::another_module   |
| >>> % Module coverage: 100.00 |
| Module 0x0::untested_module  |
| >>> % Module coverage: 0.00  |
+-------------------------+
| % Move Coverage: 62.50  |
+-------------------------+
```

要查看按個別函式細分的覆蓋率，請添加 `--summarize-functions` 標誌：

```bash
sui move coverage summary --summarize-functions
```

為了便於程式化處理，你可以以 CSV 格式輸出結果：

```bash
sui move coverage summary --csv
```

## 原始碼覆蓋率 (Source Coverage)

`source` 子命令顯示特定模組的哪些行被執行了：

```bash
sui move coverage source --module <MODULE_NAME>
```

這會顯示帶有覆蓋率註釋的原始碼，顯示哪些行已被覆蓋 (在測試期間執行)，哪些行未被覆蓋。這對於識別需要額外測試覆蓋的特定程式碼路徑非常有用。

## LCOV 格式

為了與外部工具和 CI/CD 流程整合，你可以生成 [LCOV 格式](https://github.com/linux-test-project/lcov) 的覆蓋率報告。LCOV 是一種廣泛支援的格式，適用於許多覆蓋率視覺化工具。

首先，使用 `--trace` 標誌執行測試以生成必要的追蹤 (trace) 數據：

```bash
sui move test --coverage --trace
```

然後生成 LCOV 報告：

```bash
sui move coverage lcov
```

這會在當前目錄中建立一個 `lcov.info` 檔案。該檔案包含詳細的覆蓋率資訊，可與以下工具一起使用：

- [genhtml](https://github.com/linux-test-project/lcov) - 生成 HTML 覆蓋率報告
- [VS Code Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) - 在編輯器中視覺化覆蓋率
- [Codecov](https://codecov.io/) / [Coveralls](https://coveralls.io/) - 上傳到覆蓋率追蹤服務

### 生成 HTML 報告

要從 LCOV 檔案生成 HTML 報告，請使用 `genhtml` (LCOV 套件的一部分)：

```bash
genhtml lcov.info -o coverage_html
```

這會建立一個 `coverage_html` 目錄，其中包含一個可以在瀏覽器中打開的互動式 HTML 報告。

### 差異覆蓋率 (Differential Coverage)

`lcov` 命令支援使用 `--differential-test` 標誌進行差異覆蓋率分析。這顯示了哪些行僅由特定測試覆蓋：

```bash
sui move coverage lcov --differential-test <TEST_NAME>
```

僅被指定測試命中的行顯示為已覆蓋，而被指定測試和其他測試同時命中的行顯示為未覆蓋。這有助於識別每個測試提供的獨特覆蓋範圍。

### 單一測試覆蓋率

要僅為單個測試生成覆蓋率：

```bash
sui move coverage lcov --only-test <TEST_NAME>
```

這對於理解個別測試的覆蓋範圍非常有用。

## 字節碼覆蓋率 (Bytecode Coverage)

對於進階除錯，你可以查看針對反組譯字節碼的覆蓋率：

```bash
sui move coverage bytecode --module <MODULE_NAME>
```

這顯示了字節碼層級的覆蓋率，對於理解確切執行了哪些指令可能很有用。

## 總結

| 命令 | 描述 |
| --- | --- |
| `sui move test --coverage` | 執行測試並收集覆蓋率數據 |
| `sui move test --coverage --trace` | 執行帶有追蹤數據的測試 (LCOV 需要) |
| `sui move coverage summary` | 顯示每個模組的覆蓋率百分比 |
| `sui move coverage summary --summarize-functions` | 顯示按函式細分的覆蓋率 |
| `sui move coverage summary --csv` | 以 CSV 格式輸出覆蓋率摘要 |
| `sui move coverage source --module <NAME>` | 顯示模組的逐行覆蓋率 |
| `sui move coverage lcov` | 生成 LCOV 報告 (`lcov.info`) |
| `sui move coverage lcov --differential-test <TEST>` | 顯示僅由測試覆蓋的行 |
| `sui move coverage lcov --only-test <TEST>` | 生成單個測試的覆蓋率 |
| `sui move coverage bytecode --module <NAME>` | 顯示針對反組譯字節碼的覆蓋率 |
