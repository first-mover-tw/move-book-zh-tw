---
description: '使用 #[test] 屬性、預期失敗及測試智慧合約邏輯的公用程式，在 Move 中撰寫及執行單元測試 (unit tests)。'
title: 測試 (Testing)
keywords:
  - Move
  - Sui
  - Move tutorial
  - testing
questions:
  - What is Testing in Move?
  - How do I use Testing in Move?
  - What is Test-Only Code in Move?
  - What is Explore More in Move?
answer: 'Write and run unit tests in Move using the #[test] attribute, expected failures, and utilities for testing smart contract logic.'
goal:
  description: 'Reader can write and run unit tests in Move using the #[test] attribute, expected failures, and utilities for testing smart contract logic'
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

# 測試 (Testing) {#testing}

Move 內建測試框架，讓你可以在原始碼旁撰寫單元測試。測試是以 `#[test]` 屬性標記的函式，不會納入已發布的位元組碼，並透過
`sui move test` 指令執行。此框架透過 `#[expected_failure]` 支援預期失敗，並透過 `#[test_only]` 支援僅供測試使用的輔助工具。

```move
module book::testing;

#[test_only]
use std::unit_test::assert_eq;

// 測試函式不接受引數，也不回傳任何內容
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

若測試執行至完成便會通過，若中止則會失敗——這正是當 `assert_eq!` 巨集的兩個值不同時所做的事。若要檢查任意條件，可以使用更通用的
[`assert!`](./assert-and-abort) 巨集；兩者都是 Move 測試的主力工具。上述第二個測試會反轉結果：`#[expected_failure(abort_code = 0)]` 讓測試僅在以指定代碼中止時通過，這是測試錯誤條件的方式。

## 僅供測試使用的程式碼 (Test-Only Code) {#test-only-code}

`#[test_only]` 屬性會將模組成員，或整個模組，標記為僅在測試時編譯。測試輔助工具、模擬建構子，以及如上方 `std::unit_test` 的匯入項目，都會以此方式標記：已發布的位元組碼不會包含測試機制，而測試則可存取所需的一切，包括公開 API 刻意未公開的內容。

## 探索更多 (Explore More) {#explore-more}

本頁僅觸及皮毛。專門的[測試](./../testing/index.md)章節會逐步說明測試情境、涵蓋率報告、gas 分析、系統物件的使用方式，以及撰寫可在正式環境中真正信賴之測試的最佳實務。

## 接下來 (What's Next) {#whats-next}

本頁結束 Move 基礎章節。你現在可以定義模組與自訂型別、控制值是否可複製或捨棄、透過參考或值傳遞它們、以模式比對撰寫邏輯、利用泛型與巨集進行抽象，並測試所有內容。目前我們暫時擱置的部分，正是 Move 在 Sui 上的特色：儲存模型。[物件模型](./../object/)章節正是從這裡開始——它介紹會成為鏈上資產的 Move 結構體 _物件_，後續章節則說明如何儲存、擁有及轉移它們。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[單元測試](./../../reference/unit-testing)。
