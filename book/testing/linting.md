---
description:
  使用 sui move lint 執行 Move 程式碼檢查工具（linter）：在編譯時期抓出 Sui 特有的反模式（antipattern），抑制誤判，並在
  CI 中強制執行 lint 規則。
---

# 執行檢查程式碼風格 (Running Lints) {#running-lints}

Move 編譯器隨附一組 _lints_（靜態程式碼檢查工具），會在編譯時標記程式碼中可疑的模式。測試驗證程式碼是否做了它該做的事；lints 則抓出那些能通過編譯、甚至能通過測試，但卻不是經驗豐富的 Move 開發者會寫出來的程式碼：破壞可組合性的轉移（transfer）、看起來像做了某件事但實際上永遠不會如此運作的比較、或永遠無法被呼叫的 `entry` 函式。定期執行 lints——並讓套件保持沒有警告的狀態——是維持程式碼品質的低成本做法。

## 執行檢查程式碼風格 (Running Lints) {#running-lints-1}

`sui move lint` 指令會編譯套件並執行完整的 linter 集合：

```bash
sui move lint
```

若要同時檢查 `tests` 目錄中的程式碼，加上 `--test` 旗標：

```bash
sui move lint --test
```

其他指令也可透過 `--lint` 旗標使用相同的檢查——例如，`sui move test --lint` 會一次執行測試以及完整的 lint 集合。

考慮一個模組，其中有個函式會將剛建立的物件轉移給交易發送者：

```move
module book::mint;

public struct Item has key, store { id: UID }

public fun mint(ctx: &mut TxContext) {
    let item = Item { id: object::new(ctx) };
    transfer::transfer(item, ctx.sender());
}
```

執行 linter 會印出一則警告，附帶說明及指向確切運算式的指標：

```
warning[Lint W99001]: non-composable transfer to sender
  ┌─ ./sources/mint.move:7:5
  │
5 │ public fun mint(ctx: &mut TxContext) {
  │            ---- Returning an object from a function, allows a caller to use the object and enables composability via programmable transactions.
6 │     let item = Item { id: object::new(ctx) };
7 │     transfer::transfer(item, ctx.sender());
  │     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  │     │                        │
  │     │                        Transaction sender address coming from here
  │     Transfer of an object to transaction sender address
  │
  = This warning can be suppressed with '#[allow(lint(self_transfer))]' applied to the 'module' or module member ('const', 'fun', or 'struct')
```

這個 lint 建議的修正方式是從函式中回傳 `Item`，而不是直接轉移它，讓呼叫端自行決定該如何處理該物件。

## 預設與額外檢查 (Default and Extra Lints) {#default-and-extra-lints}

Lints 分成兩個層級。_default_（預設）層級包含最重要的 Sui 專屬檢查，會在每次編譯時執行——一般的 `sui move build` 或 `sui move test` 也會回報這些警告。_extra_（額外）層級則新增了兩項 Sui 檢查以及一組程式碼風格 lints；當明確要求執行檢查時——透過 `sui move lint` 或 `--lint` 旗標——才會執行。

## 抑制檢查 (Suppressing Lints) {#suppressing-lints}

Lints 是啟發式的（heuristic），有時被標記的程式碼是刻意寫成那樣的。可以用 `#[allow(lint(<name>))]` 屬性來抑制某個 lint，套用在模組或模組成員上，使用警告中印出的 lint 名稱：

```move
public struct Account has key { id: UID }

/// 一個帳戶物件，刻意為 sender 建立並由其擁有。
#[allow(lint(self_transfer))]
public fun new_account(ctx: &mut TxContext) {
    transfer::transfer(
        Account { id: object::new(ctx) },
        ctx.sender(),
    );
}
```

單一屬性可以抑制多個 lints：`#[allow(lint(share_owned, self_transfer))]`。把抑制當成其他例外狀況一樣處理——盡量縮小範圍（優先選函式而非整個模組），並在註解或文件註解中說明原因。

## CI 中的檢查程式碼風格 (Lints in CI) {#lints-in-ci}

若要強制執行無警告的程式碼庫，加上 `--warnings-are-errors` 旗標——這樣一來，只要有任何警告（包括 lints），指令就會以非零結束碼失敗：

```bash
sui move lint --test --warnings-are-errors
```

若工具需要以程式化方式解析輸出，`--json-errors` 可將診斷訊息切換為 JSON 格式。

## 檢查程式碼風格參考 (Lint Reference) {#lint-reference}

Linter 將其檢查項目分為兩組：每次編譯都會執行的 _default_ lints，以及只在 `--lint` 旗標下才會執行的 _extra_ lints。

### 預設檢查 (Default Lints) {#default-lints}

這些會在每次編譯時執行：

| Lint                  | 代碼   | 標記內容                                                                                                              |
| --------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| `share_owned`         | W99000 | 分享一個可能先前已被擁有的物件；應在建立物件的同一筆交易中分享物件                                                    |
| `self_transfer`       | W99001 | 將新物件轉移給發送者，而非直接回傳它；會損害可組合性                                                                  |
| `custom_state_change` | W99002 | 在具有 `store` 能力的型別上自訂轉移／分享／凍結策略；`public_*` [儲存函式](./../storage/storage-functions) 可以繞過它 |
| `coin_field`          | W99003 | 型別為 `Coin<T>` 的 struct 欄位；[`Balance<T>`](./../programmability/balance-and-coin) 成本較低，通常是更好的選擇     |
| `freeze_wrapped`      | W99004 | 凍結一個包裹著其他物件的物件                                                                                          |
| `collection_equality` | W99005 | 使用 `==` 比較[動態集合](./../programmability/dynamic-collections)；只會比較 `id` 與 `size`，不會比較內容             |
| `public_random`       | W99006 | 接受 [`Random`](./../programmability/randomness) 的 `public` 函式；會將隨機性暴露給組合攻擊                           |
| `missing_key`         | W99007 | 具有 `id: UID` 欄位但缺少 `key` 能力的 struct                                                                         |
| `public_entry`        | W99010 | `public` 函式上不必要的 [`entry`](./../move-advanced/entry-functions) 修飾詞                                          |
| `uncallable_function` | W99011 | 永遠無法在交易中被呼叫的函式，例如接受 `&mut Clock` 的 `entry` 函式                                                   |

### 額外檢查 (Extra Lints) {#extra-lints}

由 `sui move lint` 或 `--lint` 旗標啟用：

| Lint                    | 代碼   | 標記內容                                                                                |
| ----------------------- | ------ | --------------------------------------------------------------------------------------- |
| `freezing_capability`   | W99008 | 凍結一個看起來像[能力（capability）](./../programmability/capability)的型別             |
| `prefer_mut_tx_context` | W99009 | 接受 `&TxContext` 的 `public` 函式；建議改用 `&mut TxContext`，以保持簽章面向未來的彈性 |

extra 層級還包含程式碼風格 lints（代碼 `W04xxx`）：`constant_naming`、`while_true`、`unnecessary_math`、`unneeded_return`、`abort_without_constant`、`loop_without_exit`、`unnecessary_conditional`、`self_assignment`、`redundant_ref_deref`、`unnecessary_unit`、`always_equal_operands`，以及 `combinable_comparisons`。每一項都會標記一個小的可讀性或正確性問題，並提出更簡潔的等價寫法。

## 總結 (Summary) {#summary}

| 指令                                  | 說明                            |
| ------------------------------------- | ------------------------------- |
| `sui move lint`                       | 編譯套件並執行完整的 lint 集合  |
| `sui move lint --test`                | 同時檢查 `tests` 目錄中的程式碼 |
| `sui move lint --warnings-are-errors` | 任何警告都會導致失敗——適用於 CI |
| `sui move build` / `sui move test`    | 執行 default lint 層級          |
| `sui move test --lint`                | 以完整的 lint 集合執行測試      |
| `--no-lint`                           | 完全停用 linters                |

## 延伸閱讀 (Further Reading) {#further-reading}

- [程式碼品質檢查清單](./../guides/code-quality-checklist) —— 更全面的審查清單，lints 只是其自動化的其中一部分。
- Sui 文件中的 [Move CLI 參考](https://docs.sui.io/references/cli/move)。
