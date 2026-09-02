---
description: 為 Move 測試產生程式碼覆蓋率報告 (Generate code coverage reports for Move tests)：使用 --coverage 旗標與 sui move coverage 找出未測試的程式碼路徑。
---

# 產生涵蓋率報告 (Generating Coverage Reports) {#generating-coverage-reports}

程式碼涵蓋率是一項指標,顯示測試執行期間程式碼的哪些部分被執行。它有助於識別未經測試的程式碼路徑,並確保你的測試足夠全面。`sui move test` 上的 `--coverage` 旗標會產生涵蓋率資料,而 `sui move coverage` 則提供分析工具。

## 執行帶有涵蓋率的測試 (Running Tests with Coverage) {#running-tests-with-coverage}

若要產生涵蓋率資料,請使用 `--coverage` 旗標執行你的測試:

```bash
sui move test --coverage
```

這將會執行所有測試並收集涵蓋率資訊。涵蓋率資料會儲存在套件根目錄(`Move.toml` 旁邊)的 `.coverage_map.mvcov` 檔案中,並可使用 `sui move coverage` 子指令進行分析。

## 涵蓋率摘要 (Coverage Summary) {#coverage-summary}

`sui move coverage summary` 指令會顯示所有模組涵蓋率的高階概覽:

```bash
sui move coverage summary
```

這會輸出一個表格,顯示每個模組的涵蓋率百分比:

```
+-------------------------+
| Move Coverage Summary   |
+-------------------------+
Module 0000000000000000000000000000000000000000000000000000000000000000::my_module
>>> % Module coverage: 85.71
Module 0000000000000000000000000000000000000000000000000000000000000000::another_module
>>> % Module coverage: 100.00
Module 0000000000000000000000000000000000000000000000000000000000000000::untested_module
>>> % Module coverage: 0.00
+-------------------------+
| % Move Coverage: 62.50  |
+-------------------------+
```

> 在此範例中,模組列在其套件地址的完整 32 位元組形式下 - `0x0`。

若要查看依個別函式細分的涵蓋率,請加上 `--summarize-functions` 旗標:

```bash
sui move coverage summary --summarize-functions
```

若要進行程式化處理,你可以以 CSV 格式輸出結果:

```bash
sui move coverage summary --csv
```

## 原始碼涵蓋率 (Source Coverage) {#source-coverage}

`source` 子指令會顯示特定模組的哪些程式碼行被執行:

```bash
sui move coverage source --module <MODULE_NAME>
```

這會顯示帶有涵蓋率標註的原始碼,顯示哪些行被涵蓋(在測試期間執行)以及哪些沒有。這對於識別需要額外測試涵蓋率的特定程式碼路徑很有用。

## LCOV 格式 (LCOV Format) {#lcov-format}

若要與外部工具及 CI/CD 流程整合,你可以以 [LCOV 格式](https://github.com/linux-test-project/lcov) 產生涵蓋率報告。LCOV 是一種廣泛支援的格式,可與許多涵蓋率視覺化工具搭配使用。

首先,使用 `--trace` 旗標執行測試以產生必要的追蹤資料:

```bash
sui move test --coverage --trace
```

接著產生 LCOV 報告:

```bash
sui move coverage lcov
```

這會在目前目錄中建立一個 `lcov.info` 檔案。此檔案包含詳細的涵蓋率資訊,可與以下工具搭配使用:

- [genhtml](https://github.com/linux-test-project/lcov) - 產生 HTML 涵蓋率報告
- [VS Code Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) -
  在你的編輯器中視覺化涵蓋率
- [Codecov](https://codecov.io/) / [Coveralls](https://coveralls.io/) - 上傳至涵蓋率追蹤服務

### 產生 HTML 報告 (Generating HTML Reports) {#generating-html-reports}

若要從 LCOV 檔案產生 HTML 報告,請使用 `genhtml`(LCOV 套件的一部分):

```bash
genhtml lcov.info -o coverage_html
```

這會建立一個 `coverage_html` 目錄,其中包含可在瀏覽器中開啟的互動式 HTML 報告。

### 差異涵蓋率 (Differential Coverage) {#differential-coverage}

`lcov` 指令支援透過 `--differential-test` 旗標進行差異涵蓋率分析。這會顯示哪些行是專門由特定測試所涵蓋:

```bash
sui move coverage lcov --differential-test <TEST_NAME>
```

僅由指定測試命中的行會顯示為已涵蓋,而由指定測試及其他測試同時命中的行則會顯示為未涵蓋。這有助於識別每個測試提供了哪些獨特的涵蓋範圍。

### 單一測試涵蓋率 (Single Test Coverage) {#single-test-coverage}

若要僅為單一測試產生涵蓋率:

```bash
sui move coverage lcov --only-test <TEST_NAME>
```

這對於理解個別測試的涵蓋範圍很有用。

## 位元組碼涵蓋率 (Bytecode Coverage) {#bytecode-coverage}

對於進階除錯,你可以查看針對反組譯位元組碼的涵蓋率:

```bash
sui move coverage bytecode --module <MODULE_NAME>
```

這會顯示位元組碼層級的涵蓋率,這對於理解確切哪些指令被執行很有用。

## 總結 (Summary) {#summary}

| 指令                                                | 說明                              |
| --------------------------------------------------- | --------------------------------- |
| `sui move test --coverage`                          | 執行測試並收集涵蓋率資料          |
| `sui move test --coverage --trace`                  | 執行帶有追蹤資料的測試(LCOV 所需) |
| `sui move coverage summary`                         | 顯示每個模組的涵蓋率百分比        |
| `sui move coverage summary --summarize-functions`   | 顯示依函式細分的涵蓋率            |
| `sui move coverage summary --csv`                   | 以 CSV 格式輸出涵蓋率摘要         |
| `sui move coverage source --module <NAME>`          | 顯示模組的逐行涵蓋率              |
| `sui move coverage lcov`                            | 產生 LCOV 報告(`lcov.info`)       |
| `sui move coverage lcov --differential-test <TEST>` | 顯示由特定測試專門涵蓋的行        |
| `sui move coverage lcov --only-test <TEST>`         | 為單一測試產生涵蓋率              |
| `sui move coverage bytecode --module <NAME>`        | 顯示針對反組譯位元組碼的涵蓋率    |
