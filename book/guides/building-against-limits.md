---
description: Sui 網路限制以及如何在限制內進行建置：物件大小、動態欄位、交易限制與協定約束。
title: 建置極限 (Building Against Limits)
keywords:
  - Move
  - Sui
  - Move tutorial
  - building
  - against
  - limits
questions:
  - What is Building Against Limits in Move?
  - How do I use Building Against Limits in Move?
  - What is Transaction Size in Move?
  - What is Object Size in Move?
answer: 'Sui network limits and how to build within them: object size, dynamic fields, transaction limits, and protocol constraints.'
goal:
  description: 'Reader understands sui network limits and how to build within them: object size, dynamic fields, transaction limits, and protocol constraints'
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

# 配合限制進行開發 (Building Against Limits) {#building-against-limits}

為了確保網路的安全與穩定，Sui 訂定了一些限制與約束。這些限制旨在防止濫用，並確保網路保持穩定與高效。本指南概述了這些限制與約束，以及如何建置應用程式以在這些限制內運作。

這些限制定義在協定設定中，並由網路強制執行。如果超出任何限制，交易將會被拒絕或中止。這些限制作為協定的一部分，只能透過網路升級來更改。

## 交易大小 (Transaction Size) {#transaction-size}

交易大小限制為 128KB。這包含交易酬載的大小、交易簽名的大小以及交易中繼資料的大小。如果交易超出此限制，將會被網路拒絕。

## 物件大小 (Object Size) {#object-size}

物件大小限制為 256KB。這包含物件資料的大小。如果物件超出此限制，將會被網路拒絕。雖然單一物件無法繞過此限制，但若需要更廣泛的儲存選項，可以使用基礎物件結合透過動態欄位（例如 Bag）附加的其他物件來達成。

## 單一純粹引數大小 (Single Pure Argument Size) {#single-pure-argument-size}

單一純粹引數的大小限制為 16KB。大於此限制的交易引數將導致執行失敗。因此，若要建立超過約 500 個地址的向量（鑑於單一地址為 32 位元組），需要在交易區塊中或在 Move 函式中動態合併它。像是 `vector::append()` 這樣標準的函式可以合併兩個約 16KB 的向量，產生約 32KB 的資料作為單一數值。

## 建立的最大物件（與動態欄位）數量 (Maximum Number of Objects (and Dynamic Fields) Created) {#maximum-number-of-objects-and-dynamic-fields-created}

在單一交易中可以建立的物件數量上限為 2048 個。如果交易嘗試建立超過 2048 個物件，將會被網路拒絕。這也會影響[動態欄位](./../programmability/dynamic-fields.md)，因為鍵與值都是物件。因此，在單一交易中可以建立的[動態欄位](./../programmability/dynamic-fields.md)數量上限為 1000 個。此限制也適用於動態物件欄位。

## 存取的動態欄位最大數量 (Maximum Number of Dynamic Fields Accessed) {#maximum-number-of-dynamic-fields-accessed}

在單一交易中可以存取的動態欄位數量上限為 1000 個。如果交易嘗試存取超過 1000 個動態欄位，將會被網路拒絕。

## 事件最大數量 (Maximum Number of Events) {#maximum-number-of-events}

在單一交易中可以發出的事件數量上限為 1024 個。如果交易嘗試發出超過 1024 個事件，將會被中止。
