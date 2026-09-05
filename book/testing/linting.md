---
description: 使用 `sui move lint` 執行 Move (Move) 靜態分析工具：在編譯時期捕捉 Sui 特有的反模式、抑制誤報，並在持續整合 (CI) 中強制套用靜態分析規則。
title: 執行 Lint 檢查 (Running Lints)
keywords:
  - Move
  - Sui
  - Move tutorial
  - running
  - lints
questions:
  - What is Running Lints in Move?
  - How do I use Running Lints in Move?
  - What is Default and Extra Lints in Move?
answer: 'Run Move linters with sui move lint: catch Sui-specific antipatterns at compile time, suppress false positives, and enforce lints in CI.'
goal:
  description: 'Reader understands run Move linters with sui move lint: catch Sui-specific antipatterns at compile time, suppress false positives, and enforce lints in CI'
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

# 執行 Lint 檢查 (Running Lints) {#running-lints}

Move 編譯器隨附一組 _lint 檢查_——會在編譯時標記原始碼中可疑模式的靜態檢查。測試會驗證原始碼是否如預期運作；lint 檢查則會找出能夠編譯、甚至可能通過測試，但資深 Move 開發者不會這樣撰寫的原始碼：破壞可組合性的轉移、結果永遠與表面意義不同的比較，或永遠無法呼叫的 `entry` 函式。定期執行 lint 檢查，並讓套件不含警告，是維持原始碼品質的低成本方式。

## 執行 Lint 檢查 (Running Lints) {#running-lints-1}

`sui move lint` 指令會編譯套件，並執行完整的 linter 集合：

```bash
sui move lint
```

若也要檢查 `tests` 目錄中的原始碼，請加入 `--test` 旗標：

```bash
sui move lint --test
```

相同檢查也能透過其他指令的 `--lint` 旗標使用——例如，`sui move test --lint` 會一次執行測試與完整 lint 集合。

假設某個模組有一個函式，會將新建立的物件轉移給交易傳送者：

```move
module book::mint;

public struct Item has key, store { id: UID }

public fun mint(ctx: &mut TxContext) {
    let item = Item { id: object::new(ctx) };
    transfer::transfer(item, ctx.sender());
}
```

執行 linter 會印出警告，其中包含說明及指向確切運算式的指標：

```
warning[Lint W99001]: non-composable transfer to sender
  ┌─ ./sources/mint.move:7:5
  │
5 │ public fun mint(ctx: &mut TxContext) {
  │            ---- 從函式回傳物件可讓呼叫端使用該物件，並透過可程式化交易啟用可組合性。
6 │     let item = Item { id: object::new(ctx) };
7 │     transfer::transfer(item, ctx.sender());
  │     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  │     │                        │
  │     │                        交易傳送者地址來自此處
  │     將物件轉移至交易傳送者地址
  │
  = 可將 '#[allow(lint(self_transfer))]' 套用至 'module' 或模組成員（'const'、'fun' 或 'struct'）以抑制此警告
```

此特定 lint 檢查建議的修正方式，是從函式回傳 `Item`，而非轉移它，並讓呼叫端決定如何處理該物件。

## 預設與額外 Lint 檢查 (Default and Extra Lints) {#default-and-extra-lints}

Lint 檢查分為兩個層級。*預設*層級包含最重要的 Sui 專用檢查，且會在每次編譯時執行——單純的 `sui move build` 或 `sui move test` 也會回報這些警告。*額外*層級會加入另外兩項 Sui 檢查及一組原始碼風格 lint 檢查；僅在明確要求執行 lint 檢查時執行，例如使用 `sui move lint` 或 `--lint` 旗標。

## 抑制 Lint 檢查 (Suppressing Lints) {#suppressing-lints}

Lint 檢查是啟發式檢查，有時被標記的原始碼是刻意如此。可使用 `#[allow(lint(<name>))]` 屬性抑制 lint 檢查；請將它套用至模組或模組成員，並使用警告中印出的 lint 名稱：

```move
public struct Account has key { id: UID }

/// 帳戶物件，刻意為傳送者建立並由其擁有。
#[allow(lint(self_transfer))]
public fun new_account(ctx: &mut TxContext) {
    transfer::transfer(
        Account { id: object::new(ctx) },
        ctx.sender(),
    );
}
```

單一屬性可抑制多個 lint 檢查：`#[allow(lint(share_owned, self_transfer))]`。請將抑制視為其他例外情況——保持範圍精確（優先套用至函式，而非整個模組），並在註解或文件註解中說明原因。

## CI 中的 Lint 檢查 (Lints in CI) {#lints-in-ci}

若要強制維持不含警告的原始碼庫，請加入 `--warnings-are-errors` 旗標——此時只要出現任何警告（包括 lint 檢查），指令便會以非零結束代碼失敗：

```bash
sui move lint --test --warnings-are-errors
```

對於以程式方式取用輸出的工具，`--json-errors` 會將診斷資訊切換為 JSON 格式。

## Lint 檢查參考 (Lint Reference) {#lint-reference}

Linter 會將檢查分成兩組：每次編譯都會執行的 _預設_ lint 檢查，以及僅在使用 `--lint` 旗標時執行的 _額外_ lint 檢查。

### 預設 Lint 檢查 (Default Lints) {#default-lints}

這些檢查會在每次編譯時執行：

| Lint 檢查             | 代碼   | 標記項目                                                                                                            |
| --------------------- | ------ | ------------------------------------------------------------------------------------------------------------------- |
| `share_owned`         | W99000 | 分享先前可能已被擁有的物件；請在建立物件的交易中分享它                                                              |
| `self_transfer`       | W99001 | 將新物件轉移給傳送者，而非回傳它；會損害可組合性                                                                    |
| `custom_state_change` | W99002 | 對具有 `store` 的型別套用自訂轉移／分享／凍結策略；`public_*` [儲存函式](./../storage/storage-functions) 可繞過它   |
| `coin_field`          | W99003 | 型別為 `Coin<T>` 的 struct 欄位；[`Balance<T>`](./../programmability/balance-and-coin) 成本更低，通常也是正確的選擇 |
| `freeze_wrapped`      | W99004 | 凍結包裝其他物件的物件                                                                                              |
| `collection_equality` | W99005 | 使用 `==` 比較[動態集合](./../programmability/dynamic-collections)；只會比較 `id` 與 `size`，絕不比較內容           |
| `public_random`       | W99006 | 接受 [`Random`](./../programmability/randomness) 的 `public` 函式；會使隨機性暴露於組合攻擊                         |
| `missing_key`         | W99007 | 具有 `id: UID` 欄位但沒有 `key` ability 的 struct                                                                   |
| `public_entry`        | W99010 | `public` 函式上不必要的 [`entry`](./../move-advanced/entry-functions) 修飾詞                                        |
| `uncallable_function` | W99011 | 永遠無法在交易中呼叫的函式，例如接受 `&mut Clock` 的 `entry` 函式                                                   |

### 額外 Lint 檢查 (Extra Lints) {#extra-lints}

由 `sui move lint` 或 `--lint` 旗標啟用：

| Lint 檢查               | 代碼   | 標記項目                                                                                    |
| ----------------------- | ------ | ------------------------------------------------------------------------------------------- |
| `freezing_capability`   | W99008 | 凍結看似[能力](./../programmability/capability)的型別                                       |
| `prefer_mut_tx_context` | W99009 | 接受 `&TxContext` 的 `public` 函式；請優先使用 `&mut TxContext`，以讓函式簽名能因應未來變更 |

額外層級也包含原始碼風格 lint 檢查（代碼為 `W04xxx`）：`constant_naming`、`while_true`、`unnecessary_math`、`unneeded_return`、`abort_without_constant`、`loop_without_exit`、`unnecessary_conditional`、`self_assignment`、`redundant_ref_deref`、`unnecessary_unit`、`always_equal_operands` 與 `combinable_comparisons`。每項檢查都會標記一個小型的可讀性或正確性問題，並建議較簡單的等效寫法。

## 總結 (Summary) {#summary}

| 指令                                  | 說明                                      |
| ------------------------------------- | ----------------------------------------- |
| `sui move lint`                       | 編譯套件並執行完整 lint 集合              |
| `sui move lint --test`                | 也對 `tests` 目錄中的原始碼執行 lint 檢查 |
| `sui move lint --warnings-are-errors` | 任一警告即失敗——適用於 CI                 |
| `sui move build` / `sui move test`    | 執行預設 lint 層級                        |
| `sui move test --lint`                | 使用完整 lint 集合執行測試                |
| `--no-lint`                           | 完全停用 linter                           |

## 延伸閱讀 (Further Reading) {#further-reading}

- [原始碼品質檢查清單](./../guides/code-quality-checklist)——更廣泛的審查檢查清單，lint 檢查會將其中一部分自動化。
- Sui 文件中的 [Move CLI 參考](https://docs.sui.io/references/cli/move)。
