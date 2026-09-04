---
description: Move 中的熱馬鈴薯模式 (Hot Potato pattern)：不具任何能力 (abilities) 且必須在同一筆交易 (transaction) 中消耗的結構 (struct)，用以強制完成工作流程 (workflow)。
title: 模式：燙手山芋 (Hot Potato)
keywords:
  - Move
  - Sui
  - Move tutorial
  - pattern
  - hot
  - potato
  - design patterns
questions:
  - 'What is Pattern: Hot Potato in Move?'
  - 'How do I use Pattern: Hot Potato in Move?'
  - What is Defining a Hot Potato in Move?
  - What is Applications in Move?
answer: 'The Hot Potato pattern in Move: a struct with no abilities that must be consumed in the same transaction, enforcing workflow completion.'
goal:
  description: 'Reader understands the Hot Potato pattern in Move: a struct with no abilities that must be consumed in the same transaction, enforcing workflow completion'
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

# 模式：燙手山芋 (Pattern: Hot Potato) {#pattern-hot-potato}

能力系統中的一種特殊情況——不具任何能力的結構——稱為*燙手山芋*（hot potato）。它無法
被儲存（無論是作為[物件](./../storage/key-ability)，或是作為
[另一個結構中的欄位](./../storage/store-ability)）、無法被
[複製](./../move-basics/copy-ability)或[丟棄](./../move-basics/drop-ability)。因此，一旦
建立，就必須由其[模組妥善解構](./../move-basics/struct)，否則交易會因未使用且不具 drop 的值而中止。

> 如果你熟悉支援*回呼*（callback）的程式語言，可以將燙手山芋視為必須呼叫回呼函式的
> 義務。若未呼叫它，交易將會中止。

此名稱源自兒童遊戲：玩家之間快速傳遞一顆球，而當音樂停止時，沒有任何玩家
想成為最後持有它的人，否則便會出局。這是此模式最貼切的說明——燙手山芋結構的
執行個體會在呼叫之間傳遞，且沒有任何模組可以保留它。

## 定義燙手山芋 (Defining a Hot Potato) {#defining-a-hot-potato}

燙手山芋可以是任何不具能力的結構。例如，下列結構就是燙手山芋：

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=definition

```

由於 `Request` 不具任何能力，且無法被儲存或忽略，模組必須提供一個
函式來解構它。例如：

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=new_request

```

## 使用範例 (Example Usage) {#example-usage}

在下列範例中，`Promise` 燙手山芋用於確保從容器取出的借用值會被歸還
至其中。`Promise` 結構包含借用物件的 ID 與容器的 ID，
確保借用值未被替換為其他值，並且會被歸還至正確的容器。

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=container_borrow

```

## 應用情境 (Applications) {#applications}

以下列出燙手山芋模式的一些常見使用情境。

### 借用 (Borrowing) {#borrowing}

如[上述範例](#example-usage)所示，燙手山芋非常適合用於借用，並能保證
借用值會歸還至正確的容器。雖然範例著重於儲存在 `Option` 內的值，
相同模式也可套用至任何其他儲存類型，例如
[動態欄位](./dynamic-fields)。

### 閃電貸款 (Flash Loans) {#flash-loans}

燙手山芋模式的典型範例是閃電貸款——在同一筆交易中借入並償還的
貸款。借入的資金可用於執行某些操作，償還的資金則會歸還給放款人。
燙手山芋模式可確保借入資金會歸還給放款人。

此模式的使用範例可能如下：

```move
// 從放款人借入資金；`potato` 使我們必須償還。
let (funds, potato) = lender.borrow(amount);

// 使用借入資金執行一些操作。
let asset = dex.trade(funds);
let proceeds = another_contract::do_something(asset);

// 償還貸款並保留利潤。
let payback = proceeds.split(amount, ctx);
lender.repay(payback, potato);
transfer::public_transfer(proceeds, ctx.sender());
```

> 未處理的燙手山芋也會影響交易其餘部分允許執行的操作：與其
> 糾纏的值在燙手山芋被消耗之前，無法傳遞給非 `public` 的 `entry` 函式。
> 精確規則——包括一個完整的閃電貸款範例——請參閱
> [入口函式](./../move-advanced/entry-functions)。

### 可變路徑執行 (Variable-path Execution) {#variable-path-execution}

燙手山芋模式可用於在執行路徑中引入變化。例如，若有一個模組允許使用
某些「Bonus Points」或 USD 購買 `Phone`，即可使用燙手山芋將購買與付款
解耦。此方法非常類似某些商店的運作方式——你從架上拿取商品，
接著前往收銀台付款。

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=phone_shop

```

這種解耦技術可將購買邏輯與付款邏輯分離，使原始碼更模組化且更容易維護。
`Ticket` 可拆分為獨立模組，為付款提供基本介面；商店實作也可擴充以支援其他
商品，而無須變更付款邏輯。

### 組合式模式 (Compositional Patterns) {#compositional-patterns}

燙手山芋可用於以組合方式串連不同模組。其模組可以定義與燙手山芋互動的方式，
例如為其蓋上型別簽章，或從中擷取某些資訊。如此一來，燙手山芋便可在不同模組之間
傳遞，甚至可在同一筆交易中的不同套件之間傳遞。

### 在 Sui Framework 中的使用 (Usage in the Sui Framework) {#usage-in-the-sui-framework}

此模式以多種形式用於 Sui Framework。以下是一些範例：

- [sui::borrow][borrow-framework] - 使用燙手山芋確保借用值會歸還至
  正確的容器。
- [sui::transfer_policy][transfer-policy-framework] - 定義 `TransferRequest`——一種燙手山芋，
  唯有滿足所有條件時才能被消耗。
- [sui::token][token-framework] - 在封閉迴圈代幣系統中，`ActionRequest` 攜帶
  已執行操作的資訊，並以類似 `TransferRequest` 的方式收集核准。
- [sui::package][package-framework] - 守護
  [套件升級](./package-upgrades)流程的 `UpgradeTicket` 與 `UpgradeReceipt`
  是燙手山芋：已授權的升級必須在同一筆交易中執行並提交。

[borrow-framework]: https://docs.sui.io/references/framework/sui/borrow
[package-framework]: https://docs.sui.io/references/framework/sui/package
[transfer-policy-framework]: https://docs.sui.io/references/framework/sui/transfer_policy
[token-framework]: https://docs.sui.io/references/framework/sui/token

## 總結 (Summary) {#summary}

- 燙手山芋是不具能力的結構；其模組必須提供建立與銷毀它的方法。
- 燙手山芋用於確保交易結束前會採取某項操作，類似回呼。
- 燙手山芋最常見的使用情境為借用、閃電貸款、可變路徑執行與組合式模式。

> 下一節介紹的 [Scratchpad](./scratchpad) 是另一種限於單一交易範圍內的
> 機制。兩者看似相似，但用途不同——請參閱該節結尾的比較。
