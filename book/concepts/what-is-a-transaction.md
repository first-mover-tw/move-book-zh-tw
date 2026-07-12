---
description: 了解如何 Sui 交易運作：結構、指令、gas 支付方式，以及如何透過 Move 函式呼叫改變區塊鏈狀態。
---

# Transaction 交易 (Transaction) {#transaction}

交易是與區塊鏈互動的基本方式。交易用於改變區塊鏈的狀態，而且是唯一能做到這件事的方式。在 Sui 上，一筆交易可以呼叫已發布套件中的函式、部署新套件，以及升級現有套件。

## 交易結構 (Transaction Structure) {#transaction-structure}

> 每筆交易都明確指定它所操作的物件！

交易由以下組成：

- 一個 sender —— _簽署_該交易的[帳戶](./what-is-an-account)；
- 一系列（或一串）指令 —— 要執行的操作；
- 指令輸入 —— 指令的引數：可以是 `pure` —— 像數字或字串這類簡單值，或是 `object` —— 該交易將存取的物件；
- 一個 gas 物件 —— 用於支付交易費用的 `Coin` 物件；
- gas 價格與預算 —— 交易的成本。

## 輸入 (Inputs) {#inputs}

交易輸入是交易的引數，分為兩種類型：

- Pure 引數：這些大多是[基本型別](../move-basics/primitive-types)，並附帶一些額外的補充。一個 pure 引數可以是：
  - [`bool`](../move-basics/primitive-types#booleans)。
  - [無號整數](../move-basics/primitive-types#integer-types)（`u8`、`u16`、`u32`、`u64`、`u128`、`u256`）。
  - [`address`](../move-basics/address)。
  - [`std::string::String`](../move-basics/string)，UTF8 字串。
  - [`std::ascii::String`](../move-basics/string#ascii-strings)，ASCII 字串。
  - [`vector<T>`](../move-basics/vector)，其中 `T` 為 pure 型別。
  - [`std::option::Option<T>`](../move-basics/option)，其中 `T` 為 pure 型別。
  - [`sui::object::ID`](../storage/uid-and-id)，通常指向一個物件。另見
    [What is an Object](../object/object-model)。
- Object 引數：這些是交易將存取的物件或物件參考。要讓交易成功，object 引數必須是共享物件、凍結物件，或是交易 sender 所擁有的物件。詳見
  [Object Model](../object)。

## 指令 (Commands) {#commands}

Sui 交易可能由多個指令組成。每個指令要麼是單一內建指令（例如發布套件），要麼是呼叫已發布套件中的函式。這些指令會依照在交易中列出的順序執行，並且可以使用前面指令的結果，形成一條鏈。交易要麼整體成功，要麼整體失敗。

任何 [`public`](../move-basics/visibility#public-visibility) 函式都可以作為指令被呼叫：把函式設為 `public` 就足以讓使用者在交易中呼叫它，這也是在 Move 中公開功能的預設方式。（另外還有
[`entry`](../move-basics/visibility#entry-modifier) 修飾詞，它建立的函式*只能*作為交易指令被呼叫——這是一個刻意受限的選項，會在
[Entry Functions](../move-advanced/entry-functions) 章節中介紹。）

以示意圖表示，一筆交易大致如下（以虛擬程式碼表示）：

```
Inputs:
- sender = 0xa11ce

Commands:
- payment = SplitCoins(Gas, [ 1000 ])
- item = MoveCall(0xAAA::market::purchase, [ payment ])
- TransferObjects(item, sender)
```

在這個範例中，交易由三個指令組成：

1. `SplitCoins` —— 一個內建指令，從傳入的物件（在此例中為 `Gas` 物件）分割出一個新的 coin；
2. `MoveCall` —— 一個指令，使用給定的引數（`payment` 物件）呼叫套件 `0xAAA` 中模組 `market` 的函式 `purchase`；
3. `TransferObjects` —— 一個內建指令，將物件轉移給接收者。

## 交易效果 (Transaction Effects) {#transaction-effects}

交易效果是指一筆交易對區塊鏈狀態所做的改變。更具體地說，交易可以透過以下方式改變狀態：

- 使用 gas 物件支付交易費用；
- 建立、更新或刪除物件；
- 發出事件；

已執行交易的結果由不同部分組成：

- Transaction Digest —— 用來識別該交易的雜湊值；
- Transaction Data —— 交易中使用的輸入、指令與 gas 物件；
- Transaction Effects —— 交易的狀態與「效果」，更具體地說：交易的狀態、物件的更新與其新版本、所使用的 gas 物件、交易的 gas 成本，以及交易所發出的事件；
- Events —— 交易所發出的自訂[事件](./../programmability/events)；
- Object Changes —— 對物件所做的變更，包括*所有權的變更*；
- Balance Changes —— 對參與交易的帳戶總餘額所做的變更。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的[Transactions](https://docs.sui.io/concepts/transactions)。
- Sui 文件中的[Programmable Transaction Blocks](https://docs.sui.io/concepts/transactions/prog-txn-blocks)。
- Sui 文件中的[Using Address Balances](https://docs.sui.io/onchain-finance/asset-custody/address-balances/using-address-balances) —— 在沒有 `Coin` 物件的情況下支付 gas 與轉移資金。
