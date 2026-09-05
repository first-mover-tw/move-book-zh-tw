---
title: 測試 Move 程式 (Testing Move Programs)
description: 在 Sui 上測試 Move 智慧合約 (smart contracts)：單元測試 (unit tests)、測試情境 (test scenarios)、程式碼檢查 (linting)、涵蓋率報告 (coverage reports)、gas 效能分析 (gas profiling) 及最佳實務 (best practices)。
keywords:
  - Move
  - Sui
  - Move tutorial
  - testing
  - move
  - programs
questions:
  - How do I test Move code?
  - What testing framework does Move use?
answer: 'Move has a built-in testing framework with #[test] annotations, test-only functions, and test scenarios for simulating transactions.'
goal:
  description: Reader understands the Move testing framework and can write effective tests
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 30
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 測試 (Testing) {#testing}

Move 的設計理念是[預設安全](./../foreword.md)：其型別系統與內建防護機制可防止困擾其他智慧合約語言的整類錯誤，例如重入、算術溢位，以及未經授權的資產存取。但語言安全性不等於程式正確性。型別系統能確保你的原始碼不會違反 Move 的規則，卻無法驗證你的轉移邏輯是否將資金傳送給正確的收款人、你的拍賣是否在正確時間結束，或你的存取控制是否符合預期的政策。這些是設計層面的特性，而非語言本身的特性——只能透過測試來驗證。

在鏈上程式設計中，出錯的代價格外高昂：

- **財務風險**：處理資產的原始碼若存在錯誤，可能導致資金永久損失。轉移邏輯或存取控制中一個被忽略的邊界案例，就可能遭到利用並造成不可逆的損害。
- **不可變性**：智慧合約原始碼一旦部署，未必能輕易修改；即使可以升級，先前版本的原始碼仍會一直可用。部署前徹底測試是防範漏洞的主要防線。
- **對抗性環境**：已發布的 Move 套件實際上是開放原始碼——任何人都能讀取及反編譯鏈上位元組碼。這表示惡意行為者可以詳細研究你的原始碼，尋找可利用的缺陷。你的原始碼不僅必須處理預期輸入，也必須能應對蓄意破壞它的嘗試。
- **可組合性風險**：Move 模組會與其他鏈上原始碼互動。測試必須驗證你的原始碼不僅能獨立正確運作，也能在與其他套件組合時正確運作。

考量這些風險，完整測試並非可有可無——對於任何處理資產或實作商業邏輯的 Move 應用程式而言，這是不可或缺的。
