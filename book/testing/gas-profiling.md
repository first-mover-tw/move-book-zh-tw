---
description: "Sui Move 測試中的 Gas 分析：測量計算成本、比較實作，並使用 sui analyze-trace 分析追蹤紀錄。"
---

# Gas 分析 (Gas Profiling)

了解 Gas 消耗有助於優化你的 Move 程式碼並估算交易成本。Move 測試框架提供了內建工具來測量測試執行期間的 Gas 使用量。除此之外，還提供了一個特殊的工具 `sui analyze-trace` 用於更徹底地分析 Gas 使用量。

> `-s` 顯示的統計數據僅反映**計算單位 (computation units)** —— 它們不包括存儲成本。此外，編譯器計算單位並不直接對應於實際的鏈上 Gas 費用；它們顯示相對的計算複雜度，有助於比較不同實作。要獲得實際 Gas 成本，請將你的套件發布到測試網並測量真實交易。

## 簡單測量：測試統計

使用 `-s` 或 `--statistics` 標誌與 `sui move test` 一起使用，以查看每個測試的執行時間和 Gas 消耗：

```bash
sui move test -s
```

輸出顯示一個包含三列的表格：

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
- **Time**：執行時間 (秒)
- **Gas Used**：測試消耗的 Gas 單位

## CSV 輸出

為了進行程式化分析或匯入試算表，請使用 `csv` 選項：

```bash
sui move test -s csv
```

這會產生逗號分隔的輸出：

```
test_name,time_ns,gas_used
book::my_module::test_simple_operation,3381750,1
book::my_module::test_complex_operation,8454125,59
book::my_module::test_with_objects,3905625,25
```

時間以奈秒 (nanoseconds) 為單位，這允許在比較相似操作時進行更精確的測量。

## Gas 限制

使用 `-i` 或 `--gas-limit` 標誌來設定測試的最大 Gas 預算。超過此限制的測試將會超時：

```bash
sui move test -i 50
```

當測試超過 Gas 限制時的輸出：

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

這對於以下情況很有用：

- **識別昂貴的操作**：找出消耗意外 Gas 量的測試
- **強制執行 Gas 預算**：確保關鍵路徑保持在可接受的限制內
- **測試 Gas 耗盡**：驗證你的程式碼是否正確處理 Gas 耗盡的情況 (參見 [預期失敗](./testing-basics.md#expected-failures))

## 比較實作

使用統計數據來比較不同實作之間的 Gas 消耗：

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

使用統計數據執行揭示了差異：

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

為了更深入的剖析，你可以從測試中生成執行追蹤，並使用 [speedscope](https://www.speedscope.app/) 將其視覺化。這會顯示按函式調用細分的 Gas 消耗火焰圖 (flamegraph)，使你可以輕鬆找出 Gas 實際花費在哪裡。

### 步驟 1：生成追蹤

使用 `--trace` 標誌執行測試以產生追蹤檔案：

```bash
sui move test --trace
```

追蹤檔案會寫入套件構建資料夾內的 `traces/` 目錄中。

### 步驟 2：生成 Gas 設定檔 (Gas Profile)

使用 `sui analyze-trace` 和 `gas-profile` 子命令將追蹤轉換為設定檔：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile
```

這會在當前目錄中輸出一個 `gas_profile_<TRACE_FILE>.json` 檔案。你可以使用 `-o` 標誌指定不同的輸出目錄：

```bash
sui analyze-trace -p traces/<TRACE_FILE> gas-profile -o ./profiles
```

### 步驟 3：使用 Speedscope 視覺化

安裝 [speedscope](https://www.speedscope.app/) 並打開設定檔：

```bash
npm install -g speedscope
speedscope gas_profile_<TRACE_FILE>.json
```

Speedscope 提供三種視圖：

- **Time Order (時間順序)**：按調用順序從左到右顯示調用堆疊。條形寬度對應於 Gas 消耗。
- **Left Heavy (左側加重)**：將重複的調用分組在一起，按總 Gas 消耗排序 —— 對於查找最昂貴的程式碼路徑很有用。
- **Sandwich (三明治)**：列出每個函式的 Gas 消耗，包含 **Total** (包括被調用的函式) 和 **Self** (僅函式本身) 列。

## 延伸閱讀

- [執行測試](./testing-basics.md) - 基本測試執行和預期失敗
- [測試工具](./test-utilities.md) - 斷言巨集和測試輔助工具
- [集合 (Collections)](./../programmability/collections.md) - 選擇高效的資料結構
- [追蹤分析](https://docs.sui.io/references/cli/trace-analysis) - Sui CLI 追蹤分析參考
