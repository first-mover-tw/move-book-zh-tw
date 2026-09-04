---
description: Sui 快速路徑 (fast path) 的設計：建構擁有 (structure-owned) 與共享物件 (shared objects)，以將交易平行處理 (transaction parallelism) 與效能 (performance) 最大化。
title: 快速路徑 (Fast Path)
keywords:
  - Move
  - Sui
  - Move tutorial
  - fast
  - path
questions:
  - What is Fast Path in Move?
  - How do I use Fast Path in Move?
  - What is Frozen objects in Move?
  - What is In Practice in Move?
answer: 'Design for the fast path in Sui: structure owned vs shared objects to maximize transaction parallelism and performance.'
goal:
  description: 'Reader understands design for the fast path in Sui: structure owned vs shared objects to maximize transaction parallelism and performance'
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

# 快速路徑 (Fast Path) {#fast-path}

由於 Sui 的物件模型與資料組織模型，某些操作可以用更有效率且平行化的方式執行。這稱為**快速路徑**。會接觸共用狀態的交易需要共識，因為多方可以同時存取它。然而，若交易只接觸私有狀態（擁有的物件），則不需要共識。這就是快速路徑。

我們最喜歡用咖啡機和咖啡杯來舉例：放在辦公室裡的咖啡機是共用資源——每個人都能使用，但同一時間只能有一位使用者。另一方面，咖啡杯是私有資源——它屬於特定的人，且只有那個人可以使用。要泡咖啡，需要使用咖啡機；若有人正在使用，就必須等待。不過，咖啡泡好並倒入杯中後，這個人便能拿著杯子喝咖啡，無須等待其他人。

相同原則也適用於 Sui。若交易只接觸私有狀態（裝著咖啡的杯子），便能在不經共識的情況下執行。若接觸共用狀態（咖啡機），則需要共識。這就是快速路徑。

## 凍結物件 (Frozen objects) {#frozen-objects}

只有修改共用狀態時才需要共識。若物件不可變，便會被視為「常數」，且可被平行存取。凍結物件可用於在多方之間分享不可變更的資料，而無須共識。

## 實務上 (In Practice) {#in-practice}

```move file=packages/samples/sources/programmability/fast-path.move anchor=main

```

## 特殊案例：時鐘 (Special Case: Clock) {#special-case-clock}

具有保留地址 `0x6` 的 `Clock` 物件，是共用物件的一種特殊案例；它無法在一般交易中以可變參考傳遞。嘗試這麼做將不會成功，且交易會遭拒絕。由於此限制，`Clock` 物件只能以不可變方式存取，因此可在無須共識的情況下平行執行交易。

<!-- 補充更多關於原因與方式的內容 -->
