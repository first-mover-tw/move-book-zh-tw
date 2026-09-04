---
description: 在 Sui Move 中發出並測試事件：通知鏈下 (offchain) 監聽器智慧合約中的鏈上 (onchain) 活動。
title: 事件 (Events)
keywords:
  - Move
  - Sui
  - Move tutorial
  - events
questions:
  - What is Events in Move?
  - How do I use Events in Move?
  - What is Definition in Move?
  - What is Emitting Events in Move?
answer: 'Emit and test events in Sui Move: notify offchain listeners about onchain activity in your smart contracts.'
goal:
  description: 'Reader can emit and test events in Sui Move: notify offchain listeners about onchain activity in your smart contracts'
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

# 事件 (Events) {#events}

鏈上儲存會保留應用程式的*目前*狀態：物件、其欄位及其擁有者。但它不會保留導致此狀態的動作歷史。市集模組會儲存已上架的項目，但當項目售出且物件轉手後，鏈上便不會留下購買的痕跡——支付的價格、銷售時間或涉及的各方。儘管如此，應用程式通常正需要這些資訊：活動摘要、交易歷史或分析資料。

*事件*正是實現此目的的機制。事件是附加於成功交易結果的資料，並儲存在鏈下。發出事件不會修改任何物件，也不需支付儲存費；事件會由全節點建立索引，鏈下服務則可查詢或訂閱事件。事件是 Move 程式與外部世界溝通的主要方式。

## 定義 (Definition) {#definition}

事件會透過 [Sui Framework](./sui-framework) 的 [`sui::event`][event-framework] 模組中定義的 `emit` 函式發出：

```move
module sui::event;

/// 發出自訂 Move 事件，將資料傳送至鏈下。
///
/// 用於建立自訂索引，並以最適合特定應用程式的方式
/// 追蹤鏈上活動。
///
/// 型別 `T` 是為事件建立索引的主要方式，且可以包含
/// phantom 參數，例如 `emit(MyEvent<phantom T>)`。
public native fun emit<T: copy + drop>(event: T);
```

事件可以是任何具有 [copy](./../move-basics/copy-ability) 與
[drop](./../move-basics/drop-ability) 能力的自訂型別。此外，Sui Verifier 要求該型別必須
[為發出事件模組的*內部型別*](./../storage/internal-constraint)：不可能發出在其他模組中定義的型別；即使符合 `copy + drop` 要求，
[原始型別](./../move-basics/primitive-types)也無法發出。此規則使事件型別成為不可偽造的標籤——`ItemPurchased` 事件只能來自宣告它的模組。

## 發出事件 (Emitting Events) {#emitting-events}

若要發出事件，請為其定義一個 struct，並將該 struct 的執行個體傳入 `event::emit`。事件資料會以值傳遞，並作為交易結果的一部分傳送至鏈下：

```move file=packages/samples/sources/programmability/events.move anchor=emit

```

事件的型別是鏈下查詢的主要篩選條件——服務會透過指定型別來訂閱 `ItemPurchased` 事件。這引出一項簡單的設計原則：每項動作發出專用型別，並以發生的動作之過去式命名，例如 `ItemPurchased`、`AuctionStarted`、`ConfigUpdated`。事件內應包含索引器無須擷取其他資料即可理解該動作所需的值：涉及物件的 ID、數量及相關地址。

請注意，事件會附加至*成功*的交易：若交易在 `emit` 呼叫後中止，則不會記錄任何事件。

## 事件結構 (Event Structure) {#event-structure}

事件會成為*交易效果*的一部分，系統會將中繼資料附加至每個事件：

- _傳送者_——簽署交易的地址；
- _交易摘要_——將事件連結至發出它的交易；
- _時間戳記_——最終確認交易的檢查點時間，該交易的所有事件共用此時間；
- 事件的*型別簽章*，包含發出它的套件與模組。

由於中繼資料一定會包含傳送者與交易摘要，因此無須在事件欄位中重複這些資訊。事件 struct 中的 `sender: address` 欄位是多餘的，除非「邏輯上的」傳送者與交易簽署者不同（例如代表使用者執行的贊助交易）。

請務必理解，事件是單向通道。發出的事件不會儲存在鏈上，且 Move 程式碼無法讀回——無論在同一筆交易中，或在任何後續交易中皆然。若程式需要存取某個值，它應屬於物件；若需要讓外部世界看見，它應屬於事件。

## 測試事件 (Testing Events) {#testing-events}

由於事件是應用程式與其鏈下服務之間的介面，因此測試是否以正確值發出正確事件相當重要。`sui::event` 模組為此提供兩個僅限測試使用的函式：`num_events`，回傳目前測試中已發出的事件數量；以及 `events_by_type<T>`，回傳所有已發出的 `T` 型別事件之向量。

```move file=packages/samples/sources/programmability/events.move anchor=test

```

由於事件 struct 是模組內部型別，放置在相同模組中的測試（或具有適當存取子、位於相同套件之測試模組中的測試）可以直接檢查其欄位。

## 總結 (Summary) {#summary}

- 事件會將應用程式定義的資料附加至交易結果；它們會在鏈下建立索引，且是通知外部世界鏈上活動的主要方式。
- 任何具有 `copy` 與 `drop` 的自訂型別都可作為事件，但它必須是發出事件模組的內部型別——這使事件型別成為不可偽造的標籤。
- 事件中繼資料已包含傳送者、交易摘要與時間戳記；事件欄位應攜帶動作專屬資料，例如物件 ID 與數量。
- Move 程式碼無法讀回事件——它們是單向通道。
- 使用 `num_events` 與 `events_by_type<T>` 測試已發出的事件。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::event][event-framework] 模組文件。
- Sui 文件中的[使用事件](https://docs.sui.io/guides/developer/sui-101/using-events)——在鏈下查詢與訂閱事件。

[event-framework]: https://docs.sui.io/references/framework/sui/event
