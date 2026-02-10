---
description: "在 Move 測試中進行 Gas 分析：測量計算成本、比較實作方案，並使用 sui analyze-trace 分析追蹤記錄。"
---

# Gas 分析 (Gas Profiling)

了解 gas 消耗有助於最佳化你的 Move 程式碼並估算交易成本。Move 測試框架提供內建工具，可在測試執行期間測量 gas 使用量。此外，還有一個特別的工具 `sui analyze-trace` 可用於更深入的 gas 使用分析。

> `-s` 顯示的統計數據只反映**計算單元**——不包括儲存成本。此外，編譯器計算單元不直接對應到實際鏈上的 gas 費用；它們顯示相對計算複雜度，適合用於比較不同實作之間的效能。若要獲得實際 gas 成本，請將你的套件發佈到測試網並測量真實交易。

## 簡單測量：測試統計 (Simple Measurement: Test Statistics)

使用 `sui move test` 搭配 `-s` 或 `--statistics` 旗標，可查看每個測試的執行時間和 gas 消耗：

```bash
sui move test -s
```

輸出會顯示包含三欄的表格：

```table
Test Statistics:

┌────────────────────────────────────────────────────────┬────────────┬───────────────────────────┐
│                       Test Name                        │    Time    │         Gas Used          │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_simple_operation                 │   0.003    │             1             │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_complex_operation                │   0.011    │            59             │
├────────────────────────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::my_module::test_with_objects                     │   0.008    │            25             │
└────────────────────────────────────────────────────────┴────────────┴───────────────────────────┘

Test result: OK. Total tests: 3; passed: 3; failed: 0
```

- **Test Name**：測試函式的完全限定名稱
- **Time**：執行時間（以秒為單位）
- **Gas Used**：測試消耗的 gas 單元數

## CSV 輸出 (CSV Output)

若要進行程式化分析或匯入試算表，請使用 `csv` 選項：

```bash
sui move test -s csv
```

這會產生以逗號分隔的輸出：

```
test_name,time_ns,gas_used
book::my_module::test_simple_operation,3381750,1
book::my_module::test_complex_operation,8454125,59
book::my_module::test_with_objects,3905625,25
```

時間以奈秒為單位，可在比較類似操作時提供更精確的測量。

## Gas 限制 (Gas Limits)

使用 `-i` 或 `--gas-limit` 旗標為測試設定最大 gas 預算。超過此限制的測試將逾時：

```bash
sui move test -i 50
```

當測試超過 gas 限制時的輸出：

```
[ PASS    ] book::my_module::test_simple_operation
[ TIMEOUT ] book::my_module::test_complex_operation
[ PASS    ] book::my_module::test_with_objects

Test failures:

Failures in book::my_module:

┌── test_complex_operation ──────
│ Test timed out
└──────────────────
```

這對以下情況很有用：

- **識別昂貴的操作**：找出消耗意外大量 gas 的測試
- **強制執行 gas 預算**：確保關鍵路徑保持在可接受限制內
- **測試 gas 耗盡**：驗證你的程式碼是否正確處理 gas 不足的情況（見[預期的失敗](./testing-basics.md#expected-failures)）

## 比較實作方案 (Comparing Implementations)

使用統計來比較不同實作之間的 gas 消耗：

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
    let result = sum_loop(100);
    assert_eq!(result, 4950);
}

#[test]
fun test_sum_formula() {
    let result = sum_formula(100);
    assert_eq!(result, 4950);
}
```

使用統計執行會揭示差異：

```bash
sui move test -s comparison
```

```table
┌────────────────────────────────────┬────────────┬───────────────────────────┐
│           Test Name                │    Time    │         Gas Used          │
├────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::comparison::test_sum_loop    │   0.005    │            201            │
├────────────────────────────────────┼────────────┼───────────────────────────┤
│ book::comparison::test_sum_formula │   0.002    │             3             │
└────────────────────────────────────┴────────────┴───────────────────────────┘
```

## 追蹤分析 (Trace Analysis)

若要進行更深入的分析，你可以從測試中產生執行追蹤記錄，並使用 [speedscope](https://www.speedscope.app/) 進行視覺化。這會顯示 gas 消耗的火焰圖，按函式呼叫細分，便於準確找出 gas 消耗位置。

### 步驟 1：產生追蹤記錄 (Step 1: Generate Traces)

使用 `--trace` 旗標執行測試以產生追蹤檔案：

```bash
sui move test --trace
```

追蹤檔案會寫入套件建置資料夾內的 `traces/` 目錄。

### 步驟 2：產生 Gas 分析報告 (Step 2: Generate a Gas Profile)

使用 `sui analyze-trace` 搭配 `gas-profile` 子命令將追蹤轉換為分析報告：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile
```

這會在目前目錄輸出 `gas_profile_<TRACE_FILE>.json` 檔案。你可以使用 `-o` 旗標指定不同的輸出目錄：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile -o ./profiles
```

### 步驟 3：使用 Speedscope 視覺化 (Step 3: Visualize with Speedscope)

安裝 [speedscope](https://www.speedscope.app/) 並開啟分析報告：

```bash
npm install -g speedscope
speedscope gas_profile_<TRACE_FILE>.json
```

Speedscope 提供三種檢視方式：

- **Time Order**：以呼叫順序從左到右顯示呼叫堆疊。條形寬度對應 gas 消耗。
- **Left Heavy**：將重複呼叫分組，按總 gas 消耗排序——適合尋找最昂貴的程式碼路徑。
- **Sandwich**：列出每個函式的 gas 消耗，包含**總計**（包含被呼叫函式）和**自身**（僅函式本身）欄位。

## 延伸閱讀 (Further Reading)

- [執行測試](./testing-basics.md) - 基本測試執行與預期的失敗
- [測試工具](./test-utilities.md) - 斷言巨集與測試輔助工具
- [集合](./../programmability/collections.md) - 選擇高效的資料結構
- [追蹤分析](https://docs.sui.io/references/cli/trace-analysis) - Sui CLI 追蹤分析參考
