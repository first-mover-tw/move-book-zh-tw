---
description: Move 從 Diem 到 Sui 的演進：儲存模型 (storage model) 如何從帳戶式 (account-based) 變更為物件式模型 (object-based model)。
title: Move 的演進 (Evolution of Move)
keywords:
  - Move
  - Sui
  - Move tutorial
  - evolution
  - move
questions:
  - What is Evolution of Move in Move?
  - How do I use Evolution of Move in Move?
answer: 'The evolution of Move from Diem to Sui: how the storage model changed from account-based to the object-based model.'
goal:
  description: 'Reader understands the evolution of Move from Diem to Sui: how the storage model changed from account-based to the object-based model'
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

# Move 的演進 (Evolution of Move) {#evolution-of-move}

Move 由 [Diem](https://www.diem.com/en-us) 建立，用於管理數位資產，其原始儲存模型反映了該區塊鏈的設計。儲存採用 _帳戶式_：每一筆資料——稱為 _資源_——都位於某個帳戶地址之下，而模組只能在與其互動的帳戶之下儲存、讀取及移除資源。在其原始形式中，Move 為此提供專用的全域儲存運算子，而且只有當帳戶透過簽署交易表示同意時，資源才能放置於該帳戶之下。

這個模型帶來了一些實務上的結果，使日常資產操作出乎意料地困難：

- 沒有內建的 _轉移_ 操作。如果 Alice 想將資產 X 傳送給 Bob，定義 X 的模組必須自行實作轉移邏輯：Bob 必須先在自己的帳戶下發布一個「空白」資源（表示同意接收資產），之後 Alice 的交易才能將餘額移入其中。每個模組都得重新實作這套流程。
- 資產依型別及帳戶分別儲存。管理異質集合——例如單一帳戶持有許多不同類型的項目——需要為每種新型別投入大量工作與準備。
- 由於資料位於帳戶之下，資產本身沒有自己的身分：無法指向「這個特定項目」，並跨不同擁有者追蹤它。

Sui 透過圍繞資產本身重新設計儲存模型來解決這些挑戰。在 Sui 中，儲存單位不是帳戶，而是 _物件_——具有自身唯一識別碼，並由系統記錄其擁有者的具型別值。所有權與 _轉移_ 成為原生操作：Alice 可以直接將資產 X 轉移給 Bob，無須 Bob 預先準備任何內容，而 Bob 可以持有任意數量、任意型別的資產。原始 Move 的全域儲存運算子並不存在於 Sui 上的 Move 中——在 [使用物件](./../storage) 章節中，我們將看到它們由操作物件的函式取代。

這些變更為物件模型奠定了基礎，我們將在下一節說明。

## 總結 (Summary) {#summary}

- 原始 Move 使用帳戶式全域儲存：資源位於帳戶地址之下，沒有原生轉移操作，且異質集合難以管理。
- Sui 圍繞 _物件_ 重新設計儲存——具有自身身分及由系統追蹤之所有權的具型別值——使轉移成為原生操作。
- Sui 上的 Move 移除了全域儲存運算子，並以物件儲存函式取代。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sam Blackshear 撰寫的 [Why We Created Sui Move](https://blog.sui.io/why-we-created-sui-move/)
