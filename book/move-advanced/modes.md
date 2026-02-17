---

description: "Compilation modes in Move: include unpublishable code in named build modes like debug, benchmark, or spec beyond the built-in test mode."
---

# 模式 (Modes)

模式 (Modes) 允許您僅在明確選擇加入具名構建「模式」時，才包含 **不可發佈** 的程式碼。您可以將其視為用於任何目的（例如 `debug`、`benchmark`、`spec` 或任何其他功能）的 `#[test_only]` [測試註解](../move-basics/testing) 的泛化。

模式概覽：

* 使用 `#[mode(name, ...)]` 標記項目，或針對內建的 `test` 模式使用縮寫 `#[test_only]`。
  * `#[test_only]` 屬性是 `#[mode(test)]` 的語法糖。
* 使用 `--mode <name>`（或針對單元測試使用 `--test`）進行構建。模式清單中包含您所啟用名稱之項目會被編譯 **進來**。模式清單中 **不匹配** 的項目則會被編譯 **掉**。
* 啟用任何模式後編譯的程式碼都是 **不可發佈** 的。這可以防止偵錯/測試腳手架進入鏈上。
* **沒有** `#[mode(...)]`/`#[test_only]` 標記的項目始終會被包含。

> 提示：模式是在編譯時期強制執行的過濾器 — 它們不會影響執行時期的位元組碼。將其用於輔助工具、模擬器以及其他永遠不應發佈的模擬 (mock) 類型和函式。

## 語法

就像 `#[test_only]` 一樣，您可以將模式屬性附加到模組和單個成員上：

```move
// 僅當啟用匹配模式時才包含整個模組
#[mode(debug)]
module my_pkg::debug_tools {
    public fun dump_state() { /* ... */ }
}

module my_pkg::library {
    // 此函式僅存在於 `debug` 或 `test` 構建中
    #[mode(debug, test)]
    public fun assert_invariants() { /* ... */ }

    // 僅限測試的輔助工具；等同於 #[mode(test)]
    #[test_only]
    fun mk_fake() { /* ... */ }
}
```

正如我們在這裡看到的，單個屬性中可以列出多個模式：`#[mode(name1,name2,...)]`。如果列出的名稱中有 **任何一個** 被啟用，該項目就會在編譯期間被包含。此外，任何不具備模式標記的定義始終會被包含。

> 提示：註解 `#[mode(test)]` 等同於 `#[test_only]`。

## 使用模式進行構建

在構建或測試時，使用 Sui CLI 來選擇加入特定模式：

```bash
# 在啟用自定義模式的情況下進行構建
sui move build --mode debug

# 執行測試；自動包含 #[test_only]
sui move test --test

# 結合使用：執行單元測試並帶有額外的偵錯輔助工具
sui move test --test --mode debug
```

標記有您所啟用模式的項目會被編譯 **進來**；標記有其他未啟用模式的項目則會被編譯 **掉**。未標記的項目始終會被編譯進來。

> **發佈安全性**：在啟用任何模式（包括 `--test`）期間產生的任何產物都是不可發佈的。在執行 `sui client publish` 之前，請務必運作一次 **不帶** `--mode`/`--test` 的乾淨構建。

### 範例 1 — `test` 模式 (單元測試)

`#[test_only]` 是用於單元測試的內建模式。它的運作方式與名為 `test` 的模式完全相同。

```move
#[mode(test)]
module my_pkg::math_tests {
    use my_pkg::math;

    #[modetest]
    fun add_basic() { /* ... */ }

    // 私有測試輔助工具
    fun mk_case() { /* ... */ }
}
```

構建與執行：

```bash
# 包含標記為 #[test_only] 的模組和成員
sui move test --test
```

正如 [測試](../move-basics/testing) 檔案中所述，這是將測試輔助工具和僅限測試的公開函式排除在已發佈套件之外的好方法。

### 範例 2: 偵錯測試 (Debug testing)

假設您有一個包含 `transfer` 函式的 `bank` 模組。您想在測試運作中添加偵錯紀錄，以便查看內部狀態，但您只希望在開發期間執行帶有這些紀錄的測試（例如，不在 CI 期間執行等）。您可以為此使用 `debug` 模式。

```move
module my_pkg::bank {
    use std::error;

    public fun transfer(from: &signer, to: address, amount: u64) {
        // ... 生產環境邏輯 ...
    }
}

// 僅限偵錯的封裝器與輔助工具
#[mode(debug)]
module my_pkg::bank_debug {
    use std::debug;
    use my_pkg::bank;

    public fun transfer_debug(from: &signer, to: address, amount: u64) {
        // 在實際呼叫前執行偵錯列印
        debug::print(&b"[DEBUG] transfer begin".to_vector());
        debug::print(&amount);
        debug::print(&to);
        // 主要呼叫
        bank::transfer(from, to, amount);
        // 更多偵錯列印
        debug::print(&b"[DEBUG] transfer end".to_vector());
    }
}
```

這裡，`bank::transfer` 是 **唯一的** 生產環境入口點，不帶有任何列印。然而，`#[mode(debug)]` 公開了 `bank_debug::{transfer_debug, dump_account, ...}`，它們 **僅** 會被包含在 `debug` 模式的構建中。現在，我們可以編寫使用此額外可見性的測試，而不影響生產環境程式碼或其他測試：

```move
#[test_only]
module my_pkg::bank_tests {
    use my_pkg::bank;

    // 在所有構建中執行（不需要模式）
    #[test]
    fun transfer_basic() {
        // 建立 signer，呼叫 bank::transfer(...)
    }

    // 僅在使用 `--test --mode debug` 時執行
    #[mode(debug)]
    #[test]
    fun transfer_with_logs() {
        use my_pkg::bank_debug; // 僅存在於 debug 構建中
        // 建立 signer，然後：
        bank_debug::transfer_debug(&signer, @bob, 100);
        // 斷言與正常測試相同；此外還能看到列印內容
    }
}
```

現在，藉由啟用 `debug` 模式，我們可以執行帶有額外紀錄的測驗：

```bash
# 標準測試（未編譯進偵錯輔助工具）
sui move test

# 帶有額外紀錄的偵錯測試
sui move test --mode debug
```

這使我們能夠在不同時間產生生產環境位元組碼、持續整合測試和偵錯紀錄測試，而無需重複程式碼或複雜的分支。

## 發佈

啟用任何模式構建的程式碼均為不可發佈。在發佈之前，請務必運作一次不帶 `--mode` 或 `--test` 的乾淨構建：

```bash
sui move build   # 不帶 --mode, 不帶 --test
```

## 參見 (See also)

* Move Book 中的 [測試基礎 (Testing basics)](../move-basics/testing)。
* Move 參考手冊中的 [模式 (Modes)](/reference/modes)。
