---
description: 為 Move 測試產生程式碼涵蓋率 (code coverage) 報告：使用 `--coverage` 旗標和 `sui move coverage` 識別未測試的程式碼路徑。
title: 產生涵蓋率報告 (Generating Coverage Reports)
keywords:
  - Move
  - Sui
  - Move tutorial
  - generating
  - coverage
  - reports
questions:
  - What is Generating Coverage Reports in Move?
  - How do I use Generating Coverage Reports in Move?
  - What is Running Tests with Coverage in Move?
  - What is Coverage Summary in Move?
answer: 'Generate code coverage reports for Move tests: use the --coverage flag and sui move coverage to identify untested code paths.'
goal:
  description: 'Reader understands generate code coverage reports for Move tests: use the --coverage flag and sui move coverage to identify untested code paths'
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 50
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 產生覆蓋率報告 (Generating Coverage Reports) {#generating-coverage-reports}

程式碼覆蓋率是一項指標，用於顯示在測試期間執行了程式碼的哪些部分。它有助於識別未經測試的程式碼路徑，並確保測試足夠完整。`sui move test` 上的 `--coverage` 旗標會產生覆蓋率資料，而 `sui move coverage` 提供用於分析這些資料的工具。

## 使用覆蓋率執行測試 (Running Tests with Coverage) {#running-tests-with-coverage}

若要產生覆蓋率資料，請使用 `--coverage` 旗標執行測試：

```bash
sui move test --coverage
```

這會執行所有測試並收集覆蓋率資訊。覆蓋率資料會儲存在套件根目錄中（位於 `Move.toml` 旁）的 `.coverage_map.mvcov` 檔案，並可使用 `sui move coverage` 子命令進行分析。

## 覆蓋率摘要 (Coverage Summary) {#coverage-summary}

`sui move coverage summary` 命令會顯示所有模組覆蓋率的高階概覽：

```bash
sui move coverage summary
```

這會輸出一個表格，顯示每個模組的覆蓋率百分比：

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

> 模組會列在其套件地址完整的 32 位元組形式之下——在此範例中為 `0x0`。

若要查看依個別函式細分的覆蓋率，請加入 `--summarize-functions` 旗標：

```bash
sui move coverage summary --summarize-functions
```

若要進行程式化處理，可以 CSV 格式輸出結果：

```bash
sui move coverage summary --csv
```

## 原始碼覆蓋率 (Source Coverage) {#source-coverage}

`source` 子命令會顯示特定模組中哪些行已執行：

```bash
sui move coverage source --module <MODULE_NAME>
```

這會顯示附有覆蓋率註解的原始碼，指出哪些行已被覆蓋（在測試期間執行），以及哪些行尚未被覆蓋。這對於識別需要額外測試覆蓋率的特定程式碼路徑很有幫助。

## LCOV 格式 (LCOV Format) {#lcov-format}

若要與外部工具及 CI/CD 管線整合，可以產生 [LCOV 格式](https://github.com/linux-test-project/lcov)的覆蓋率報告。LCOV 是受到廣泛支援的格式，可搭配許多覆蓋率視覺化工具使用。

首先，使用 `--trace` 旗標執行測試以產生必要的追蹤資料：

```bash
sui move test --coverage --trace
```

接著產生 LCOV 報告：

```bash
sui move coverage lcov
```

這會在目前目錄建立 `lcov.info` 檔案。該檔案包含詳細的覆蓋率資訊，可搭配以下工具使用：

- [genhtml](https://github.com/linux-test-project/lcov) - 產生 HTML 覆蓋率報告
- [VS Code Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) -
  在編輯器中視覺化覆蓋率
- [Codecov](https://codecov.io/) / [Coveralls](https://coveralls.io/) - 上傳至覆蓋率追蹤服務

### 產生 HTML 報告 (Generating HTML Reports) {#generating-html-reports}

若要從 LCOV 檔案產生 HTML 報告，請使用 `genhtml`（LCOV 套件的一部分）：

```bash
genhtml lcov.info -o coverage_html
```

這會建立 `coverage_html` 目錄，其中包含可在瀏覽器中開啟的互動式 HTML 報告。

### 差異覆蓋率 (Differential Coverage) {#differential-coverage}

`lcov` 命令支援使用 `--differential-test` 旗標進行差異覆蓋率分析。這會顯示只有特定測試覆蓋的行：

```bash
sui move coverage lcov --differential-test <TEST_NAME>
```

只有指定測試命中的行會顯示為已覆蓋，而指定測試與其他測試皆命中的行則會顯示為未覆蓋。這有助於識別每項測試提供的獨特覆蓋率。

### 單一測試覆蓋率 (Single Test Coverage) {#single-test-coverage}

若要僅產生單一測試的覆蓋率：

```bash
sui move coverage lcov --only-test <TEST_NAME>
```

這有助於瞭解個別測試的覆蓋範圍。

## 位元碼覆蓋率 (Bytecode Coverage) {#bytecode-coverage}

若要進行進階除錯，可以查看相對於反組譯位元碼的覆蓋率：

```bash
sui move coverage bytecode --module <MODULE_NAME>
```

這會顯示位元碼層級的覆蓋率，有助於瞭解確切執行了哪些指令。

## 總結 (Summary) {#summary}

| 命令                                                | 說明                              |
| --------------------------------------------------- | --------------------------------- |
| `sui move test --coverage`                          | 執行測試並收集覆蓋率資料          |
| `sui move test --coverage --trace`                  | 使用追蹤資料執行測試（LCOV 必要） |
| `sui move coverage summary`                         | 顯示每個模組的覆蓋率百分比        |
| `sui move coverage summary --summarize-functions`   | 顯示依函式細分的覆蓋率            |
| `sui move coverage summary --csv`                   | 以 CSV 格式輸出覆蓋率摘要         |
| `sui move coverage source --module <NAME>`          | 顯示模組逐行的覆蓋率              |
| `sui move coverage lcov`                            | 產生 LCOV 報告（`lcov.info`）     |
| `sui move coverage lcov --differential-test <TEST>` | 顯示僅由某項測試覆蓋的行          |
| `sui move coverage lcov --only-test <TEST>`         | 產生單一測試的覆蓋率              |
| `sui move coverage bytecode --module <NAME>`        | 顯示相對於反組譯位元碼的覆蓋率    |
