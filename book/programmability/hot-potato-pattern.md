---
description: Hot Potato 模式 (Hot Potato Pattern)：Move 中一種沒有任何 abilities 的 struct，必須在同一筆交易中被消耗，藉此強制完成整個工作流程。
---

# Pattern：熱馬鈴薯 (Pattern: Hot Potato) {#pattern-hot-potato}

能力系統中的一個特殊情況——一個沒有任何能力的結構體——被稱為 _熱馬鈴薯 (hot potato)_。它不能被
[儲存](./../storage/key-ability)（不能作為[物件](./../storage/key-ability)，也不能作為
[另一個結構體中的欄位](./../storage/store-ability)），也不能被
[複製](./../move-basics/copy-ability) 或 [丟棄](./../move-basics/drop-ability)。因此，一旦被
建構出來，它必須被其模組[優雅地拆解](./../move-basics/struct)，否則
交易會因為存在未使用且沒有 drop 能力的值而中止。

> 如果你熟悉支援 _callback_ 的語言，可以把熱馬鈴薯想像成一個
> 必須呼叫回呼函式的義務。如果你不呼叫它，交易就會中止。

這個名稱來自兒童遊戲，遊戲中一顆球會在玩家之間快速傳遞，沒有人
想在音樂停止時還拿著球，否則就會出局。
這正是這個 pattern 的最佳寫照——熱馬鈴薯結構體的實例會在
呼叫之間傳遞，沒有任何模組可以把它留下來。

## 定義熱馬鈴薯 (Defining a Hot Potato) {#defining-a-hot-potato}

任何沒有能力的結構體都可以是熱馬鈴薯。例如，以下結構體就是一個熱馬鈴薯：

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=definition

```

因為 `Request` 沒有任何能力，不能被儲存或忽略，該模組必須提供一個
函式來拆解它。例如：

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=new_request

```

## 範例用法 (Example Usage) {#example-usage}

在以下範例中，`Promise` 熱馬鈴薯被用來確保借出的值在
從容器中取出後，會被歸還給該容器。`Promise` 結構體包含被
借出物件的 ID，以及容器的 ID，確保借出的值沒有被替換成
另一個，並且會被歸還到正確的容器。

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=container_borrow

```

## 應用場景 (Applications) {#applications}

以下我們列出一些熱馬鈴薯 pattern 的常見使用案例。

### 借用 (Borrowing) {#borrowing}

如[上方範例](#example-usage)所示，熱馬鈴薯對於借用非常有效，
可以保證借出的值會歸還到正確的容器。雖然該範例聚焦於
儲存在 `Option` 中的值，但同樣的 pattern 也可以套用到任何其他儲存型別，例如
[動態欄位](./dynamic-fields)。

### 閃電貸 (Flash Loans) {#flash-loans}

熱馬鈴薯 pattern 的經典範例就是閃電貸——一種在同一筆交易中
借出並償還的貸款。借出的資金被用來執行某些操作，
而償還的資金則歸還給放貸方。熱馬鈴薯 pattern 確保借出的資金
會歸還給放貸方。

這個 pattern 的範例用法可能像這樣：

```move
// 向放貸方借出資金；`potato` 讓我們有義務償還。
let (funds, potato) = lender.borrow(amount);

// 用借出的資金執行某些操作。
let asset = dex.trade(funds);
let proceeds = another_contract::do_something(asset);

// 償還貸款並保留利潤。
let payback = proceeds.split(amount, ctx);
lender.repay(payback, potato);
transfer::public_transfer(proceeds, ctx.sender());
```

> 一個尚未結清的熱馬鈴薯也會影響交易其餘部分被允許執行的操作：
> 與其糾纏在一起的值在熱馬鈴薯被消耗之前，不能傳遞給非 `public` 的
> `entry` 函式。詳細規則——連同一個完整的閃電貸範例——說明於
> [入口函式](./../move-advanced/entry-functions)。

### 可變路徑執行 (Variable-path Execution) {#variable-path-execution}

熱馬鈴薯 pattern 可以用來在執行路徑中引入變化。舉例來說，如果
有一個模組允許使用「紅利點數」或美金來購買 `Phone`，那麼熱
馬鈴薯可以用來將購買行為與付款行為解耦。這種做法與某些
商店的運作方式非常相似——你先從架上拿走商品，然後再去收銀台付款。

```move file=packages/samples/sources/programmability/hot-potato-pattern.move anchor=phone_shop

```

這種解耦技巧使得購買邏輯可以與付款邏輯分開，讓
程式碼更模組化、更易於維護。`Ticket` 可以被拆分成獨立的模組，
提供付款的基本介面，而商店的實作則可以擴充以支援其他
商品，而不需要更改付款邏輯。

### 組合式 Pattern (Compositional Patterns) {#compositional-patterns}

熱馬鈴薯可以用來以組合方式連結不同的模組。它的模組可以
定義與熱馬鈴薯互動的方式，例如，用一個型別簽章來標記它，或是從中
擷取某些資訊。透過這種方式，熱馬鈴薯可以在不同的模組之間傳遞，
甚至在同一筆交易中的不同套件之間傳遞。

### 在 Sui Framework 中的用法 (Usage in the Sui Framework) {#usage-in-the-sui-framework}

這個 pattern 以各種形式被用於 Sui Framework 中。以下是一些範例：

- [sui::borrow][borrow-framework]——使用熱馬鈴薯來確保借出的值會歸還到
  正確的容器。
- [sui::transfer_policy][transfer-policy-framework]——定義了 `TransferRequest`——一個
  只有在滿足所有條件時才能被消耗的熱馬鈴薯。
- [sui::token][token-framework]——在封閉迴圈代幣系統中，`ActionRequest` 攜帶
  關於已執行操作的資訊，並以類似 `TransferRequest` 的方式收集核准。
- [sui::package][package-framework]——守護
  [套件升級](./package-upgrades) 流程的 `UpgradeTicket` 和 `UpgradeReceipt` 都是熱馬鈴薯：
  一個經過授權的升級必須在同一筆交易中被執行並提交。

[borrow-framework]: https://docs.sui.io/references/framework/sui/borrow
[package-framework]: https://docs.sui.io/references/framework/sui/package
[transfer-policy-framework]: https://docs.sui.io/references/framework/sui/transfer_policy
[token-framework]: https://docs.sui.io/references/framework/sui/token

## 總結 (Summary) {#summary}

- 熱馬鈴薯是一個沒有能力的結構體；它的模組必須提供建立和銷毀它的方式。
- 熱馬鈴薯被用來確保某個動作在交易結束前被執行，類似於
  回呼函式。
- 熱馬鈴薯最常見的使用案例是借用、閃電貸、可變路徑執行，以及
  組合式 pattern。
