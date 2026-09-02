---
description: 了解 Sui 交易的運作方式：結構、指令、gas 支付方式，以及如何透過 Move 函式呼叫改變區塊鏈狀態。
title: 交易 (Transaction)
keywords:
  - Move
  - Sui
  - Move tutorial
  - transaction
questions:
  - What is Transaction in Move?
  - How do I use Transaction in Move?
  - What is Transaction Structure in Move?
  - What is Inputs in Move?
answer: 'Learn how Sui transactions work: structure, commands, gas payments, and how they change blockchain state through Move function calls.'
goal:
  description: 'Reader understands how Sui transactions work: structure, commands, gas payments, and how they change blockchain state through Move function calls'
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

# 交易 (Transaction) {#transaction}

交易是與區塊鏈互動的基本方式。交易用於變更區塊鏈的狀態，並且是唯一能這樣做的方式。在 Sui 上，交易可以呼叫已發布套件中的函式、部署新套件，以及升級現有套件。

## 交易結構 (Transaction Structure) {#transaction-structure}

> 每筆交易都會明確指定其操作的物件！

交易由以下部分組成：

- 發送者 —— *簽署*該交易的[帳戶](./what-is-an-account)；
- 一系列（或一串）指令 —— 要執行的操作；
- 指令輸入 —— 指令的引數：可以是 `pure` —— 像數字或字串這類簡單值，或是 `object` —— 該交易將存取的物件；
- 一個 gas 物件 —— 用於支付交易費用的 `Coin` 物件；
- gas 價格與預算 —— 交易的成本。

## 輸入 (Inputs) {#inputs}

交易輸入是交易的引數，分為兩種型別：

- Pure 引數：這些大多是[基本型別](../move-basics/primitive-types)，並附帶一些額外的補充。一個 pure 引數可以是：
  - [`bool`](../move-basics/primitive-types#booleans)。
  - [無號整數](../move-basics/primitive-types#integer-types) (`u8`, `u16`, `u32`, `u64`, `u128`, `u256`)。
  - [`address`](../move-basics/address)。
  - [`std::string::String`](../move-basics/string)，UTF8 字串。
  - [`std::ascii::String`](../move-basics/string#ascii-strings)，ASCII 字串。
  - [`vector<T>`](../move-basics/vector)，其中 `T` 是純量型別。
  - [`std::option::Option<T>`](../move-basics/option)，其中 `T` 是純量型別。
  - [`sui::object::ID`](../storage/uid-and-id)，通常指向一個物件。另請參閱[什麼是物件](../object/object-model)。
- 物件引數：這些是交易將會存取的物件或物件的參考。物件引數必須是共享物件、凍結物件，或是交易發送者所擁有的物件，交易才能成功。更多資訊請參閱[物件模型](../object)。

## 指令 (Commands) {#commands}

Sui 交易可能由多個指令組成。每個指令都是一個單一的內建指令（例如發布套件），或是呼叫已發布套件中的函式。這些指令會依照在交易中列出的順序執行，並且可以使用先前指令的結果，形成一個鏈結。交易會整體成功或失敗。

任何 [`public`](../move-basics/visibility#public-visibility) 函式都可以作為指令呼叫：將函式設為 `public`，使用者就可以在交易中呼叫它，這是 Move 中公開功能性的預設方式。（另外還有 [`entry`](../move-basics/visibility#entry-modifier) 修飾詞，它建立的函式*只能*作為交易指令呼叫——這是一個刻意限制的選項，在[入口函式 (Entry Functions)](../move-advanced/entry-functions)章節中介紹。）

以示意圖表示，一筆交易大致如下（以虛擬程式碼表示）：

```
Inputs:
- sender = 0xa11ce

Commands:
- payment = SplitCoins(Gas, [ 1000 ])
- item = MoveCall(0xAAA::market::purchase, [ payment ])
- TransferObjects(item, sender)
```

在這個範例中，交易包含三個指令：

1. `SplitCoins` —— 一個內建指令，從傳入的物件（在此例中為 `Gas` 物件）分割出一個新的 `Coin`；
2. `MoveCall` —— 一個指令，使用給定的引數（`payment` 物件）呼叫套件 `0xAAA` 中模組 `market` 的函式 `purchase`；
3. `TransferObjects` —— 一個內建指令，將物件轉移給接收者。

## 交易效果 (Transaction Effects) {#transaction-effects}

交易效果是交易對區塊鏈狀態所做的變更。更具體地說，交易可以透過以下方式變更狀態：

- 使用 gas 物件支付交易費用；
- 建立、更新或刪除物件；
- 發出事件；

已執行交易的結果包含不同的部分：

- 交易摘要 (Transaction Digest) —— 交易的雜湊值，用於識別交易；
- 交易資料 (Transaction Data) —— 交易中使用的輸入、指令和 gas 物件；
- 交易效果 (Transaction Effects) —— 交易的狀態和「影響」，更具體地說：交易的狀態、物件的更新及其新版本、使用的 gas 物件、交易的 gas 成本，以及交易發出的事件；
- 事件 (Events) —— 交易發出的自訂[事件](./../programmability/events)；
- 物件變更 (Object Changes) —— 對物件所做的變更，包括*所有權的變更*；
- 餘額變更 (Balance Changes) —— 對交易中涉及帳戶的總計餘額所做的變更。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的 [交易 (Transactions)](https://docs.sui.io/concepts/transactions)。
- Sui 文件中的 [可程式化交易區塊 (Programmable Transaction Blocks)](https://docs.sui.io/concepts/transactions/prog-txn-blocks)。
- Sui 文件中的 [使用地址餘額 (Using Address Balances)](https://docs.sui.io/onchain-finance/asset-custody/address-balances/using-address-balances) —— 在沒有 `Coin` 物件的情況下支付 gas 與轉移資金。
