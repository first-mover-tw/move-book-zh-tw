---
description: 進階 Sui (Sui) 可程式設計：Move (Move) 中的模式、事件、動態欄位、能力、BCS 序列化與設計模式。
title: 進階可程式設計 (Advanced Programmability)
keywords:
  - Move
  - Sui
  - Move tutorial
  - advanced
  - programmability
  - abilities
questions:
  - What advanced features does Move on Sui offer?
  - What programmability patterns are available?
answer: Move on Sui provides transaction context, module initializers, pattern matching, type reflection, events, dynamic fields, BCS serialization, and other advanced features.
goal:
  description: Reader understands the advanced programmability features available in Move on Sui
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

# 進階可程式設計性 (Advanced Programmability) {#advanced-programmability}

在前面的章節中，我們已介紹過 [Move 基礎](./../move-basics)與
[Sui 儲存模型](./../storage)。現在該深入探討 Sui 進階
可程式設計性的主題。本章介紹更複雜的 Move 與
Sui 概念、實務與功能，這些對於建置更精密的應用程式至關重要。

各節的排列順序使每一節都建立在前一節的基礎上，但它們也構成幾條大致
獨立的脈絡，因此你可以直接閱讀目前所需的部分：

- **執行環境** - 程式可以得知其執行所在交易及周遭系統的哪些資訊，
  以及它如何與外部世界通訊：
  [Sui Framework](./sui-framework)、[交易情境](./transaction-context)、
  [模組初始化器](./module-initializer)、[Epoch 與時間](./epoch-and-time)、
  [事件](./events)，以及[二進位標準序列化](./bcs)。

- **大規模儲存** - 從以簡單向量為基礎的集合，到動態欄位這項可將任意
  資料附加至物件、並解除靜態型別與大小限制的基本原語：
  [集合](./collections)、[包裝器型別](./wrapper-type-pattern)、
  [動態欄位](./dynamic-fields)、[動態物件欄位](./dynamic-object-fields)，以及
  [動態集合](./dynamic-collections)。

- **權限模式** - Move 對存取控制的解答：從作為權限的擁有物件，到由系統
  支援的保證，以及建置於其上的功能：
  [能力](./capability)、[見證](./witness-pattern)、
  [一次性見證](./one-time-witness)、[發佈者](./publisher)、[顯示](./display)，以及
  [燙手山芋](./hot-potato-pattern)。

- **資產與資金** - 可互換價值及持有它的兩種方式：作為物件，以及作為直接
  附加至地址的餘額：[餘額與代幣](./balance-and-coin)及
  [地址餘額](./address-balances)。

- **原始碼演進** - 原始碼發佈後會發生什麼事：發佈套件的新版本、
  保護共享狀態免受舊版本影響，以及遷移資料：
  [套件升級](./package-upgrades)。

> 本章許多原始碼範例都是以[測試](./../move-basics/testing)撰寫，並使用
> 框架中僅供測試使用的輔助工具：`tx_context::dummy()` 會建立預留位置的交易
> 情境，而 `std::unit_test::destroy` 會在測試結尾消耗任何值。我們會在
> [測試](./../testing)章節中詳細介紹測試技巧。
