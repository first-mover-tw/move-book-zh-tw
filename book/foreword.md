---
description: Move 的設計理念：預設安全性 (security by default)、表達能力 (expressiveness)，以及適用於智慧合約 (smart contracts) 的直覺式資源管理 (intuitive resource management)。
title: 前言 (Foreword)
keywords:
  - Move
  - Sui
  - Move tutorial
  - foreword
questions:
  - What is the design philosophy of Move?
  - Why was Move created?
  - What makes Move different from other smart contract languages?
answer: Move is a smart contract language designed around security by default, expressiveness for digital assets, and intuitive resource management, making it safe for programming with digital assets.
goal:
  description: 'Reader understands the design philosophy behind Move: security, expressiveness, and intuitive resource management'
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

# 前言 (Foreword) {#foreword}

本書專為 Move 而作，這是一種智能合約語言，旨在以數位資產的安全性程式設計為核心。Move 的設計圍繞以下價值觀：

1.  **預設安全性 (Secure by default)：** 不安全的語言嚴重阻礙了易於存取的智能合約開發和數位資產的主流採用。智能合約語言的首要職責是透過建構來預防盡可能多的潛在安全問題（例如重入、遺漏存取控制檢查、算術溢位等）。對 Move 的任何更改都應保留或增強其現有的安全保障。

2.  **本質上的表達力 (Expressive by nature)：** Move 必須讓程式設計師能夠編寫他們能想像到的任何智能合約。但我們關心撰寫 Move 的*感覺*，如同我們關心 Move 允許你做什麼一樣——該語言應足夠豐富，以提供任務所需的特性，同時又足夠精簡，讓選擇顯而易見。Move 工具鏈應該是生產力的增強器和思考夥伴。

3.  **所有人的直覺性 (Intuitive for all)：** 智能合約只是一個有用應用程式的一部分。Move 應該理解其使用的更廣泛背景，並在設計時考慮到智能合約開發者和應用程式開發者。開發者應該能夠輕鬆學習如何讀取由 Move 管理的狀態、建置由 Move 驅動的交易，以及編寫新的 Move 程式碼。

Move 的核心技術元素包括：

- 透過可程式化*物件*，為數位資產提供安全、熟悉且靈活的抽象。
- 豐富的*能力*系統（受線性型別啟發），賦予程式設計師對值如何建立、銷毀、儲存、複製和轉移的極致控制。
- 具有強大封裝特性的*模組*系統，可在保持此控制的同時實現程式碼重複使用。
- _動態欄位_，用於在物件之間建立層級關係。
- _可程式化交易區塊_ (PTBs)，以實現 Move 驅動 API 的客戶端原子組合。

Move 誕生於 2018 年，是 Facebook Libra 計畫的一部分。它於 2019 年公開，第一個由 Move 驅動的網路於 2020 年推出。截至 2024 年 4 月，目前有許多由 Move 驅動的鏈正在生產中，還有更多正在開發。Move 是一種嵌入式語言，具有平台無關的核心，這意味著它在使用它的每個鏈中都呈現出略有不同的特性。

建立一種新的程式語言並圍繞它建立一個社群，這是一個雄心勃勃的長期計畫。一種語言必須在相關方面比替代方案好一個數量級才有機會，但即使如此，社群的品質比技術基礎更重要。Move 是一種年輕的語言，但在差異化和社群方面都取得了良好的開端。一小群但狂熱的智能合約程式設計師和核心貢獻者，透過 Move 的價值觀團結一致，正在推動智能合約能做什麼、它們能實現的應用程式，以及誰能（安全地）編寫它們的極限。如果這激勵了你，請繼續閱讀！

— Sam Blackshear，Move 創作者
