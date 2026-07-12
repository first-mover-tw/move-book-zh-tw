---
description: Move 語言中的錯誤處理（Error handling in Move）：使用 abort 以錯誤碼終止執行，並用 assert! 在智能合約中強制檢查條件。
---

# 中止執行 (Aborting Execution) {#aborting-execution}

一筆交易只會以兩種方式結束：要嘛成功，它所做的所有變更都會被套用並提交到區塊鏈上；要嘛_中止_（abort），所有變更都不會被套用。沒有中間狀態：交易不能部分成功，深層巢狀函式呼叫中的中止會讓整筆交易失敗。這種全有或全無的模型，正是讓 Move 中的錯誤處理變得簡單且可預測的原因——函式永遠不需要復原自己的變更，因為一次中止就會一次撤銷所有東西。

> Move 中沒有 catch 機制。中止無法被攔截或恢復：它一定會讓整筆交易失敗。這是一項設計選擇——它用彈性換取簡單性，使得系統不可能陷入部分更新的狀態。

在本節中，我們會探討 Move 提供的中止工具：`abort` 運算式、`assert!` 巨集，以及定義錯誤代碼與錯誤訊息的慣例。

## 中止 (Abort) {#abort}

`abort` 關鍵字會立即停止執行。它通常會附帶一個_中止代碼_（abort code）——型別為 `u64` 的[整數](./primitive-types)——這個代碼會連同中止所在模組的識別資訊，一起回傳給交易的呼叫端。以下是一個範例：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=abort

```

上述程式碼當然會以中止代碼 `1` 中止。

有兩項關於中止代碼的特性值得及早內化：

- 中止代碼是_模組區域性的_。兩個不同模組都可能以代碼 `1` 中止，但它們代表不同的意思；呼叫端必須連同產生該代碼的模組一起解讀這個代碼。
- 中止代碼不攜帶訊息。區塊鏈只會記錄數字代碼和中止的位置——讓代碼可讀是模組作者的責任，這也是下方[錯誤常數](#error-constants)與[錯誤訊息](#error-messages)存在的目的。

## 省略中止代碼 (Omitting the Abort Code) {#omitting-the-abort-code}

原始碼中可以省略中止代碼——單獨一個 `abort` 運算式在 Move 中是合法的：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=clean_abort

```

不過省略不代表不存在：呼叫端仍然會收到一個 `u64` 中止代碼，由編譯器自動衍生。這個衍生出來的代碼使用下方[錯誤訊息](#error-messages)中描述的 clever-error 編碼方式——它攜帶了模組與失敗發生的原始碼行號，而常數名稱與數值則留空。

這種形式有時被稱為_乾淨中止_（clean abort），很適合用在完全不預期會被執行到的分支——例如涵蓋不可能出現數值的 `match` 運算式的萬用分支（見[列舉與 Match](./enum-and-match)）。由於衍生出來的代碼只指出失敗發生的位置，但完全沒有說明其_意義_，因此對於外部呼叫端實際上有可能觸發的情況，應優先使用明確的代碼或錯誤訊息。

## 斷言! (assert!) {#assert}

`assert!` 巨集是一個內建巨集，用來檢查一個條件，若條件為假則中止。它是你原本要手寫的 `if` + `abort` 組合的簡寫，也是 Move 程式碼中目前為止最常見的中止方式。第一個參數是條件；第二個（可選的）參數是中止代碼——當它被省略時，會自動衍生出一個代碼，方式與單獨 `abort` 相同：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=assert

```

一個常見的做法是把 assert 放在函式的開頭——先檢查所有條件，再執行變更。由於中止會回復整筆交易，這麼做並非安全性上的必要條件，但它能讓函式的需求一目了然，並避免在注定會被丟棄的工作上浪費 [gas](./../concepts/what-is-a-transaction)。

## 錯誤常數 (Error Constants) {#error-constants}

像 `assert!(user_has_access, 1)` 這樣的原始數字代碼，完全無法告訴讀者哪裡出了問題。為了讓錯誤代碼具有描述性，好的做法是將它們定義為[常數](./constants)。錯誤常數有自己的命名慣例——`E` 後面接上 CamelCase 描述——這使它們與一般的 `ALL_CAPS` 常數有所區別：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_const

```

錯誤常數屬於一般的 `u64` 常數，編譯器不會給予任何特殊處理。然而，遵循這個慣例能讓程式碼具有自我說明性——`assert!(user_has_access, ENoAccess)` 讀起來就像一句話——而收到中止代碼的呼叫端，可以在模組的原始碼中找到對應的常數。一份寫得好的模組，會為它可能產生的每一種中止情境定義一個錯誤常數。

## 錯誤訊息 (Error Messages) {#error-messages}

Move 2024 引入了 _clever errors_（聰明錯誤）——用 `#[error]` 屬性標記的錯誤常數。與一般錯誤常數不同，它們可以是任意型別——最常用的是 `vector<u8>`，用來存放人類可讀的錯誤訊息：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_attribute

```

這個屬性並不會改變中止的本質：交易仍然會以一個 `u64` 中止代碼失敗。改變的是這個代碼的內容——編譯器會把中止所在的原始碼行號（對於像 `assert!` 這樣的巨集，是呼叫端所在的行號）以及對常數名稱與數值的參考，打包進代碼中。理解此格式的工具——Sui CLI、瀏覽器（explorer）、SDK——會將其解包並顯示完整資訊，類似下方這樣：

```text
Error from 'book::assert_abort::update_value' (line 15), abort 'EValueTooLow':
"The value is too low, it should be at least 10"
```

錯誤訊息省去了查找數字代碼含義的需要，這在面向大眾的應用程式中尤其重要，因為閱讀失敗訊息的人往往不是模組的作者。這種編碼方式的另一面是，clever abort 代碼的數字值取決於原始碼的排版：重新排版模組或新增一行都會改變這個值。應該用名稱來參考這些常數——絕不要用它們編譯後的數字值。這種編碼的確切格式，記錄在 Move 參考手冊的[Clever Errors](./../../reference/abort-and-assert/clever-errors)中。

## 測試中的中止 (Aborts in Tests) {#aborts-in-tests}

中止和其他行為一樣，值得被測試。`#[expected_failure]` 屬性用來標記一個預期會中止的測試，其 `abort_code` 參數會斷言確切的代碼——若函式成功執行，或以不同的代碼中止，該測試就會失敗。我們會在[測試](./testing)一節中更詳細地介紹這個屬性。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[Abort and Assert](./../../reference/abort-and-assert)。
- Move 參考手冊中的[Clever Errors](./../../reference/abort-and-assert/clever-errors)。
- 我們建議閱讀[更好的錯誤處理](./../guides/better-error-handling)指南，以了解 Move 中錯誤處理的最佳實務。
