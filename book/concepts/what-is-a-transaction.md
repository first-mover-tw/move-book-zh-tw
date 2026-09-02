---
description: 學習 Sui 交易 (Sui transactions) 的運作方式：結構 (structure)、指令 (commands)、燃料費 (gas payments)，以及它們如何透過 Move 函式 (Move function) 呼叫 (calls) 改變區塊鏈狀態 (blockchain state)。
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

交易是與區塊鏈互動的基本方式。交易用於變更區塊鏈的狀態，並且是唯一能這樣做的方式。在 Sui 上，交易可以呼叫已發佈套件中的函式、部署新套件，以及升級現有套件。

## 交易結構 (Transaction Structure) {#transaction-structure}

> 每筆交易都會明確指定其操作的物件！

交易由以下部分組成：

- 傳送者 - _簽署_交易的[帳號](./what-is-an-account)；
- 指令列表（或鏈結）- 要執行的操作；
- 指令輸入 - 指令的引數：可以是 `pure` - 像數字或字串的簡單值，或是 `object` - 交易將會存取的物件；
- gas 物件 - 用於支付交易的 `Coin` 物件；
- gas 價格和預算 - 交易的成本。

## 輸入 (Inputs) {#inputs}

交易輸入是交易的引數，分為兩種型別：

- 純量引數：這些主要是[原生型別](../move-basics/primitive-types)，並有一些額外增加。純量引數可以是：
  - [`bool`](../move-basics/primitive-types#booleans)。
  - [無號整數](../move-basics/primitive-types#integer-types) (`u8`, `u16`, `u32`, `u64`, `u128`, `u256`)。
  - [`address`](../move-basics/address)。
  - [`std::string::String`](../move-basics/string)，UTF8 字串。
  - [`std::ascii::String`](../move-basics/string#ascii-strings)，ASCII 字串。
  - [`vector<T>`](../move-basics/vector)，其中 `T` 是純量型別。
  - [`std::option::Option<T>`](../move-basics/option)，其中 `T` 是純量型別。
  - [`sui::object::ID`](../storage/uid-and-id)，通常指向一個物件。另請參閱[什麼是物件](../object/object-model)。
- 物件引數：這些是交易將會存取的物件或物件的參考。物件引數必須是共享物件、凍結物件，或是交易傳送者擁有的物件，交易才能成功。更多資訊請參閱[物件模型](../object)。

## 指令 (Commands) {#commands}

Sui 交易可能由多個指令組成。每個指令都是一個單一的內建指令（例如發佈套件），或是呼叫已發佈套件中的函式。這些指令會依照在交易中列出的順序執行，並且可以使用先前指令的結果，形成一個鏈結。交易會整體成功或失敗。

任何[`public`](../move-basics/visibility#public-visibility)函式都可以作為指令呼叫：將函式設為 `public`，使用者就可以在交易中呼叫它，這是 Move 中公開功能性的預設方式。（還有[`entry`](../move-basics/visibility#entry-modifier)修飾符，它建立的函式_只能_作為交易指令呼叫——這是一個刻意限制的選項，在[進入點函式](../move-advanced/entry-functions)部分中介紹。）

示意上，交易看起來像這樣（以偽程式碼表示）：

```
Inputs:
- sender = 0xa11ce

Commands:
- payment = SplitCoins(Gas, [ 1000 ])
- item = MoveCall(0xAAA::market::purchase, [ payment ])
- TransferObjects(item, sender)
```

在這個範例中，交易包含三個指令：

1.  `SplitCoins` - 一個內建指令，從傳入的物件（在此範例中為 `Gas` 物件）中分割出一個新 `Coin`；
2.  `MoveCall` - 一個指令，以給定的引數（`payment` 物件）呼叫套件 `0xAAA`、模組 `market` 中的 `purchase` 函式；
3.  `TransferObjects` - 一個內建指令，將物件轉移給接收者。

## 交易影響 (Transaction Effects) {#transaction-effects}

交易影響是交易對區塊鏈狀態所做的變更。更具體地說，交易可以透過以下方式變更狀態：

- 使用 gas 物件支付交易；
- 建立、更新或刪除物件；
- 發出事件；

已執行交易的結果包含不同的部分：

- 交易摘要 (Transaction Digest) - 交易的雜湊值，用於識別交易；
- 交易資料 (Transaction Data) - 交易中使用的輸入、指令和 gas 物件；
- 交易影響 (Transaction Effects) - 交易的狀態和「影響」，更具體地說：交易的狀態、物件的更新及其新版本、使用的 gas 物件、交易的 gas 成本，以及交易發出的事件；
- 事件 (Events) - 交易發出的自訂[事件](./../programmability/events)；
- 物件變更 (Object Changes) - 對物件所做的變更，包括_所有權的變更_；
- 餘額變更 (Balance Changes) - 對交易中涉及帳號的總計餘額所做的變更。

## 延伸閱讀 (Further Reading) {#further-reading}

- [交易](https://docs.sui.io/concepts/transactions)，Sui 文件。
- [可程式化交易區塊](https://docs.sui.io/concepts/transactions/prog-txn-blocks)，Sui 文件。
- [使用地址餘額](https://docs.sui.io/onchain-finance/asset-custody/address-balances/using-address-balances)，Sui 文件 - 支付 gas 並轉移資金，無需 `Coin` 物件。
