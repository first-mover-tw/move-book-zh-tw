---
description:
  使用 Move Registry (MVR) 將外部相依套件 (external dependencies) 加入你的 Move 套件 (package)：搜尋套件、將它們加入清單
  (manifest)，並在程式碼中呼叫它們。
---

# 使用 Move Registry (Using Move Registry) {#using-move-registry}

發布在 Sui 上的每個套件都由其位址識別。位址雖然精確，但難以使用：它們不好記憶、在不同網路間有所差異，也無法透露套件的功能或發布者是誰。[Move Registry (MVR)](https://www.moveregistry.com) 透過將人類可讀的名稱（例如 `@potatoes/date`）對應到已發布套件的位址，解決了這個問題。有了 MVR，將外部依賴加入套件只需一道指令，而工具鏈會依據你所建置的網路，解析成對應的正確位址。

本指南將帶你走過使用外部套件的完整流程：在 registry 中尋找套件、將其加入 manifest、在程式碼中呼叫，以及測試結果。本指南假設你已安裝 MVR CLI——若尚未安裝，請參考[安裝 MVR (Install MVR)](./../before-we-begin/install-move-registry-cli) 章節。

## 套件名稱 (Package Names) {#package-names}

MVR 名稱遵循 `@organization/package-name` 的模式：organization 部分由 [SuiNS](https://suins.io) 名稱支援，而 package name 則由該 organization 的擁有者在其下註冊。一個名稱指向特定網路上已發布的套件，因此同一個名稱在 _mainnet_ 與 _testnet_ 上可能解析為不同位址。此外，由於 Sui 上的套件有版本控管，名稱也可以帶有版本後綴，例如 `@potatoes/date/1`；若未指定，該名稱則解析為最新版本。

本指南使用 [`@potatoes/date`](https://www.moveregistry.com/package/@potatoes/date) 套件——這是一個小型函式庫，能將時間戳記轉換為 `Date` 結構，並以 ISO 8601、UTC（RFC 7231）或自訂格式印出。

## 尋找套件 (Finding a Package) {#finding-a-package}

套件可以在 [MVR 網站](https://www.moveregistry.com)上找到，也可以直接在終端機中使用 `mvr search` 指令搜尋。查詢字串可以是套件名稱或描述的一部分，也可以是 `@organization/` 前綴，用來列出某個 organization 所發布的所有套件：

```bash
$ mvr search "@potatoes/"
```

```plaintext
- @potatoes/codec
# 適用於 Sui 的高效能編碼函式庫，功能包含 base64、base64url、urlencode、hex (base16)
Networks: mainnet, testnet

- @potatoes/date
# 日期與時間輸出／格式化工具，支援 RFC 7231 (UTC)、ISO-8601 及自訂
# 格式，並支援從字串建構日期
Networks: mainnet, testnet
```

`Networks` 這一行很重要：一個名稱只能在該套件已發布的網路上解析。若某個依賴只在 _mainnet_ 上可用，那麼針對 _testnet_ 的建置就會無法解析它。

## 加入依賴 (Adding a Dependency) {#adding-a-dependency}

若要將套件加入你的專案，請在含有套件 manifest 的目錄中執行 `mvr add` 指令：

```bash
$ mvr add @potatoes/date
```

此指令會在 `Move.toml` 的 `[dependencies]` 區段中插入一筆新記錄：

```toml
[dependencies]
date = { r.mvr = "@potatoes/date" }
```

與指向儲存庫與修訂版本的 git 依賴不同，這筆記錄只包含 registry 名稱。`r.` 前綴代表 _external resolver_（外部解析器）——這是一個在建置期間由 Sui CLI 呼叫的外掛，用來將名稱轉換為具體的套件位址與原始碼位置。`mvr` 這支執行檔就是該解析器，因此必須安裝並可在 `PATH` 中找到。

若要將依賴固定於特定版本，可在名稱後加上版本後綴：

```toml
[dependencies]
date = { r.mvr = "@potatoes/date/1" }
```

## 建置套件 (Building the Package) {#building-the-package}

依賴會在一般建置過程中被抓取並解析。在 `sui move build` 期間，CLI 會針對每筆 `r.mvr` 記錄呼叫 MVR 解析器，並使用目前作用中的環境來選定網路：

```plaintext
Output from mvr:
  │ [mvr] resolving: "@potatoes/date" on network: testnet

Output from mvr:
  │ [mvr] resolving: "@potatoes/ascii/1" on network: testnet

INCLUDING DEPENDENCY MoveStdlib
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY ascii
INCLUDING DEPENDENCY date
BUILDING postcard
```

請注意第二次解析器呼叫：`@potatoes/date` 本身依賴 `@potatoes/ascii`，而解析器會自動抓取它。過渡性的 MVR 依賴不需要在你的 manifest 中額外加入記錄。

解析結果會記錄在 `Move.lock` 檔案中，將每個依賴依網路固定於特定的原始碼修訂版本。此鎖定檔應加入版本控制，以確保你套件的每次建置都使用相同的依賴版本。

## 使用依賴 (Using the Dependency) {#using-the-dependency}

依賴加入後，其模組即可用一般的 `use` 陳述式匯入。路徑中的位址部分是該依賴自身宣告的具名位址——對 `@potatoes/date` 而言，該位址為 `date`，因此其中的 `date` 模組會以 `date::date` 的形式匯入。

以下範例定義了一個 `Postcard` 物件，它會儲存一個人類可讀的建立時間戳記，使用依賴中的 `Date` 型別以及 `Clock` 物件來取得目前時間：

```move
/// 模組：postcard
module postcard::postcard;

use date::date;
use std::string::String;
use sui::clock::Clock;

/// 一張會列印其建立日期與時間的明信片
public struct Postcard has key, store {
    id: UID,
    message: String,
    sent_at: String,
}

/// 使用訊息與人類可讀的時間戳記建立一個新的 `Postcard`
public fun new(message: String, clock: &Clock, ctx: &mut TxContext): Postcard {
    let date = date::from_clock(clock);

    Postcard {
        id: object::new(ctx),
        message,
        sent_at: date.to_utc_string(),
    }
}
```

`date::from_clock` 函式會從 `Clock` 物件讀取時間戳記（參見[紀元與時間 (Epoch and Time)](./../programmability/epoch-and-time)），並將其轉換為 `Date` 值，接著再印出為 UTC 字串。此套件也提供了 `to_iso_string` 用於 ISO 8601 輸出，以及 `format` 用於自訂格式：

```move
// 2025 年 1 月 1 日，UTC 12:30:00
let date = date::new(1735734600000);

assert!(date.to_utc_string() == "Wed, 01 Jan 2025 12:30:00 GMT");
assert!(date.to_iso_string() == "2025-01-01T12:30:00.000Z");
assert!(date.format("DD MMM YYYY, HH:mm") == "01 Jan 2025, 12:30");
```

## 測試 (Testing) {#testing}

外部依賴與其他程式碼一樣可以參與測試。以下測試建立了一個帶有已知時間戳記的 `Clock`，並檢查 `Postcard` 是否正確印出它：

```move
#[test]
fun test_postcard() {
    let ctx = &mut tx_context::dummy();
    let mut clock = sui::clock::create_for_testing(ctx);

    // 將時間設為 2025 年 1 月 1 日，UTC 12:30:00
    clock.set_for_testing(1735734600000);

    let postcard = new("Hello from Move!", &clock, ctx);

    assert!(postcard.sent_at == "Wed, 01 Jan 2025 12:30:00 GMT");

    transfer::public_transfer(postcard, ctx.sender());
    clock.destroy_for_testing();
}
```

執行 `sui move test` 會解析依賴、建置套件，並執行測試：

```plaintext
Running Move unit tests
[ PASS    ] postcard::postcard::test_postcard
Test result: OK. Total tests: 1; passed: 1; failed: 0
```

## 總結 (Summary) {#summary}

- Move Registry (MVR) 依網路將人類可讀的名稱（例如 `@potatoes/date`）對應到已發布套件的位址。
- `mvr search` 指令（或 [MVR 網站](https://www.moveregistry.com)）可協助尋找套件，並顯示它們發布於哪些網路上。
- `mvr add` 指令會在 `Move.toml` 中加入依賴記錄；名稱會在建置期間由 `mvr` 執行檔依據作用中的環境進行解析。
- 已解析的依賴會固定記錄於 `Move.lock` 檔案中，該檔應加入版本控制。
- 依賴的模組須使用該依賴自身宣告的具名位址來匯入。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Move Registry 文件](https://docs.suins.io/move-registry)——包含如何發布並註冊你自己的套件。
- 本書的[套件 Manifest (Package Manifest)](./../concepts/manifest) 章節。
