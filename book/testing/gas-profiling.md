---
description:
  在 Move 測試中分析 gas 使用量 (Profile Gas Usage in Move Tests)：測量運算成本、比較不同實作方式，並使用
  sui analyze-trace 分析追蹤紀錄
---

# Gas 效能分析 (Gas Profiling) {#gas-profiling}

理解 gas 消耗有助於最佳化你的 Move 程式碼並估算交易成本。Move 測試框架提供內建工具來測量測試執行過程中的 gas 使用量。除此之外，還有一個專門的工具 `sui analyze-trace` 可用於更深入地分析 gas 使用情形。

> `-s` 顯示的統計數據只反映**計算單位（computation units）**——不包含儲存成本。此外，編譯器的計算單位並不會直接對應到實際的鏈上 gas 費用；它們顯示的是相對的計算複雜度，適合用來比較不同實作之間的差異。若要取得實際的 gas 成本，請將你的套件發佈到 testnet 並測量實際交易。

## 簡易測量：測試統計 (Simple Measurement: Test Statistics) {#simple-measurement-test-statistics}

使用 `sui move test` 搭配 `-s` 或 `--statistics` 旗標，可以看到每個測試的執行時間與 gas 消耗量：

```bash
sui move test -s
```

輸出會顯示一個包含三欄的表格：

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

- **Test Name**：測試函式的完整限定名稱
- **Time**：以秒為單位的執行時間
- **Gas Used**：測試消耗的 gas 單位

> 每個測試的總量都包含一筆很大的固定基礎成本——即使是空的測試，也會回報約 998000 個 gas 單位。比較測試時，應觀察它們總量之間的差異，而非絕對數值。

## CSV 輸出 (CSV Output) {#csv-output}

若要進行程式化分析或匯入試算表，可使用 `csv` 選項：

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

時間單位為奈秒，能在比較相似操作時提供更精確的測量。

## Gas 上限 (Gas Limits) {#gas-limits}

使用 `-i` 或 `--gas-limit` 旗標可為測試設定最大 gas 預算。超過此上限的測試會逾時：

```bash
sui move test -i 1000
```

> 此上限是以內部執行 gas 單位來衡量的，並不會與 `Gas Used` 欄位中的數值一對一對應——一個回報約 998000 gas 的簡單測試，在上限為 1000 的情況下依然能輕鬆通過。

當測試超過 gas 上限時的輸出：

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

這在以下情況很有用：

- **找出昂貴的操作**：找出消耗超乎預期 gas 量的測試
- **強制執行 gas 預算**：確保關鍵路徑維持在可接受的範圍內
- **測試 gas 耗盡情形**：驗證你的程式碼能正確處理 gas 用盡的情境（參見
  [預期失敗 (Expected Failures)](./testing-basics.md#expected-failures)）

## 比較不同實作 (Comparing Implementations) {#comparing-implementations}

使用統計資料來比較不同實作之間的 gas 消耗：

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

搭配統計功能執行後可看出差異：

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

迴圈在基礎成本之上額外花費了 77 個 gas 單位，而公式則沒有增加任何可測量的成本。

## 追蹤分析 (Trace Analysis) {#trace-analysis}

若要進行更深入的效能分析，可以從測試中產生執行追蹤（trace），並使用
[speedscope](https://www.speedscope.app/) 將其視覺化。這會顯示依函式呼叫拆解的 gas 消耗火焰圖，讓你能輕易找出 gas 究竟花在哪裡。

### 步驟一：產生追蹤 (Step 1: Generate Traces) {#step-1-generate-traces}

使用 `--trace` 旗標執行測試以產生追蹤檔案：

```bash
sui move test --trace
```

追蹤檔案會被寫入套件根目錄下的 `traces/` 目錄（與 `Move.toml` 同層）。

### 步驟二：產生 Gas 效能分析報告 (Step 2: Generate a Gas Profile) {#step-2-generate-a-gas-profile}

使用 `sui analyze-trace` 搭配 `gas-profile` 子指令，將追蹤檔轉換為效能分析報告：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile
```

這會在目前目錄下輸出一個 `gas_profile_<TRACE_FILE>.json` 檔案。你可以用 `-o` 旗標指定不同的輸出目錄，該旗標須放在 `gas-profile` 子指令之前：

```bash
sui analyze-trace -p traces/<TRACE_FILE> -o ./profiles gas-profile
```

### 步驟三：使用 Speedscope 視覺化 (Step 3: Visualize with Speedscope) {#step-3-visualize-with-speedscope}

安裝 [speedscope](https://www.speedscope.app/) 並開啟效能分析報告：

```bash
npm install -g speedscope
speedscope gas_profile_<TRACE_FILE>.json
```

Speedscope 提供三種檢視方式：

- **Time Order**：由左至右依呼叫順序顯示呼叫堆疊。長條寬度對應 gas 消耗量。
- **Left Heavy**：將重複的呼叫分組，依總 gas 消耗量排序——適合用來找出最昂貴的程式碼路徑。
- **Sandwich**：列出每個函式的 gas 消耗量，包含 **Total**（含被呼叫的函式）與
  **Self**（僅該函式本身）兩欄。

## 延伸閱讀 (Further Reading) {#further-reading}

- [執行測試 (Running Tests)](./testing-basics.md) - 基本測試執行與預期失敗
- [測試工具 (Test Utilities)](./test-utilities.md) - 斷言巨集與測試輔助工具
- [集合 (Collections)](./../programmability/collections.md) - 選擇高效的資料結構
- [追蹤分析 (Trace Analysis)](https://docs.sui.io/references/cli/trace-analysis) - Sui CLI 追蹤分析
  參考文件
