---
description: '以撰寫測試（testing）為主軸的技術短句翻譯，不涉及技能觸發。


  使用 `#[test]` 屬性（attribute）、預期失敗（expected failures）以及測試工具，在 Move 中撰寫並執行單元測試（unit tests），驗證智能合約邏輯。'
---

# Testing 測試 (Testing) {#testing}

Move 內建測試框架，讓你可以在程式碼旁邊撰寫單元測試。測試是標記 `#[test]` 屬性的函式，會從已發布的位元組碼中排除，並用 `sui move test` 指令執行。此框架透過 `#[expected_failure]` 支援預期失敗，並透過 `#[test_only]` 支援僅測試用的輔助函式。

```move
module book::testing;

#[test_only]
use std::unit_test::assert_eq;

// 測試函式不接受任何參數，也不回傳任何東西
#[test]
fun simple_test() {
    let sum = 2 + 2;
    assert_eq!(sum, 4);
}

#[test, expected_failure(abort_code = 0)]
fun test_fail() {
    abort 0
}
```

若測試執行到完成則視為通過，若中止（abort）則視為失敗——這正是當 `assert_eq!` 巨集的兩個值不相等時所做的事。對於任意條件，還有更通用的 [`assert!`](./assert-and-abort) 巨集；這兩者都是 Move 測試的主力工具。上面第二個測試反轉了結果：`#[expected_failure(abort_code = 0)]` 只有在測試以給定的錯誤碼中止時才會通過，這是測試錯誤情況的方式。

## 僅測試用程式碼 (Test-Only Code) {#test-only-code}

`#[test_only]` 屬性將一個模組成員——或整個模組——標記為僅在測試時編譯。測試輔助函式、模擬用建構函式，以及像上面 `std::unit_test` 這樣的匯入，都是用這種方式標記的：已發布的位元組碼不會包含測試機制，而測試則可以存取它們所需的一切，包括公開 API 刻意不曝露的東西。

## 進一步探索 (Explore More) {#explore-more}

本頁僅觸及皮毛。專門的 [Testing 測試](./../testing/index.md) 章節會深入介紹測試情境、覆蓋率報告、gas 效能分析、系統物件的操作，以及撰寫可靠測試的最佳實踐。

## 下一步 (What's Next) {#whats-next}

本頁結束了 Move Basics 章節。你現在已經能夠定義模組與自訂型別、控制值是否可以複製或捨棄、以參考或以值的方式傳遞它們、用模式比對撰寫邏輯、用泛型與巨集將其抽象化——並對這一切進行測試。到目前為止我們暫時擱置的，正是讓 Move on Sui 與眾不同之處：儲存模型。[Object Model 物件模型](./../object/) 章節正是從這裡開始——它介紹了 _objects_（物件），也就是會成為鏈上資產的 Move struct，而其後的章節則會展示如何儲存、擁有並轉移它們。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[Unit Testing 單元測試](./../../reference/unit-testing)。
