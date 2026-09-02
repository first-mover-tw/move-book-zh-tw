---
description: Move 中的編譯模式 (Compilation modes)：在內建的 test 模式之外，於 debug、benchmark 或 spec 等具名建置模式中包含不可發佈的程式碼。
---

# 模式 (Modes) {#modes}

模式（Modes）讓你只在明確選用某個具名的 build `mode` 時，才能包含**不可發布（unpublishable）**的程式碼。可以把它們想成是
[test annotation](../move-basics/testing) 中 `#[test_only]` 的通用化版本，適用於你所選擇的任何用途（例如
`debug`、`benchmark`、`spec`，或任何其他功能）。

模式一覽：

- 使用 `#[mode(name, ...)]` 為項目加上註解，或使用內建 `test` 模式的簡寫 `#[test_only]`。
  - `#[test_only]` 屬性是 `#[mode(test)]` 的語法糖。
- 使用 `--mode <name>` 建置（或使用 `--test` 進行單元測試）。凡是模式清單中包含你所啟用名稱的項目都會被編譯進去。凡是模式清單
  **不**符合的項目則會被編譯**排除**。
- 啟用任何模式所編譯出的程式碼都是**不可發布的**。這可以防止 debug／test 的鷹架程式碼上鏈。
- 沒有 `#[mode(...)]`／`#[test_only]` 註解的項目一律會被包含。

> 提示：模式是在編譯期強制執行的過濾器 —— 它們不會影響執行期的位元組碼（bytecode）。請將它們用於輔助函式、模擬器，以及其他絕不應該被發布的模擬型別與函式。

## 語法 (Syntax) {#syntax}

就像 `#[test_only]` 一樣，你可以將模式屬性附加到模組（module）以及個別成員上：

```move
// 只有在啟用對應 mode 時才會包含整個 module
#[mode(debug)]
module my_pkg::debug_tools {
    public fun dump_state() { /* ... */ }
}

module my_pkg::library {
    // 這個函式只存在於 `debug` 或 `test` build 中
    #[mode(debug, test)]
    public fun assert_invariants() { /* ... */ }

    // 僅供測試用的輔助工具；等同於 #[mode(test)]
    #[test_only]
    fun mk_fake() { /* ... */ }
}
```

如我們在此所見，單一屬性中可以列出多個模式：`#[mode(name1,name2,...)]`。只要所列出的名稱中**任一個**被啟用，這個項目就會在編譯期間被包含進去。此外，任何沒有模式註解的定義一律會被包含。

> 提示：註解 `#[mode(test)]` 等同於 `#[test_only]`。

## 以模式進行建置 (Building with modes) {#building-with-modes}

使用 Sui CLI 在建置或測試時選用某個模式：

```bash
# 用自訂 mode 啟用來 build
sui move build --mode debug

# 執行測試；會自動包含 #[test_only]
sui move test --test

# 組合：執行 unit 測試並加上額外的 debug 輔助工具
sui move test --test --mode debug
```

被你啟用之模式所註解的項目會被編譯**進去**；被其他未啟用模式所註解的項目則會被編譯**排除**。沒有註解的項目一律會被編譯進去。

> **發布安全性**：在啟用任何模式（包括 `--test`）的情況下所產出的任何產物都是不可發布的。請務必先執行不帶 `--mode`／`--test` 的乾淨建置，再執行 `sui client publish`。

### 範例：`test` 模式（單元測試）(Example - `test` mode (unit tests)) {#example---test-mode-unit-tests}

`#[test_only]` 是用於單元測試的內建模式。它的運作方式與名為 `test` 的模式完全相同。

```move
#[mode(test)]
module my_pkg::math_tests {
    use my_pkg::math;

    #[mode(test)]
    fun add_basic() { /* ... */ }

    // 私有測試輔助工具
    fun mk_case() { /* ... */ }
}
```

要進行建置與執行：

```bash
# 包含標記為 #[test_only] 的 module 與成員
sui move test --test
```

如同 [testing](../move-basics/testing) 文件中所述，這是將測試輔助函式與僅供測試用的公開函式排除在已發布套件之外的絕佳方式。

### 範例 2：Debug 測試 (Example 2: Debug testing) {#example-2-debug-testing}

假設你有一個帶有 `transfer` 函式的 `bank` 模組。你想在測試執行時加入 debug 記錄（logging），以便觀察內部狀態，但你只想在開發期間執行帶有這些記錄的測試（例如，不在 CI 等環境中執行）。你可以為此使用 `debug` 模式。

```move
module my_pkg::bank {
    use std::error;

    public fun transfer(from: &signer, to: address, amount: u64) {
        // ... 正式環境邏輯 ...
    }
}

// 僅供 debug 用的 wrapper 與輔助工具
#[mode(debug)]
module my_pkg::bank_debug {
    use std::debug;
    use std::string::String;
    use my_pkg::bank;

    public fun transfer_debug(from: &signer, to: address, amount: u64) {
        // 在真正呼叫前先執行 debug 列印
        let begin: String = "[DEBUG] transfer begin";
        debug::print(&begin);
        debug::print(&amount);
        debug::print(&to);
        // 主要呼叫
        bank::transfer(from, to, amount);
        // 更多 debug 列印
        let end: String = "[DEBUG] transfer end";
        debug::print(&end);
    }
}
```

在此，`bank::transfer` 是**唯一**的正式環境（production）進入點，沒有任何列印。而 `#[mode(debug)]` 則會公開
`bank_debug::{transfer_debug, dump_account, ...}`，然而這些內容**只會**被包含在 `debug` 模式的建置之中。現在，我們可以撰寫使用這種額外可見性的測試，而不會影響正式環境程式碼或其他測試：

```move
#[test_only]
module my_pkg::bank_tests {
    use my_pkg::bank;

    // 在所有 build 中都會執行（不需要 mode）
    #[test]
    fun transfer_basic() {
        // 建立 signer，呼叫 bank::transfer(...)
    }

    // 只有在 `--test --mode debug` 下才會執行
    #[mode(debug)]
    #[test]
    fun transfer_with_logs() {
        use my_pkg::bank_debug; // only exists in debug builds
        // 建立 signer，接著：
        bank_debug::transfer_debug(&signer, @bob, 100);
        // 斷言與一般測試相同；但你會看到列印
    }
}
```

現在我們可以透過啟用 `debug` 模式來執行這個附加額外記錄功能的測試：

```bash
# 標準測試（不會編譯進 debug 輔助工具）
sui move test

# 帶額外記錄的 debug 測試
sui move test --mode debug
```

這讓我們能夠在不同的時間點分別產出正式環境位元組碼、持續整合（continuous integration）測試，以及 debug 記錄測試，而不需要重複程式碼或複雜的分支處理。

## 發布 (Publication) {#publication}

啟用任何模式所建置的程式碼都是不可發布的。發布之前請務必先進行不帶 `--mode` 或 `--test` 的乾淨建置：

```bash
sui move build   # no --mode, no --test
```

## 延伸閱讀 (See also) {#see-also}

- Move Book 中的 [Testing basics](../move-basics/testing)。
- Move Reference 中的 [Modes](/reference/modes)。
