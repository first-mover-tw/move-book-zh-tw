---
description: 在 Sui Move 中發出與測試事件 (Emit and Test Events)：在智慧合約中通知鏈下監聽器有關鏈上活動的資訊。
---

# 事件 (Events) {#events}

鏈上儲存保存的是應用程式的*目前*狀態：物件、其欄位以及其擁有者。它不保存的是導致此狀態的動作歷史。一個市集模組儲存已上架的物品，但一旦某個物品售出並且該物件轉手，鏈上就不會留下購買的痕跡——支付的價格、售出的時間，或涉及的各方。然而，應用程式經常正需要這些資訊：活動動態、交易歷史，或分析資料。

_事件（Events）_ 就是為此而生的機制。事件是附加在成功交易結果上並儲存在鏈下的一段資料。發出事件不會修改任何物件，也不需要儲存費用；相反地，事件會被全節點索引，鏈下服務可以查詢或訂閱它們。事件是 Move 程式與外部世界溝通的主要方式。

## 定義 (Definition) {#definition}

事件是透過 [Sui Framework](./sui-framework) 的 [`sui::event`][event-framework] 模組中定義的 `emit` 函式發出的：

```move
module sui::event;

/// 發出一個自訂的 Move 事件,將資料傳送到鏈下。
///
/// 用於建立自訂索引並在鏈上進行追蹤
/// 活動,以最適合特定應用程式的方式呈現。
///
/// 型別 `T` 是為事件建立索引的主要方式,並可以包含
/// 幻影參數,例如 `emit(MyEvent<phantom T>)`。
public native fun emit<T: copy + drop>(event: T);
```

事件可以是任何具有 [copy](./../move-basics/copy-ability) 與 [drop](./../move-basics/drop-ability) 能力的自訂型別。此外，Sui 驗證器要求該型別必須是[_發出該事件的模組內部_](./../storage/internal-constraint)的：不可能發出另一個模組中定義的型別，而且即使符合 `copy + drop` 的要求，[基本型別](./../move-basics/primitive-types)也無法被發出。這項規則使事件型別成為一個無法偽造的標籤——`ItemPurchased` 事件只能來自宣告它的那個模組。

## 發出事件 (Emitting Events) {#emitting-events}

要發出事件，需為它定義一個 struct，並將該 struct 的實例傳給 `event::emit`。事件資料是以值傳遞的方式傳入，並作為交易結果的一部分傳送到鏈下：

```move file=packages/samples/sources/programmability/events.move anchor=emit

```

事件的型別是鏈下查詢的主要過濾條件——服務透過指定型別名稱來訂閱 `ItemPurchased` 事件。這暗示了一個簡單的設計原則：為每個動作發出一個專屬的型別，並以該動作發生的過去式來命名它——`ItemPurchased`、`AuctionStarted`、`ConfigUpdated`。在事件內部，應包含索引器在不需另外抓取任何資訊的情況下，理解該動作所需的值：涉及的物件 ID、金額，以及相關的地址。

請注意，事件是附加在*成功的*交易上的：如果交易在呼叫 `emit` 之後中止，就不會記錄任何事件。

## 事件結構 (Event Structure) {#event-structure}

事件會成為*交易效果（transaction effects）* 的一部分，系統會為每個事件附加中繼資料：

- _寄件者（sender）_——簽署此交易的地址；
- _交易摘要（transaction digest）_——將事件與發出它的交易連結起來；
- _時間戳記（timestamp）_——最終確認該交易的檢查點（checkpoint）的時間，該交易的所有事件共用此時間戳記；
- 事件的*型別簽章（type signature）*，包括發出它的 package 與模組。

由於寄件者與交易摘要一定會存在於中繼資料中，因此不需要在事件欄位中重複這些資訊。事件 struct 中的 `sender: address` 欄位是多餘的，除非「邏輯上的」寄件者與交易簽署者不同（例如，在代表使用者執行的贊助交易中）。

必須理解的是，事件是單向通道。發出的事件不會儲存在鏈上，也無法被 Move 程式碼讀回——無論是在同一筆交易中，還是任何後續的交易中皆然。如果一個值需要被程式存取，它應該存放在物件中；如果它需要被外部世界看到，它應該存放在事件中。

## 測試事件 (Testing Events) {#testing-events}

由於事件是應用程式與其鏈下服務之間的介面，測試正確的事件是否以正確的值被發出就顯得相當重要。`sui::event` 模組為此提供了兩個僅供測試使用的函式：`num_events`，回傳目前測試中已發出的事件數量；以及 `events_by_type<T>`，回傳所有已發出的 `T` 型別事件的 vector。

```move file=packages/samples/sources/programmability/events.move anchor=test

```

由於事件 struct 是模組內部的，放在同一模組（或同一 package 中具備適當存取函式的測試模組）中的測試可以直接檢查其欄位。

## 總結 (Summary) {#summary}

- 事件將應用程式定義的資料附加到交易結果上；它們會被鏈下索引，是通知外部世界鏈上活動的主要方式。
- 任何具有 `copy` 與 `drop` 的自訂型別都可以作為事件，但它必須是發出該事件模組的內部型別——這使得事件型別成為一個無法偽造的標籤。
- 事件的中繼資料已經包含寄件者、交易摘要以及時間戳記；事件欄位應攜帶與該動作相關的特定資料，例如物件 ID 與金額。
- 事件無法被 Move 程式碼讀回——它們是單向通道。
- 使用 `num_events` 與 `events_by_type<T>` 來測試已發出的事件。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::event][event-framework] 模組文件。
- Sui 文件中的[使用事件（Using Events）](https://docs.sui.io/guides/developer/sui-101/using-events)——在鏈下查詢與訂閱事件。

[event-framework]: https://docs.sui.io/references/framework/sui/event
