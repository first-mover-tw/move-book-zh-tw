# 中斷執行

交易不是成功就是失敗。成功的執行會套用對物件和鏈上資料所做的所有更改，並將交易提交到區塊鏈。或者，如果交易中斷，則不會套用更改。使用 `abort` 關鍵字來中斷交易並還原所做的任何更改。

> 值得注意的是，Move 中沒有擷取 (catch) 機制。如果交易中斷，迄今為止所做的更改將被還原，並且該交易被視為失敗。

## 中斷 (Abort)

`abort` 關鍵字用於中斷交易的執行。它與中斷碼 (abort code) 結合使用，中斷碼會返回給交易的呼叫者。中斷碼是一個 `u64` 類型的 [整數](./primitive-types)。

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=abort

```

上面的程式碼當然會以中斷碼 `1` 中斷。

## assert!

`assert!` 巨集是一個內建巨集，可用於斷言一個條件。如果條件為 false，交易將以給定的中斷碼中斷。`assert!` 巨集是在條件不滿足時中斷交易的便捷方式。該巨集縮短了原本使用 `if` 表達式 + `abort` 編寫的程式碼。`code` 參數是可選的，但必須是一個 `u64` 值或一個 `#[error]`（有關更多資訊，請參見下文）。

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=assert

```

## 錯誤常數

為了使錯誤代碼更具描述性，定義 [錯誤常數](./constants) 是一個很好的做法。錯誤常數被定義為 `const` 宣告，通常以 `E` 開頭，後接大駝峰式 (camel case) 名稱。錯誤常數與其他常數類似，沒有任何特殊處理。但是，它們通常用於提高程式碼的可讀性，並使中斷情境更容易理解。

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_const

```

## 錯誤訊息

Move 2024 引入了一種特殊類型的錯誤常數，標有 `#[error]` 屬性。此屬性允許錯誤常數為 `vector<u8>` 類型，並可用於儲存錯誤訊息。

```move file=packages/samples/sources/move-basics/assert-and-abort.move anchor=error_attribute

```

## 延伸閱讀

- Move 參考手冊中的 [中斷與斷言 (Abort and Assert)](./../../reference/abort-and-assert)。
- 我們建議閱讀 [更好的錯誤處理](./../guides/better-error-handling) 指南，以瞭解 Move 中錯誤處理的最佳實踐。
