---
description: Sui 網路限制與其開發應對之道 (Sui network limits and how to build within them)：物件大小 (object size)、動態欄位 (dynamic fields)、交易限制 (transaction limits) 與協定約束 (protocol constraints)。
---

# 針對限制進行開發 (Building Against Limits)

為了保證網路的安全，Sui 設定了某些限制和約束。這些限制旨在防止濫用並確保網路保持穩定和高效。本指南概述了這些限制，以及如何使你的應用程式在這些限制下工作。

## 交易大小 (Transaction Size)

單筆交易的大小限制為 128KB。這包括交易負載 (payload)、簽章和中繼資料的大小。

## 物件大小 (Object Size)

單個物件的大小限制為 256KB。如果你需要更多儲存空間，可以使用動態欄位（如 Bag）將多個物件連接在一起。

## 單個純粹參數大小 (Single Pure Argument Size)

單個純粹參數的大小限制為 16KB。

## 建立物件（和動態欄位）的最大數量

單次交易中可以建立的最大物件數量為 2048 個。這也影響到[動態欄位](./../programmability/dynamic-fields.md)，因為鍵和值都是物件。

## 存取動態欄位的最大數量

單次交易中可以存取的最大動態欄位數量為 1000 個。

## 事件的最大數量

單次交易中可以發出的最大事件數量為 1024 個。
