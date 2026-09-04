---
description: Sui 網路 (Sui network) 限制及其因應建置方式：物件大小、動態欄位、交易限制與協定限制。
title: 在限制下建置 (Building Against Limits)
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

# 在限制下建置 (Building Against Limits) {#building-against-limits}

為了確保網路的安全性與資安防護，Sui 設有特定的限制與約束。這些限制旨在防止濫用，並確保網路維持穩定且有效率。
本指南概述這些限制與約束，以及如何建置能在其範圍內運作的應用程式。

這些限制定義於協定設定中，並由網路強制執行。若超出任何限制，交易將遭到拒絕或中止。這些限制屬於協定的一部分，因此只能透過網路升級來變更。

## 交易大小 (Transaction Size) {#transaction-size}

交易大小限制為 128KB。這包含交易承載資料、交易簽章及交易中繼資料的大小。若交易超出此限制，將遭網路拒絕。

## 物件大小 (Object Size) {#object-size}

物件大小限制為 256KB。這包含物件資料的大小。若物件超出此限制，將遭網路拒絕。雖然單一物件無法略過此限制，但若需要更大規模的儲存選項，可以使用基礎物件，並透過動態欄位（例如 Bag）附加其他物件。

## 單一純引數大小 (Single Pure Argument Size) {#single-pure-argument-size}

單一純引數的大小限制為 16KB。大於此限制的交易引數將導致執行失敗。因此，若要建立超過約 500 個地址的向量（假設單一地址為 32 位元組），就必須在 Transaction Block 或 Move 函式中動態合併。`vector::append()` 等標準函式可以合併兩個約 16KB 的向量，產生約 32KB 的資料作為單一值。

## 建立物件（及動態欄位）的最大數量 (Maximum Number of Objects (and Dynamic Fields) Created) {#maximum-number-of-objects-and-dynamic-fields-created}

單一交易可建立的物件數量上限為 2048。若交易嘗試建立超過 2048 個物件，將遭網路拒絕。這也會影響[動態欄位](./../programmability/dynamic-fields.md)，因為索引鍵和值皆為物件。因此，單一交易可建立的[動態欄位](./../programmability/dynamic-fields.md)數量上限為 1000。此限制同樣適用於動態物件欄位。

## 存取動態欄位的最大數量 (Maximum Number of Dynamic Fields Accessed) {#maximum-number-of-dynamic-fields-accessed}

單一交易可存取的動態欄位數量上限為 1000。若交易嘗試存取超過 1000 個動態欄位，將遭網路拒絕。

## 事件最大數量 (Maximum Number of Events) {#maximum-number-of-events}

單一交易可發出事件的數量上限為 1024。若交易嘗試發出超過 1024 個事件，將會中止。
