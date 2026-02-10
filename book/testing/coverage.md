---
description: "為 Move 測試生成程式碼覆蓋率報告：使用 --coverage 標誌和 sui move coverage 來識別未測試的程式碼路徑。"
---

# 生成覆蓋率報告 (Generating Coverage Reports)

程式碼覆蓋率是一個指標，顯示您的程式碼在測試期間執行的部分。它幫助識別未測試的程式碼路徑，並確保您的測試是全面的。`sui move test` 上的 `--coverage` 標誌生成覆蓋率資料，而 `sui move coverage` 提供工具來分析它。

## 使用覆蓋率運行測試 (Running Tests with Coverage)

要生成覆蓋率資料，請使用 `--coverage` 標誌運行您的測試：

```bash
sui move test --coverage
```

這將運行所有測試並收集覆蓋率資訊。覆蓋率資料存儲在 `build` 目錄中，可以使用 `sui move coverage` 子命令進行分析。

## 覆蓋率摘要 (Coverage Summary)

`sui move coverage summary` 命令顯示所有模組的覆蓋率高級概覽：

```bash
sui move coverage summary
```

這將輸出一個表格，顯示每個模組的覆蓋率百分比：

```
+-------------------------+
| Move Coverage Summary   |
+-------------------------+
Module 0x0::my_module
>>> % Module coverage: 85.71
Module 0x0::another_module
>>> % Module coverage: 100.00
Module 0x0::untested_module
>>> % Module coverage: 0.00
+-------------------------+
| % Move Coverage: 62.50  |
+-------------------------+
```

要按單個函式查看覆蓋率，請添加 `--summarize-functions` 標誌：

```bash
sui move coverage summary --summarize-functions
```

對於程式化處理，您可以以 CSV 格式輸出結果：

```bash
sui move coverage summary --csv
```

## 原始程式碼覆蓋率 (Source Coverage)

`source` 子命令顯示特定模組的哪些行被執行：

```bash
sui move coverage source --module <MODULE_NAME>
```

這顯示原始程式碼以及覆蓋率註解，顯示哪些行被覆蓋（在測試期間執行）以及哪些行未被覆蓋。這對於識別需要額外測試覆蓋率的特定程式碼路徑很有用。

## LCOV 格式 (LCOV Format)

為了與外部工具和 CI/CD 流水線集成，您可以生成 [LCOV 格式](https://github.com/linux-test-project/lcov)的覆蓋率報告。LCOV 是一種廣泛支持的格式，適用於許多覆蓋率視覺化工具。

首先，使用 `--trace` 標誌運行測試以生成必要的追蹤資料：

```bash
sui move test --coverage --trace
```

然後生成 LCOV 報告：

```bash
sui move coverage lcov
```

這將在當前目錄中建立 `lcov.info` 檔案。該檔案包含詳細的覆蓋率資訊，可與以下工具一起使用：

- [genhtml](https://github.com/linux-test-project/lcov) - 生成 HTML 覆蓋率報告
- [VS Code Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) -
  在您的編輯器中視覺化覆蓋率
- [Codecov](https://codecov.io/) / [Coveralls](https://coveralls.io/) - 上傳到覆蓋率跟蹤服務

### 生成 HTML 報告 (Generating HTML Reports)

要從 LCOV 檔案生成 HTML 報告，請使用 `genhtml`（LCOV 套件的一部分）：

```bash
genhtml lcov.info -o coverage_html
```

這將建立一個 `coverage_html` 目錄，其中包含可在瀏覽器中打開的互動式 HTML 報告。

### 差異覆蓋率 (Differential Coverage)

`lcov` 命令支持差異覆蓋率分析，使用 `--differential-test` 標誌。這顯示哪些行專由特定測試覆蓋：

```bash
sui move coverage lcov --differential-test <TEST_NAME>
```

僅由指定的測試命中的行顯示為已覆蓋，而由指定的測試和其他測試都命中的行顯示為未覆蓋。這有助於識別每個測試提供的獨特覆蓋率。

### 單一測試覆蓋率 (Single Test Coverage)

要僅為單一測試生成覆蓋率：

```bash
sui move coverage lcov --only-test <TEST_NAME>
```

這對於瞭解個別測試的覆蓋率範圍很有用。

## 位元組碼覆蓋率 (Bytecode Coverage)

對於進階除錯，您可以針對反組譯位元組碼查看覆蓋率：

```bash
sui move coverage bytecode --module <MODULE_NAME>
```

這顯示位元組碼級別的覆蓋率，這對於瞭解執行的確切指令很有用。

## 摘要 (Summary)

| 命令 | 描述 |
| --- | --- |
| `sui move test --coverage` | 運行測試並收集覆蓋率資料 |
| `sui move test --coverage --trace` | 運行測試並追蹤資料（LCOV 必需） |
| `sui move coverage summary` | 顯示每個模組的覆蓋率百分比 |
| `sui move coverage summary --summarize-functions` | 按函式顯示覆蓋率 |
| `sui move coverage summary --csv` | 以 CSV 格式輸出覆蓋率摘要 |
| `sui move coverage source --module <NAME>` | 顯示模組的逐行覆蓋率 |
| `sui move coverage lcov` | 生成 LCOV 報告（`lcov.info`） |
| `sui move coverage lcov --differential-test <TEST>` | 顯示專由測試覆蓋的行 |
| `sui move coverage lcov --only-test <TEST>` | 為單一測試生成覆蓋率 |
| `sui move coverage bytecode --module <NAME>` | 顯示針對反組譯位元組碼的覆蓋率 |
