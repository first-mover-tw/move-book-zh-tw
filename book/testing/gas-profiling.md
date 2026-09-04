---
description: 在 Move 測試中分析 gas 使用量：測量運算成本、比較實作方式，並使用 sui analyze-trace 分析追蹤記錄。
title: gas 分析 (Gas Profiling)
keywords:
  - Move
  - Sui
  - Move tutorial
  - gas
  - profiling
questions:
  - What is Gas Profiling in Move?
  - How do I use Gas Profiling in Move?
  - 'What is Simple Measurement: Test Statistics in Move?'
  - What is CSV Output in Move?
answer: 'Profile gas usage in Move tests: measure computation costs, compare implementations, and analyze traces with sui analyze-trace.'
goal:
  description: 'Reader understands profile gas usage in Move tests: measure computation costs, compare implementations, and analyze traces with sui analyze-trace'
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

# Gas 用量剖析 (Gas Profiling) {#gas-profiling}

瞭解 gas 消耗情況有助於最佳化 Move 程式碼，並估算交易成本。Move
測試框架提供內建工具，可在測試執行期間測量 gas 用量。此外，也提供特殊工具
`sui analyze-trace`，可更徹底地分析 gas 用量。

> `-s` 顯示的統計資料僅反映**計算單位**，不包含儲存
> 成本。此外，編譯器計算單位不會直接對應至實際鏈上 gas 費用；
> 它們顯示的是相對計算複雜度，適合用於相互比較不同實作。
> 若要取得實際 gas 成本，請將套件發布至 testnet 並測量真實交易。

## 簡易測量：測試統計資料 (Simple Measurement: Test Statistics) {#simple-measurement-test-statistics}

搭配 `sui move test` 使用 `-s` 或 `--statistics` 旗標，即可查看每個測試的執行時間和
gas 消耗量：

```bash
sui move test -s
```

輸出會顯示包含三個欄位的表格：

```table
Test Statistics:

┌────────────────────────────────────────────────────────┬────────────┬───────────────────────────┐
│                       Test Name                        │    Time    │         Gas Used          │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_simple_operation                 │   0.006    │          998001           │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_complex_operation                │   0.007    │          998068           │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_with_objects                     │   0.006    │          998001           │
└────────────────────────────────────────────────────────┴────────────┴───────────────────────────┘

Test result: OK. Total tests: 3; passed: 3; failed: 0
```

- **測試名稱**：測試函式的完整限定名稱
- **時間**：以秒為單位的執行時間
- **已使用的 Gas**：測試消耗的 gas 單位

> 每個測試的總計都包含一筆很大的固定基本成本；即使空白測試也會顯示約 998000 個
> gas 單位。比較測試時，應查看總計之間的差異，而非
> 絕對值。

## CSV 輸出 (CSV Output) {#csv-output}

若要進行程式化分析或匯入試算表，請使用 `csv` 選項：

```bash
sui move test -s csv
```

這會產生以逗號分隔的輸出：

```
name,nanos,gas
book::my_module::test_simple_operation,5992125,998001
book::my_module::test_complex_operation,6870583,998068
book::my_module::test_with_objects,6022917,998001
```

時間單位為奈秒，可在比較相似操作時進行更精確的測量。

## Gas 限制 (Gas Limits) {#gas-limits}

使用 `-i` 或 `--gas-limit` 旗標，可為測試設定最大 gas 預算。超過此限制的測試
將會逾時：

```bash
sui move test -i 1000
```

> 此限制以內部執行 gas 單位衡量，與 `Gas Used` 欄位中的值並非一對一對應；
> 顯示約 998000 gas 的簡單測試，在限制為 1000 時仍可輕鬆
> 通過。

測試超出 gas 限制時的輸出：

```
[ TIMEOUT ] book::my_module::test_complex_operation
[ PASS    ] book::my_module::test_simple_operation
[ PASS    ] book::my_module::test_with_objects

Test failures:

Failures in book::my_module:

┌── test_complex_operation ──────
│ Test timed out
└──────────────────

Test result: FAILED. Total tests: 3; passed: 2; failed: 1
```

這適用於：

- **識別高成本操作**：找出消耗超出預期 gas 數量的測試
- **強制實施 gas 預算**：確保關鍵路徑維持在可接受的限制內
- **測試 gas 耗盡**：驗證你的程式碼能正確處理 gas 耗盡情境（請參閱
  [預期失敗](./testing-basics.md#expected-failures)）

## 比較實作 (Comparing Implementations) {#comparing-implementations}

使用統計資料比較不同實作之間的 gas 消耗量：

```move
module book::comparison;

use std::unit_test::assert_eq;

public fun sum_loop(n: u64): u64 {
    let mut sum = 0;
    n.do!(|i| sum = sum + i);
    sum
}

public fun sum_formula(n: u64): u64 {
    n * (n - 1) / 2
}

#[test]
fun test_sum_loop() {
    let result = sum_loop(1000);
    assert_eq!(result, 499500);
}

#[test]
fun test_sum_formula() {
    let result = sum_formula(1000);
    assert_eq!(result, 499500);
}
```

搭配統計資料執行可顯示差異：

```bash
sui move test comparison -s
```

```table
┌────────────────────────────────────┬────────────┬───────────────────────────┐
│           Test Name                │    Time    │         Gas Used          │
├────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::comparison::test_sum_loop    │   0.003    │          998078           │
├────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::comparison::test_sum_formula │   0.001    │          998001           │
└────────────────────────────────────┴────────────┴───────────────────────────┘
```

迴圈在基本成本之外需額外花費 77 個 gas 單位，而公式沒有增加可測量的成本。

## 追蹤分析 (Trace Analysis) {#trace-analysis}

若要進行更深入的剖析，可以從測試產生執行追蹤，並使用
[speedscope](https://www.speedscope.app/) 將其視覺化。這會顯示依函式
呼叫細分的 gas 消耗火焰圖，讓你能輕易找出 gas 的確切花費位置。

### 步驟 1：產生追蹤 (Step 1: Generate Traces) {#step-1-generate-traces}

使用 `--trace` 旗標執行測試，以產生追蹤文件：

```bash
sui move test --trace
```

追蹤文件會寫入套件根目錄中的 `traces/` 目錄（位於 `Move.toml` 旁）。

### 步驟 2：產生 Gas 設定檔 (Step 2: Generate a Gas Profile) {#step-2-generate-a-gas-profile}

使用 `sui analyze-trace` 的 `gas-profile` 子命令，將追蹤轉換為設定檔：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile
```

這會在目前目錄輸出 `gas_profile_<TRACE_FILE>.json` 文件。你可以使用
`-o` 旗標指定不同的輸出目錄；該旗標必須位於 `gas-profile` 子命令之前：

```bash
sui analyze-trace -p traces/<TRACE_FILE> -o ./profiles gas-profile
```

### 步驟 3：使用 Speedscope 視覺化 (Step 3: Visualize with Speedscope) {#step-3-visualize-with-speedscope}

安裝 [speedscope](https://www.speedscope.app/) 並開啟設定檔：

```bash
npm install -g speedscope
speedscope gas_profile_<TRACE_FILE>.json
```

Speedscope 提供三種檢視方式：

- **時間順序**：依呼叫順序由左至右顯示呼叫堆疊。長條寬度對應
  gas 消耗量。
- **左重**：將重複呼叫分組，並依總 gas 消耗量排序，適合用於
  找出成本最高的程式碼路徑。
- **三明治**：列出每個函式的 gas 消耗量，包含**總計**（含被呼叫函式）與
  **自身**（僅函式本身）欄位。

## 延伸閱讀 (Further Reading) {#further-reading}

- [執行測試](./testing-basics.md) - 基本測試執行與預期失敗
- [測試工具](./test-utilities.md) - 斷言巨集與測試輔助工具
- [集合](./../programmability/collections.md) - 選擇高效率的資料結構
- [追蹤分析](https://docs.sui.io/references/cli/trace-analysis) - Sui CLI 追蹤分析
  參考文件
