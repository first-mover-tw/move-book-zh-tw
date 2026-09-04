---
description: 使用 Move 登錄表 (Move Registry, MVR) 將外部依賴項新增至你的 Move 套件：搜尋套件、將其新增至套件清單，並在你的原始碼中呼叫它們。
title: 使用 Move 登錄 (Move Registry)
keywords:
  - Move
  - Sui
  - Move tutorial
  - using
  - move
  - registry
questions:
  - What is Using Move Registry in Move?
  - How do I use Using Move Registry in Move?
  - What is Package Names in Move?
  - What is Finding a Package in Move?
answer: 'Use Move Registry (MVR) to add external dependencies to your Move package: search for packages, add them to the manifest, and call them in your code.'
goal:
  description: 'Reader can use Move Registry (MVR) to add external dependencies to your Move package: search for packages, add them to the manifest, and call them in your code'
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

# 使用 Move Registry (Using Move Registry) {#using-move-registry}

發佈在 Sui 上的每個套件都由其地址識別。地址雖然精確，但難以使用：不易記憶、會因網路而異，且無法說明套件的用途或發佈者。[Move Registry (MVR)](https://www.moveregistry.com) 透過將人類可讀的名稱（例如 `@potatoes/date`）對應至已發佈的套件地址來解決此問題。使用 MVR，將外部依賴項加入你的套件只需一個指令，而工具鏈會將名稱解析為你目前建置目標網路所對應的正確地址。

本指南將說明使用外部套件的完整流程：在註冊表中尋找套件、將其加入套件清單、在程式碼中呼叫，以及測試結果。本指南假設你已安裝 MVR CLI；如果尚未安裝，請參考 [安裝 MVR (Install MVR)](./../before-we-begin/install-move-registry-cli) 章節。

## 套件名稱 (Package Names) {#package-names}

MVR 名稱遵循 `@organization/package-name` 模式：organization 部分由 [SuiNS](https://suins.io) 名稱支援，而套件名稱則由組織擁有者在其底下註冊。一個名稱會指向特定網路上已發佈的套件，因此同一個名稱在 _mainnet_ 與 _testnet_ 上可能解析為不同地址。此外，由於 Sui 上的套件具有版本，名稱也可以帶有版本後綴，例如 `@potatoes/date/1`；未加後綴時，名稱會解析為最新版本。

本指南使用 [`@potatoes/date`](https://www.moveregistry.com/package/@potatoes/date) 套件，這是一個小型程式庫，可將時間戳記轉換為 `Date` 結構，並以 ISO 8601、UTC (RFC 7231) 或自訂格式輸出。

## 尋找套件 (Finding a Package) {#finding-a-package}

你可以在 [MVR 網站](https://www.moveregistry.com) 上探索套件，或直接在終端機中使用 `mvr search` 指令。查詢可以是套件名稱或描述的一部分，或使用 `@organization/` 前綴列出特定組織發佈的所有內容：

```bash
$ mvr search "@potatoes/"
```

```plaintext
- @potatoes/codec
# 適用於 Sui 的高效能編碼程式庫，功能包括：base64、base64url、urlencode、hex (base16)
網路：mainnet、testnet

- @potatoes/date
# 日期與時間輸出／格式化工具，支援 RFC 7231 (UTC)、ISO-8601 與自訂
# 格式，以及從字串建立日期
網路：mainnet、testnet
```

`Networks` 行相當重要：名稱只能在套件已發佈的網路上解析。若依賴項只在 _mainnet_ 上可用，針對 _testnet_ 的建置將無法解析它。

## 新增依賴項 (Adding a Dependency) {#adding-a-dependency}

若要將套件加入專案，請在包含套件清單的目錄中執行 `mvr add` 指令：

```bash
$ mvr add @potatoes/date
```

此指令會在 `Move.toml` 的 `[dependencies]` 區段插入一筆新記錄：

```toml
[dependencies]
date = { r.mvr = "@potatoes/date" }
```

不同於指向儲存庫與修訂版本的 git 依賴項，這筆記錄只包含註冊表名稱。`r.` 前綴代表 _external resolver_，也就是 Sui CLI 在建置期間呼叫的外掛程式，用來將名稱轉換為具體的套件地址與原始碼位置。`mvr` 二進位檔就是該解析器，因此必須安裝並可透過 `PATH` 使用。

若要將依賴項固定至特定版本，請將版本後綴加入名稱：

```toml
[dependencies]
date = { r.mvr = "@potatoes/date/1" }
```

## 建置套件 (Building the Package) {#building-the-package}

依賴項會在一般建置流程中擷取並解析。執行 `sui move build` 時，CLI 會針對每筆 `r.mvr` 記錄呼叫 MVR 解析器，並使用目前作用中的環境來選擇網路：

```plaintext
mvr 的輸出：
  │ [mvr] 正在解析：testnet 網路上的 "@potatoes/date"

mvr 的輸出：
  │ [mvr] 正在解析：testnet 網路上的 "@potatoes/ascii/1"

包含依賴項 MoveStdlib
包含依賴項 Sui
包含依賴項 ascii
包含依賴項 date
正在建置 postcard
```

請注意第二次解析器呼叫：`@potatoes/date` 本身依賴 `@potatoes/ascii`，解析器會自動擷取它。傳遞性 MVR 依賴項不需要在你的套件清單中加入額外記錄。

解析結果會記錄在 `Move.lock` 文件中，將每個依賴項固定至每個網路上的確切原始碼修訂版本。應將鎖定文件提交至版本控制，讓套件的每次建置都使用相同依賴項版本。

## 使用依賴項 (Using the Dependency) {#using-the-dependency}

新增依賴項後，可以使用一般的 `use` 陳述式匯入其模組。路徑中的地址部分，是依賴項本身所宣告的具名地址；對於 `@potatoes/date` 而言，此地址為 `date`，因此其中的 `date` 模組會以 `date::date` 匯入。

以下範例定義一個 `Postcard` 物件，使用依賴項中的 `Date` 型別與 `Clock` 物件取得目前時間，並儲存建立時的人類可讀時間戳記：

```move
/// 模組：postcard
module postcard::postcard;

use date::date;
use std::string::String;
use sui::clock::Clock;

/// 一張會輸出其建立日期與時間的明信片。
public struct Postcard has key, store {
    id: UID,
    message: String,
    sent_at: String,
}

/// 建立一張帶有訊息與人類可讀時間戳記的新 `Postcard`。
public fun new(message: String, clock: &Clock, ctx: &mut TxContext): Postcard {
    let date = date::from_clock(clock);

    Postcard {
        id: object::new(ctx),
        message,
        sent_at: date.to_utc_string(),
    }
}
```

`date::from_clock` 函式會從 `Clock` 物件讀取時間戳記（請參閱[紀元與時間 (Epoch and Time)](./../programmability/epoch-and-time)），並將其轉換為 `Date` 值，接著輸出為 UTC 字串。此套件也提供用於 ISO 8601 輸出的 `to_iso_string`，以及用於自訂格式的 `format`：

```move
// 2025 年 1 月 1 日，12:30:00 UTC
let date = date::new(1735734600000);

assert!(date.to_utc_string() == "Wed, 01 Jan 2025 12:30:00 GMT");
assert!(date.to_iso_string() == "2025-01-01T12:30:00.000Z");
assert!(date.format("DD MMM YYYY, HH:mm") == "01 Jan 2025, 12:30");
```

## 測試 (Testing) {#testing}

外部依賴項會和其他程式碼一樣參與測試。以下測試會建立具有已知時間戳記的 `Clock`，並檢查 `Postcard` 是否正確輸出該時間：

```move
#[test]
fun test_postcard() {
    let ctx = &mut tx_context::dummy();
    let mut clock = sui::clock::create_for_testing(ctx);

    // 將時間設定為 2025 年 1 月 1 日，12:30:00 UTC
    clock.set_for_testing(1735734600000);

    let postcard = new("Hello from Move!", &clock, ctx);

    assert!(postcard.sent_at == "Wed, 01 Jan 2025 12:30:00 GMT");

    transfer::public_transfer(postcard, ctx.sender());
    clock.destroy_for_testing();
}
```

執行 `sui move test` 會解析依賴項、建置套件並執行測試：

```plaintext
正在執行 Move 單元測試
[ 通過    ] postcard::postcard::test_postcard
測試結果：OK。測試總數：1；通過：1；失敗：0
```

## 總結 (Summary) {#summary}

- Move Registry (MVR) 會將人類可讀名稱（例如 `@potatoes/date`）對應至各網路上的已發佈套件地址。
- `mvr search` 指令（或 [MVR 網站](https://www.moveregistry.com)）可協助探索套件，並顯示其發佈所在的網路。
- `mvr add` 指令會將依賴項記錄加入 `Move.toml`；建置期間，`mvr` 二進位檔會依據作用中的環境解析名稱。
- 解析後的依賴項會固定在 `Move.lock` 文件中，應將其提交至版本控制。
- 依賴項的模組會使用依賴項本身宣告的具名地址匯入。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Move Registry 文件](https://docs.suins.io/move-registry)：包括如何發佈並註冊你自己的套件。
- 本書的[套件清單 (Package Manifest)](./../concepts/manifest)章節。
