# 交易 (Transaction)

交易是區塊鏈世界中的一個基本概念。它是與區塊鏈互動的一種方式。交易用於更改區塊鏈的狀態，而且它們是執行此操作的唯一方式。在 Move 中，交易用於呼叫套件中的函式、部署新套件以及升級現有套件。

## 交易結構

> 每一筆交易都明確指定了它所操作的物件！

交易由以下部分組成：

- 發送者 (sender) —— 「簽署」交易的[帳戶](./what-is-an-account)；
- 命令列表（或鏈） —— 要執行的操作；
- 命令輸入 —— 命令的參數：可以是「純粹 (pure)」參數 —— 如數字或字串等簡單數值，或者是「物件 (object)」參數 —— 交易將訪問的物件；
- Gas 物件 —— 用於支付交易費用的 `Coin` 物件；
- Gas 價格和預算 (price and budget) —— 交易的成本；

## 輸入 (Inputs)

交易輸入是交易的參數，分為兩種類型：

- 純粹參數 (Pure arguments)：這些大多是[原始類型](../move-basics/primitive-types)以及一些額外補充。純粹參數可以是：
  - [`bool`](../move-basics/primitive-types#booleans)。
  - [無符號整數](../move-basics/primitive-types#integer-types) (`u8`、`u16`、`u32`、`u64`、`u128`、`u256`)。
  - [`address`](../move-basics/address)。
  - [`std::string::String`](../move-basics/string)，UTF8 字串。
  - [`std::ascii::String`](../move-basics/string#ascii-strings)，ASCII 字串。
  - [`vector<T>`](../move-basics/vector)，其中 `T` 是純粹類型。
  - [`std::option::Option<T>`](../move-basics/option)，其中 `T` 是純粹類型。
  - [`std::object::ID`](../storage/uid-and-id)，通常指向一個物件。另請參閱[什麼是物件](../object/object-model)。
- 物件參數 (Object arguments)：這些是交易將訪問的物件或物件參照。物件參數必須是共享物件、凍結物件或者是交易發送者擁有的物件，交易才能成功。更多資訊請參閱[物件模型](../object)。

## 命令 (Commands)

Sui 交易可能由多個命令組成。每個命令可以是一個內建命令（如發佈套件）或對已發佈套件中函式的呼叫。命令按照在交易中列出的順序執行，並且可以使用先前命令的結果來形成一個鏈。交易作為一個整體，要麼成功要麼失敗。

從圖解上看，一筆交易看起來像這樣（虛擬碼）：

```
Inputs:
- sender = 0xa11ce

Commands:
- payment = SplitCoins(Gas, [ 1000 ])
- item = MoveCall(0xAAA::market::purchase, [ payment ])
- TransferObjects(item, sender)
```

在這個範例中，交易由三個命令組成：

1. `SplitCoins` - 一個內建命令，從傳遞的物件（在此範例中為 `Gas` 物件）中拆分出一個新代幣；
2. `MoveCall` - 呼叫套件 `0xAAA`、模組 `market` 中 `purchase` 函式的命令，其參數為 `payment` 物件；
3. `TransferObjects` - 一個內建命令，將物件轉移給接收者。

## 交易效果 (Transaction Effects)

交易效果是交易對區塊鏈狀態所做的更改。更具體地說，交易可以透過以下方式更改狀態：

- 使用 Gas 物件支付交易費用；
- 建立、更新或刪除物件；
- 發出事件；

執行交易的結果由不同部分組成：

- 交易摘要 (Transaction Digest) —— 用於標識交易的交易哈希；
- 交易數據 (Transaction Data) —— 交易中使用的輸入、命令和 Gas 物件；
- 交易效果 (Transaction Effects) —— 交易的狀態和「效果」，更具體地說：交易的狀態、物件的更新及其新版本、使用的 Gas 物件、交易的 Gas 成本以及交易發出的事件；
- 事件 (Events) —— 交易發出的自定義[事件](./../programmability/events)；
- 物件變更 (Object Changes) —— 對物件所做的更改，包括「所有權變更 (change of ownership)」；
- 餘額變更 (Balance Changes) —— 交易涉及帳戶總餘額的變更；
