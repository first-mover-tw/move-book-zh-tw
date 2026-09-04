---
description: Sui 中的快速路徑 (Fast path) 與共識 (consensus)：自有物件 (owned objects) 如何略過共識以加快交易 (transactions)，而共享物件 (shared objects) 則需要排序 (ordering)。
title: 快速路徑 (Fast Path) 與共識 (Consensus)
keywords:
  - Move
  - Sui
  - Move tutorial
  - fast
  - path
  - consensus
questions:
  - What is Fast Path and Consensus in Move?
  - How do I use Fast Path and Consensus in Move?
  - What is Concurrency Challenge in Move?
  - What is Fast Path in Move?
answer: 'Fast path vs consensus in Sui: how owned objects skip consensus for faster transactions while shared objects require ordering.'
goal:
  description: 'Reader understands fast path vs consensus in Sui: how owned objects skip consensus for faster transactions while shared objects require ordering'
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

# 快速路徑與共識 (Fast Path and Consensus) {#fast-path-and-consensus}

物件模型允許根據物件的擁有權類型，採用不同的交易執行路徑。交易執行路徑決定網路如何處理及驗證交易。本節將探討 Sui 中不同的交易執行路徑，以及它們如何與共識機制互動。

## 並行挑戰 (Concurrency Challenge) {#concurrency-challenge}

區塊鏈技術的核心面臨一項根本的並行挑戰：在去中心化環境中，多方可能同時嘗試修改或存取相同資料。這需要一套系統來排序及驗證交易，以維持網路的一致性。Sui 透過共識機制因應此挑戰，確保所有節點都同意交易的順序及狀態。

設想一個市集情境，Alice 與 Bob 同時嘗試購買相同資產。網路必須解決此衝突以防止雙重支付，確保至多只有一筆交易成功，而另一筆交易會被正確拒絕。

## 快速路徑 (Fast Path) {#fast-path}

然而，並非所有交易都需要相同程度的驗證。如果 Alice 將她擁有的物件轉移給 Bob，其他任何一方一開始就不可能接觸過該物件——Alice 是其唯一擁有者。沒有需要解決的衝突，因此網路不需要將此交易與網路中的所有其他交易排序。僅存取帳戶擁有物件的交易會採用 _快速路徑_：它們略過完整排序並迅速處理。這是[單一擁有者](./ownership#account-owner-or-single-owner)模型的直接優勢——獨佔存取完全消除了並行問題。

不可變物件也符合快速路徑的條件。由於[凍結物件](./ownership#immutable-frozen-state)永遠無法改變，任意數量的交易都能同時讀取它，而無須排序。

## 共識路徑 (Consensus Path) {#consensus-path}

存取*共享*物件的交易正是共識存在的原因：多方可能同時嘗試修改相同物件，因此網路必須就這些修改的順序達成共識。此類交易會經過*共識路徑*——在執行前由共識協定排序，讓所有節點的狀態保持一致。

[Party 物件](./ownership#party-objects)也會採用共識路徑，即使它們只有一位擁有者——這正是其取捨：僅限擁有者存取，並搭配共識排序。

一項重要細節是：Sui 的共識是依*物件*排序交易，而非全域排序。接觸兩個無關共享物件的兩筆交易不會彼此競爭——只有存取*相同*共享物件的交易才需要彼此排序。這讓 Sui 能夠平行執行沒有衝突的交易。

單一交易可以混合輸入：若同時存取擁有物件及共享物件，便會經過共識——執行路徑由「最慢」的輸入決定。設計應用程式時值得牢記這點：你的核心狀態是共享物件，或維持在擁有物件中，會直接影響使用者交易的執行方式。

## 由物件擁有的物件 (Objects Owned by Objects) {#objects-owned-by-objects}

最後，由其他物件擁有的物件會遵循其父物件的執行路徑——子物件只能透過其父物件存取，因此存取它代表必須先存取父物件。若父物件是*共享*物件，使用子物件需要共識；若父物件由帳戶擁有，整條鏈都符合快速路徑的條件。

## 總結 (Summary) {#summary}

- **快速路徑**：僅涉及帳戶擁有或不可變物件的交易，無須完整共識排序即可迅速處理。
- **共識路徑**：涉及共享或 Party 物件的交易會由共識排序——依物件排序，因此沒有衝突的交易可以平行執行。
- **混合輸入**：同時接觸擁有物件及共享物件的交易會經過共識。
- **由物件擁有的物件**：子物件遵循其父物件的執行路徑。

## 後續步驟 (Next Steps) {#next-steps}

至此完成物件模型的概念導覽：你已了解物件是什麼、誰能擁有它，以及擁有權如何塑造執行方式。下一章——[使用物件](./../storage)——會將這些概念轉化為原始碼：如何定義物件，以及如何從 Move 模組轉移、共享及凍結它。
