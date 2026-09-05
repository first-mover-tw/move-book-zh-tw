---
description: Move 中的錯誤處理：使用 abort 以錯誤碼中止執行，並使用 assert! 在智慧合約中強制執行條件。
title: 中止執行 (Aborting Execution)
keywords:
  - Move
  - Sui
  - Move tutorial
  - aborting
  - execution
  - error handling
questions:
  - What is Aborting Execution in Move?
  - How do I use Aborting Execution in Move?
  - What is Abort in Move?
  - What is Omitting the Abort Code in Move?
answer: 'Error handling in Move: use abort to halt execution with error codes and assert! to enforce conditions in smart contracts.'
goal:
  description: 'Reader understands error handling in Move: use abort to halt execution with error codes and assert! to enforce conditions in smart contracts'
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

# 中止執行 (Aborting Execution) {#aborting-execution}

一筆交易會以兩種方式之一結束：要麼成功，且其所做的所有變更都會套用並提交至區塊鏈；要麼會 _中止_，且不會套用任何變更。兩者之間沒有其他可能：交易無法部分成功，而深度巢狀函式呼叫中的中止會使整筆交易失敗。這種全有或全無的模型讓 Move 中的錯誤處理變得簡單且可預測——函式永遠不需要復原其變更，因為中止會一次復原所有內容。

> Move 中沒有 catch 機制。中止無法被攔截或從中復原：它總是會讓整筆交易失敗。這是一項設計選擇——以彈性換取簡潔，並使部分更新的狀態不可能發生。

本節將介紹 Move 提供的中止工具：`abort` 運算式、`assert!` 巨集，以及定義錯誤碼與錯誤訊息的慣例。

## 中止 (Abort) {#abort}

`abort` 關鍵字會立即停止執行。它通常會指定一個 _中止碼_——型別為 `u64` 的[整數](./primitive-types)——並與中止之模組的身分一併回傳給交易的呼叫端。以下是一個範例：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=abort

```

上述程式碼當然會以中止碼 `1` 中止。

中止碼有兩項特性，值得及早牢記：

- 中止碼是 _模組區域_ 的。兩個不同模組都可以使用碼 `1` 中止，但它們代表不同意義；呼叫端必須將該碼與產生它的模組一併解讀。
- 中止碼不帶有訊息。區塊鏈只記錄數值碼與中止位置——讓這些碼易於理解是模組作者的責任，這正是下方的[錯誤常數](#error-constants)與[錯誤訊息](#error-messages)用途所在。

## 省略中止碼 (Omitting the Abort Code) {#omitting-the-abort-code}

原始碼中可以省略中止碼——單獨的 `abort` 運算式是有效的 Move 程式碼：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=clean_abort

```

不過，省略不代表不存在：呼叫端仍會收到一個由編譯器自動推導的 `u64` 中止碼。推導出的碼使用下方[錯誤訊息](#error-messages)所述的 clever-error 編碼——它包含模組與失敗所在的原始碼行，而常數名稱與值則留空。

這種形式有時稱為 _乾淨中止_，很適合根本不應可達的分支——例如涵蓋不可能出現值的 `match` 運算式萬用字元分支（請參閱 [列舉與 Match](./enum-and-match)）。由於推導出的碼會指向失敗位置，卻不說明其 _意義_，對於外部呼叫端實際可以觸發的條件，應優先使用明確的碼或錯誤訊息。

## 斷言巨集 (assert!) {#assert}

`assert!` 巨集是內建巨集，用來檢查條件，並在條件為 false 時中止。它是原本需手動撰寫的 `if` + `abort` 組合之簡寫，也是 Move 程式碼中最常見的中止方式。第一個引數是條件；第二個選用引數是中止碼——省略時，會如同單獨的 `abort` 一樣自動推導一個碼：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=assert

```

常見做法是在函式開頭放置斷言——先檢查所有條件，再進行變更。由於中止會還原整筆交易，這並非安全性所必需；但它能讓函式的需求一目了然，並避免將必然捨棄的工作浪費[gas](./../concepts/what-is-a-transaction)。

## 錯誤常數 (Error Constants) {#error-constants}

像 `assert!(user_has_access, 1)` 這樣的原始數值碼，無法告訴讀者哪裡出錯。為了讓錯誤碼具有描述性，最佳做法是將其定義為[常數](./constants)。錯誤常數遵循專屬命名慣例——以 `E` 加上 CamelCase 描述組成——使其與一般的 `ALL_CAPS` 常數有所區別：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_const

```

錯誤常數是一般的 `u64` 常數，編譯器不會對它們作任何特殊處理。不過，遵循此慣例可讓程式碼自我說明——`assert!(user_has_access, ENoAccess)` 讀起來就像一句話——而收到中止碼的呼叫端也能在模組的原始碼中找到相符的常數。撰寫良好的模組會為其可能產生的每種中止情境定義錯誤常數。

## 錯誤訊息 (Error Messages) {#error-messages}

Move 2024 引入了 _clever errors_——以 `#[error]` 屬性標記的錯誤常數。不同於一般錯誤常數，它們可以是任何型別——最有用的是儲存人類可讀錯誤訊息的 `vector<u8>`：

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_attribute

```

此屬性不會改變中止的本質：交易仍會以 `u64` 中止碼失敗。改變的是該碼的內容——編譯器會將中止的原始碼行號（對於 `assert!` 這類巨集，則是呼叫位置所在行）以及常數名稱和值的參考打包至其中。能理解此格式的工具——Sui CLI、瀏覽器、SDK——會將其解包並顯示完整資訊，例如：

```text
來自 'book::assert_abort::update_value'（第 15 行）的錯誤，中止 'EValueTooLow'：
「值過低，至少應為 10」
```

錯誤訊息免除了查詢數值碼意義的需求，這在面向公眾的應用程式中特別重要，因為閱讀失敗訊息的人通常不是模組作者。此編碼的另一面是，clever 中止碼的數值取決於原始碼版面配置：重新格式化模組或新增一行都會改變它。請依名稱參考這些常數——切勿依其編譯後的數值參考。編碼的確切版面配置請參閱 Move 參考文件中的 [Clever Errors](./../../reference/abort-and-assert/clever-errors)。

## 測試中的中止 (Aborts in Tests) {#aborts-in-tests}

中止和其他行為一樣值得測試。`#[expected_failure]` 屬性會標記預期應中止的測試，而其 `abort_code` 引數會斷言確切的碼——若函式成功或以不同碼中止，測試便會失敗。我們會在[測試](./testing)章節中更詳細介紹此屬性。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Abort and Assert](./../../reference/abort-and-assert)。
- Move 參考文件中的 [Clever Errors](./../../reference/abort-and-assert/clever-errors)。
- 建議閱讀 [Better Error Handling](./../guides/better-error-handling) 指南，了解 Move 錯誤處理的最佳實務。
