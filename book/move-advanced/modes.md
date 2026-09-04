---
description: Move 中的編譯模式 (compilation modes)：在具名建置模式 (build modes)（例如偵錯 (debug)、基準測試 (benchmark) 或規格 (spec)）中納入不可發布的程式碼，超越內建的測試模式 (test mode)。
title: 模式 (Modes)
keywords:
  - Move
  - Sui
  - Move tutorial
  - modes
questions:
  - What is Modes in Move?
  - How do I use Modes in Move?
  - What is Building with modes in Move?
  - What is Publication in Move?
answer: 'Compilation modes in Move: include unpublishable code in named build modes like debug, benchmark, or spec beyond the built-in test mode.'
goal:
  description: 'Reader understands compilation modes in Move: include unpublishable code in named build modes like debug, benchmark, or spec beyond the built-in test mode'
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

# 模式 (Modes) {#modes}

模式可讓你只有在明確選擇具名建置 `mode` 時，才納入**不可發布**的程式碼。
你可以將其視為 `#[test_only]` [測試註解](../move-basics/testing)的泛化形式，適用於
你選擇的任何用途（例如 `debug`、`benchmark`、`spec` 或其他功能）。

模式概覽：

- 使用 `#[mode(name, ...)]` 註解項目，或針對內建的
  `test` 模式使用簡寫 `#[test_only]`。
  - `#[test_only]` 屬性是 `#[mode(test)]` 的語法糖。
- 使用 `--mode <name>` 建置（或在單元測試時使用 `--test`）。模式清單包含已啟用名稱的項目
  會被編譯進來。模式清單**不**相符的項目則會被編譯**排除**。
- 啟用任何模式後所編譯的程式碼都**不可發布**。這可確保偵錯／測試支援程式碼
  絕不會上鏈。
- 沒有 `#[mode(...)]`／`#[test_only]` 註解的項目一律會被納入。

> 提示：模式是由編譯期強制執行的篩選器，不會影響執行期的位元組碼。請將其用於
> 絕不應發布的輔助工具、模擬器，以及其他模擬型別與函式。

## 語法 (Syntax) {#syntax}

和 `#[test_only]` 一樣，你可以將模式屬性附加至模組與個別成員：

```move
// 僅在啟用相符模式時才納入整個模組
#[mode(debug)]
module my_pkg::debug_tools {
    public fun dump_state() { /* ... */ }
}

module my_pkg::library {
    // 此函式僅存在於 `debug` 或 `test` 建置中
    #[mode(debug, test)]
    public fun assert_invariants() { /* ... */ }

    // 僅供測試使用的輔助工具；等同於 #[mode(test)]
    #[test_only]
    fun mk_fake() { /* ... */ }
}
```

如同此處所見，可在單一屬性中列出多個模式：`#[mode(name1,name2,...)]`。
若所列名稱中**任一個**已啟用，該項目便會在編譯期間被納入。此外，
未使用模式註解的任何定義一律會被納入。

> 提示：`#[mode(test)]` 註解等同於 `#[test_only]`。

## 使用模式建置 (Building with modes) {#building-with-modes}

建置或測試時，請使用 Sui CLI 選擇啟用模式：

```bash
# 啟用自訂模式進行建置
sui move build --mode debug

# 執行測試；自動納入 #[test_only]
sui move test --test

# 組合：以額外的偵錯輔助工具執行單元測試
sui move test --test --mode debug
```

使用已啟用模式註解的項目會被編譯**納入**；使用不同且未啟用模式註解的項目
會被編譯**排除**。未加註解的項目一律會被編譯納入。

> **發布安全性**：在啟用模式時（包括 `--test`）產生的任何成品皆不可發布。在執行 `sui client publish` 前，務必執行不含 `--mode`／`--test` 的乾淨建置。

### 範例 - `test` 模式（單元測試） (Example - `test` mode (unit tests)) {#example---test-mode-unit-tests}

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

建置並執行：

```bash
# 納入標示為 #[test_only] 的模組與成員
sui move test --test
```

如同 [測試](../move-basics/testing)文件所述，這是讓測試輔助工具與僅供測試使用的公用函式
不會被納入已發布套件的絕佳方式。

### 範例 2：偵錯測試 (Example 2: Debug testing) {#example-2-debug-testing}

假設你有一個具備 `transfer` 函式的 `bank` 模組。你想在可查看內部狀態的測試
執行中加入偵錯記錄，但只想在開發期間以這些記錄執行該測試
（例如不在 CI 等環境中執行）。你可以為此使用 `debug` 模式。

```move
module my_pkg::bank {
    use std::error;

    public fun transfer(from: &signer, to: address, amount: u64) {
        // ... 正式環境邏輯 ...
    }
}

// 僅供偵錯使用的包裝函式與輔助工具
#[mode(debug)]
module my_pkg::bank_debug {
    use std::debug;
    use std::string::String;
    use my_pkg::bank;

    public fun transfer_debug(from: &signer, to: address, amount: u64) {
        // 在實際呼叫前執行偵錯輸出
        let begin: String = "[DEBUG] transfer begin";
        debug::print(&begin);
        debug::print(&amount);
        debug::print(&to);
        // 主要呼叫
        bank::transfer(from, to, amount);
        // 更多偵錯輸出
        let end: String = "[DEBUG] transfer end";
        debug::print(&end);
    }
}
```

此處的 `bank::transfer` 是**唯一**的正式環境入口點，且不會輸出內容。不過，
`#[mode(debug)]` 會公開 `bank_debug::{transfer_debug, dump_account, ...}`，而它們
**僅會**被納入 `debug` 模式建置。現在，我們可以撰寫使用此額外可見性的測試，
而不影響正式環境程式碼或其他測試：

```move
#[test_only]
module my_pkg::bank_tests {
    use my_pkg::bank;

    // 在所有建置中執行（不需要模式）
    #[test]
    fun transfer_basic() {
        // 建立 signers，呼叫 bank::transfer(...)
    }

    // 僅使用 `--test --mode debug` 時執行
    #[mode(debug)]
    #[test]
    fun transfer_with_logs() {
        use my_pkg::bank_debug; // 僅存在於偵錯建置中
        // 建立 signers，接著：
        bank_debug::transfer_debug(&signer, @bob, 100);
        // 斷言與一般測試相同；此外你可看到輸出
    }
}
```

現在，我們可透過啟用 `debug` 模式，以額外記錄執行此測試：

```bash
# 標準測試（不會編譯偵錯輔助工具）
sui move test

# 含額外記錄的偵錯測試
sui move test --mode debug
```

這讓我們能在不同時機產生正式環境位元組碼、持續整合測試與偵錯記錄測試，
而無須重複程式碼或進行複雜分支處理。

## 發布 (Publication) {#publication}

啟用任何模式所建置的程式碼皆不可發布。發布前，務必執行不含 `--mode` 或
`--test` 的乾淨建置：

```bash
sui move build   # 不含 --mode，不含 --test
```

## 另請參閱 (See also) {#see-also}

- Move Book 中的[測試基礎](../move-basics/testing)。
- Move Reference 中的[模式](/reference/modes)。
