---
description: 在 Sui 上建置並發布待辦事項清單應用程式：建立帳戶、部署 Move 套件，並透過 CLI 傳送交易。
title: 你好，Sui！
keywords:
  - Move
  - Sui
  - Move tutorial
  - hello
  - sui
questions:
  - How do I create an object in Move?
  - How do I deploy Move to Sui?
  - What is Hello Sui?
answer: Hello Sui extends Hello World by creating a Sui object with a UID, transferring it to the sender, and publishing the package to the blockchain.
goal:
  description: Reader can write a Move module that creates and transfers an object on Sui
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

# 哈囉，Sui！ (Hello, Sui!) {#hello-sui}

在[上一節](./hello-world)中，我們建立了一個新的套件，並示範了建立、建置及測試 Move 套件的基本流程。本節將撰寫一個使用儲存模型且可與之互動的簡單應用程式。為此，我們將建立一個簡單的待辦事項清單應用程式。

## 建立新的套件 (Create a New Package) {#create-a-new-package}

依照與 [Hello, World!](./hello-world) 相同的流程，我們將建立一個名為
`todo_list` 的新套件。

```bash
$ sui move new todo_list
```

## 新增程式碼 (Add the Code) {#add-the-code}

為了加快進度並專注於應用程式邏輯，我們將提供待辦清單應用程式的程式碼。請以下列程式碼取代 _sources/todo_list.move_ 檔案的內容：

> 注意：雖然一開始內容可能令人不知所措，但我們將在接下來的章節逐步拆解。現在請嘗試專注於眼前的內容。

```move file=packages/todo_list/sources/todo_list.move anchor=all

```

## 建置套件 (Build the Package) {#build-the-package}

為了確認我們已正確完成所有步驟，請執行 `sui move build` 指令來建置套件。如果一切正確，你應該會看到類似以下的輸出：

```bash
$ sui move build
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING todo_list
```

如果此輸出後沒有出現錯誤，表示你已成功建置套件。如果出現錯誤，請確認：

- 原始碼是否已正確複製
- 文件名稱與套件名稱是否正確

在這個階段，原始碼失敗的原因通常不多。但如果你仍遇到問題，請嘗試查看[此處](https://github.com/MystenLabs/move-book/tree/main/packages/todo_list)的套件結構。

## 設定帳戶 (Set Up an Account) {#set-up-an-account}

> 如果你已設定帳戶，可以略過此步驟。

若要發布並與套件互動，我們需要設定帳戶。在開發期間，最佳選項是執行自己的
[本機網路](https://docs.sui.io/guides/developer/getting-started/local-network)。目前你只
需要執行 `RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis`。Sui
本機網路會在你機器的連接埠 9000 上執行，因此請確認沒有其他應用程式正在使用該連接埠。

如果你是第一次進行此操作，則需要建立新帳戶。為此，請執行
`sui client` 指令，接著 CLI 會向你提出多個問題。答案會在下方以 `>` 標示：

```bash
$ sui client
Config file ["/path/to/home/.sui/sui_config/client.yaml"] doesn't exist, do you want to connect to a Sui Full node server [y/N]?
> y
Sui Full node server URL (Defaults to Sui Testnet if not specified) :
> http://127.0.0.1:9000
Environment alias for [http://127.0.0.1:9000] :
> localnet
Select key scheme to generate keypair (0 for ed25519, 1 for secp256k1, 2: for secp256r1):
> 0
```

回答問題後，CLI 會產生新的金鑰對，並將其儲存至設定文件。你現在可以使用此帳戶與網路互動。

若要確認帳戶是否已正確設定，請執行 `sui client active-address` 指令：

```bash
$ sui client active-address
0x....
```

此指令會輸出你帳戶的地址；它以 `0x` 開頭，後面接著 64 個字元。

## 請求代幣 (Requesting Coins) {#requesting-coins}

在 _devnet_ 與 _testnet_ 環境中，CLI 提供了向你的帳戶請求代幣的方法，讓你可以與網路互動。若要請求代幣，請執行 `sui client faucet` 指令：

```bash
$ sui client faucet
Request successful. It can take up to 1 minute to get the coin. Run sui client gas to check your gas coins.
```

稍候片刻後，你可以執行 `sui client balance` 指令，確認 Coin 物件已傳送至你的帳戶：

```bash
$ sui client balance
╭────────────────────────────────────────╮
│ Balance of coins owned by this address │
├────────────────────────────────────────┤
│ ╭──────────────────────────────────╮   │
│ │ coin  balance (raw)  balance     │   │
│ ├──────────────────────────────────┤   │
│ │ Sui   1000000000    1.00 SUI     │   │
│ ╰──────────────────────────────────╯   │
╰────────────────────────────────────────╯
```

或者，你可以執行 `sui client objects` 指令，查詢你的帳戶所擁有的 _物件_。實際輸出會有所不同，因為物件 ID 與摘要皆為唯一值，但結構會相似：

```bash
$ sui client objects
╭───────────────────────────────────────────────────────────────────────────────────────╮
│ ╭────────────┬──────────────────────────────────────────────────────────────────────╮ │
│ │ objectId   │  0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de  │ │
│ │ version    │  4                                                                   │ │
│ │ digest     │  nA68oa8gab/CdIRw+240wze8u0P+sRe4vcisbENcR4U=                        │ │
│ │ objectType │  0x0000..0002::coin::Coin                                            │ │
│ ╰────────────┴──────────────────────────────────────────────────────────────────────╯ │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

現在帳戶已設定完成，且帳戶中已有代幣，我們便可以與網路互動。我們將先把套件發布至網路。

## 發布 (Publish) {#publish}

若要將套件發布至網路，我們將使用 `sui client publish` 指令。此指令會自動建置套件，並在單筆交易中使用其位元組碼進行發布。

> 我們會在發布時使用 `--gas-budget` 引數。它指定我們願意為此交易花費多少 gas。本節不會深入探討此主題，但請務必知道，Sui 中的每筆交易都需要支付 gas，且 gas 以 SUI Coin 支付。
> 值得注意的是，`--gas-budget` 並非必要參數。未設定時，會有預設的消耗上限。

`gas-budget` 以 _MIST_ 指定。1 SUI 等於 10^9 MIST。為了示範，我們將使用 100,000,000 MIST，也就是 0.1 SUI。

```bash
# 從 `todo_list` 資料夾執行此指令
$ sui client publish --gas-budget 100000000

# 或者，你可以指定套件的路徑
$ sui client publish --gas-budget 100000000 todo_list
```

發布指令的輸出相當冗長，因此我們會分段顯示並說明。

```bash
$ sui client publish --gas-budget 100000000
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING todo_list
Successfully verified dependencies onchain against source.
Transaction Digest: GpcDV6JjjGQMRwHpEz582qsd5MpCYgSwrDAq1JXcpFjW
```

如你所見，執行 `publish` 指令時，CLI 會先建置套件，接著在鏈上驗證依賴項，最後發布套件。此指令的輸出為交易摘要，這是交易的唯一識別碼，可用來查詢交易狀態。

### 交易資料 (Transaction Data) {#transaction-data}

標題為 `TransactionData` 的區段包含我們剛送出的交易資訊。其包含 `sender` 等欄位，亦即你的地址、透過 `--gas-budget` 引數設定的 `gas_budget`，以及我們用於付款的 Coin。它也會列印由 CLI 執行的 Commands。在此範例中，執行了 `Publish` 與 `TransferObject` 指令；後者會將特殊物件 `UpgradeCap` 轉移給傳送者。

```table
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Transaction Data                                                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                               │
│ Gas Owner: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                            │
│ Gas Budget: 100000000 MIST                                                                               │
│ Gas Price: 1000 MIST                                                                                     │
│ Gas Payment:                                                                                             │
│  ┌──                                                                                                     │
│  │ ID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                                │
│  │ Version: 7                                                                                            │
│  │ Digest: AXYPnups8A5J6pkvLa6RekX2ye3qur66EZ88mEbaUDQ1                                                  │
│  └──                                                                                                     │
│                                                                                                          │
│ Transaction Kind: Programmable                                                                           │
│ ╭────────────────────────────────────────────────────────────────────────────────────────────────╮       │
│ │ Commands                                                                                       │       │
│ ├────────────────────────────────────────────────────────────────────────────────────────────────┤       │
│ │ 0  Publish:                                                                                    │       │
│ │  ┌                                                                                             │       │
│ │  │ Dependencies:                                                                               │       │
│ │  │   0x0000000000000000000000000000000000000000000000000000000000000001                        │       │
│ │  │   0x0000000000000000000000000000000000000000000000000000000000000002                        │       │
│ │  └                                                                                             │       │
│ │                                                                                                │       │
│ │ 1  TransferObjects:                                                                            │       │
│ │  ┌                                                                                             │       │
│ │  │ Arguments:                                                                                  │       │
│ │  │   Result 0                                                                                  │       │
│ │  │ Address: Input  0                                                                           │       │
│ │  └                                                                                             │       │
│ ╰────────────────────────────────────────────────────────────────────────────────────────────────╯       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 交易效果 (Transaction Effects) {#transaction-effects}

交易效果包含交易狀態、交易對網路狀態所做的變更，以及交易涉及的物件。

```table
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Transaction Effects                                                                               │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Digest: GpcDV6JjjGQMRwHpEz582qsd5MpCYgSwrDAq1JXcpFjW                                              │
│ Status: Success                                                                                   │
│ Executed Epoch: 411                                                                               │
│                                                                                                   │
│ Created Objects:                                                                                  │
│  ┌──                                                                                              │
│  │ ID: 0x160f7856e13b27e5a025112f361370f4efc2c2659cb0023f1e99a8a84d1652f3                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 8                                                                                     │
│  │ Digest: 8y6bhwvQrGJHDckUZmj2HDAjfkyVqHohhvY1Fvzyj7ec                                           │
│  └──                                                                                              │
│  ┌──                                                                                              │
│  │ ID: 0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe                         │
│  │ Owner: Immutable                                                                               │
│  │ Version: 1                                                                                     │
│  │ Digest: Ein91NF2hc3qC4XYoMUFMfin9U23xQmDAdEMSHLae7MK                                           │
│  └──                                                                                              │
│ Mutated Objects:                                                                                  │
│  ┌──                                                                                              │
│  │ ID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 8                                                                                     │
│  │ Digest: 7ydahjaM47Gyb33PB4qnW2ZAGqZvDuWScV6sWPiv7LTc                                           │
│  └──                                                                                              │
│ Gas Object:                                                                                       │  ┌──                                                                                              │
│  │ ID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 8                                                                                     │
│  │ Digest: 7ydahjaM47Gyb33PB4qnW2ZAGqZvDuWScV6sWPiv7LTc                                           │
│  └──                                                                                              │
│ Gas Cost Summary:                                                                                 │
│    Storage Cost: 10404400 MIST                                                                    │
│    Computation Cost: 1000000 MIST                                                                 │
│    Storage Rebate: 978120 MIST                                                                    │
│    Non-refundable Storage Fee: 9880 MIST │                                                                                                   │
│ Transaction Dependencies:                                                                         │
│    7Ukrc5GqdFqTA41wvWgreCdHn2vRLfgQ3YMFkdks72Vk                                                   │
│    7d4amuHGhjtYKujEs9YkJARzNEn4mRbWWv3fn4cdKdyh                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 事件 (Events) {#events}

若有發出任何 _events_，你會在此區段看到它們。我們的套件未使用事件，因此此區段為空。

```table
╭─────────────────────────────╮
│ No transaction block events │
╰─────────────────────────────╯
```

### 物件變更 (Object Changes) {#object-changes}

這些是交易對 _objects_ 所做的變更。在我們的案例中，我們 _建立_ 了一個新的 `UpgradeCap` 物件，這是一種特殊物件，讓傳送者可以在未來升級套件；也 _變更_ 了 Gas 物件，並 _發布_ 了新套件。套件在 Sui 上也是物件。

```table
╭──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Object Changes                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Created Objects:                                                                                 │
│  ┌──                                                                                             │
│  │ ObjectID: 0x160f7856e13b27e5a025112f361370f4efc2c2659cb0023f1e99a8a84d1652f3                  │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                    │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 ) │
│  │ ObjectType: 0x2::package::UpgradeCap                                                          │
│  │ Version: 8                                                                                    │
│  │ Digest: 8y6bhwvQrGJHDckUZmj2HDAjfkyVqHohhvY1Fvzyj7ec                                          │
│  └──                                                                                             │
│ Mutated Objects:                                                                                 │
│  ┌──                                                                                             │
│  │ ObjectID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                  │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                    │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 ) │
│  │ ObjectType: 0x2::coin::Coin<0x2::sui::SUI>                                                    │
│  │ Version: 8                                                                                    │
│  │ Digest: 7ydahjaM47Gyb33PB4qnW2ZAGqZvDuWScV6sWPiv7LTc                                          │
│  └──                                                                                             │
│ Published Objects:                                                                               │
│  ┌──                                                                                             │
│  │ PackageID: 0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe                 │
│  │ Version: 1                                                                                    │
│  │ Digest: Ein91NF2hc3qC4XYoMUFMfin9U23xQmDAdEMSHLae7MK                                          │
│  │ Modules: todo_list                                                                            │
│  └──                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 餘額變更 (Balance Changes) {#balance-changes}

最後一個區段包含 SUI Coins 的變更。在我們的案例中，我們 _花費_ 了約 0.015 SUI，換算為 MIST 為 10,500,000。你可以在輸出的 _amount_ 欄位下看到它。

```table
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Balance Changes                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌──                                                                                              │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ CoinType: 0x2::sui::SUI                                                                        │
│  │ Amount: -10426280                                                                              │
│  └──                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 替代輸出格式 (Alternative Output) {#alternative-output}

你可以在發布時指定 `--json` 旗標，以取得 JSON 格式的輸出。若你想要以程式方式剖析輸出，或將其儲存供日後使用，這會很有用。

```bash
$ sui client publish --gas-budget 100000000 --json
```

### 使用結果 (Using the Results) {#using-the-results}

套件在鏈上發布後，我們便可與其互動。為此，我們需要找到套件的地址（物件 ID）。它位於 `Object Changes` 輸出的 `Published Objects` 區段中。每個套件的地址皆不相同，因此你需要從輸出中複製它。

在此範例中，地址為：

```table
0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
```

現在我們已有地址，可以與套件互動。下一節將示範如何透過傳送交易與套件互動。

## 傳送交易 (Sending Transactions) {#sending-transactions}

為了示範與 `todo_list` 套件的互動，我們將傳送一筆交易來建立新的清單並在其中新增項目。交易是透過 `sui client ptb` 指令傳送，它能完整運用[交易區塊](./../concepts/what-is-a-transaction)。這個指令看起來可能很長且複雜，但我們會逐步說明。

### 準備變數 (Prepare the Variables) {#prepare-the-variables}

在建構指令前，先儲存將在交易中使用的值。請將 `0x4....` 替換成你已發佈套件的地址。而 `MY_ADDRESS` 變數會從 CLI 輸出中自動設為你的地址。

```bash
$ export PACKAGE_ID=0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
$ export MY_ADDRESS=$(sui client active-address)
```

### 在 CLI 中建構交易 (Building the Transaction in CLI) {#building-the-transaction-in-cli}

現在來建構實際的交易。此交易會由兩部分組成：我們將呼叫 `todo_list` 套件中的 `new` 函式來建立新清單，接著將清單物件轉移至我們的帳戶。交易如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--assign sender @$MY_ADDRESS \
--move-call $PACKAGE_ID::todo_list::new \
--assign list \
--transfer-objects "[list]" sender
```

在這個指令中，我們使用 `ptb` 子指令建構交易。其後的參數定義交易將執行的實際指令與動作。前兩個呼叫是工具呼叫，用於將傳送者地址設為指令輸入，並設定交易的 gas 預算。

```bash
# 設定交易的 gas 預算
--gas-budget 100000000 \n
# 登錄變數 "sender=@..."
--assign sender @$MY_ADDRESS \n
```

接著，我們實際呼叫套件中的函式。我們使用 `--move-call`，後面接套件 ID、模組名稱與函式名稱。在此例中，我們呼叫 `todo_list` 套件中的 `new` 函式。

```bash
# 呼叫位於 $PACKAGE_ID 地址之下「todo_list」套件中的「new」函式
--move-call $PACKAGE_ID::todo_list::new
```

我們定義的函式實際上會回傳一個值，而我們希望將其儲存。我們使用 `--assign` 指令為回傳值命名。在此例中，命名為 `list`。接著，我們將物件轉移至帳戶。

```bash
--move-call $PACKAGE_ID::todo_list::new \
# 將「new」函式的結果指派給「list」變數（來自前一步）
--assign list \
# 將物件轉移給傳送者
--transfer-objects "[list]" sender
```

建構好指令後，你可以在終端機中執行它。若一切正確，應會看到與前幾節類似的輸出。輸出將包含交易摘要、交易資料，以及交易效果。

我們要關注的區段是「Object Changes」。更明確地說，是其中的「Created Objects」部分。它包含你所建立之 `TodoList` 的物件 ID、型別與版本。我們將使用此物件 ID 與清單互動。

```bash
╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Object Changes                                                                                        │
├───────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Created Objects:                                                                                      │
│  ┌──                                                                                                  │
│  │ ObjectID: 0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553                       │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )      │
│  │ ObjectType: 0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList  │
│  │ Version: 22                                                                                        │
│  │ Digest: HyWdUpjuhjLY38dLpg6KPHQ3bt4BqQAbdF5gB8HQdEqG                                               │
│  └──                                                                                                  │
│ Mutated Objects:                                                                                      │
│  ┌──                                                                                                  │
│  │ ObjectID: 0xe5ddeb874a8d7ead328e9f2dd2ad8d25383ab40781a5f1aefa75600973b02bc4                       │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )      │
│  │ ObjectType: 0x2::coin::Coin<0x2::sui::SUI>                                                         │
│  │ Version: 22                                                                                        │
│  │ Digest: DiBrBMshDiD9cThpaEgpcYSF76uV4hCoE1qRyQ3rnYCB                                               │  └──                                                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

在此範例中，物件 ID 是
`0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553`。而擁有者應為你的帳戶地址。我們透過交易最後一個指令將物件轉移給傳送者來達成此結果。

另一種測試是否已成功建立清單的方法，是查看帳戶物件。

```bash
$ sui client objects
```

其中應有一個看起來類似以下內容的物件：

```table
╭  ...                                                                                  ╮
│ ╭────────────┬──────────────────────────────────────────────────────────────────────╮ │
│ │ objectId   │  0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553  │ │
│ │ version    │  22                                                                  │ │
│ │ digest     │  /DUEiCLkaNSgzpZSq2vSV0auQQEQhyH9occq9grMBZM=                        │ │
│ │ objectType │  0x468d..29fe::todo_list::TodoList                                   │ │
│ ╰────────────┴──────────────────────────────────────────────────────────────────────╯ │
|  ...                                                                                  |
```

### 將物件傳遞給函式 (Passing Objects to Functions) {#passing-objects-to-functions}

我們在前一步建立的 TodoList 是一個物件，身為擁有者的你可以與它互動。你可以在此物件上呼叫 `todo_list` 模組中定義的函式。為了示範這點，我們將在清單中新增項目。首先只新增一個項目，接著在第二筆交易中新增 3 個項目並移除另一個項目。

請再次確認你已[依照前一步](#prepare-the-variables)設定變數，然後再為清單物件新增一個變數。

```bash
$ export LIST_ID=0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553
```

現在我們可以建構交易，將項目新增至清單。指令如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish the Hello, Sui chapter'"
```

在此指令中，我們呼叫 `todo_list` 套件中的 `add` 函式。此函式接受兩個引數：清單物件與要新增的項目。該項目是一個字串，因此我們需要以單引號包住它。此指令會將項目新增至清單。

若一切正確，應會看到與前幾節類似的輸出。現在你可以檢查清單物件，確認項目是否已新增。

```bash
$ sui client object $LIST_ID
```

輸出應包含你新增的項目。物件中的 `items` 欄位會顯示項目清單。加入 `--json` 旗標即可取得物件的 JSON 表示法：

```bash
$ sui client object $LIST_ID --json
```

```json
{
  "objectId": "0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553",
  "version": "24",
  "digest": "FGcXH8MGpMs5BdTnC62CQ3VLAwwexYg2id5DKU7Jr9aQ",
  "type": "0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList",
  "owner": {
    "AddressOwner": "0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1"
  },
  "previousTransaction": "EJVK6FEHtfTdCuGkNsU1HcrmUBEN6H6jshfcptnw8Yt1",
  "storageRebate": "1558000",
  "content": {
    "dataType": "moveObject",
    "type": "0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList",
    "hasPublicTransfer": true,
    "fields": {
      "id": {
        "id": "0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553"
      },
      "items": ["Finish the Hello, Sui chapter"]
    }
  }
}
```

### 串連指令 (Chaining Commands) {#chaining-commands}

你可以在單一交易中串連多個指令。這展現了交易區塊的強大能力！我們將使用同一個清單物件，再新增三個項目並移除一個項目。指令如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish Concepts chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Read the Move Basics chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Learn about Object Model'" \
--move-call $PACKAGE_ID::todo_list::remove @$LIST_ID 0
```

若前面的指令已成功執行，這個指令也應沒有差異。你可以檢查清單物件，確認項目是否已新增與移除。JSON 表示法更容易閱讀！

```bash
sui client object $LIST_ID --json
```

```json
{
  "objectId": "0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553",
  "version": "25",
  "digest": "EDTXDsteqPGAGu4zFAj5bbQGTkucWk4hhuUquk39enGA",
  "type": "0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList",
  "owner": {
    "AddressOwner": "0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1"
  },
  "previousTransaction": "7SXLGBSh31jv8G7okQ9mEgnw5MnTfvzzHEHpWf3Sa9gY",
  "storageRebate": "1922800",
  "content": {
    "dataType": "moveObject",
    "type": "0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList",
    "hasPublicTransfer": true,
    "fields": {
      "id": {
        "id": "0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553"
      },
      "items": [
        "Finish Concepts chapter",
        "Read the Move Basics chapter",
        "Learn about Object Model"
      ]
    }
  }
}
```

指令不必位於同一個套件，也不必操作同一個物件。在單一交易區塊中，你可以與多個套件和物件互動。這是一項強大功能，讓你能在鏈上建構複雜的互動！

## 結論 (Conclusion) {#conclusion}

在本指南中，我們說明了如何在 Move 區塊鏈上發布套件，以及如何使用 Sui CLI 與其互動。我們示範了如何建立新的清單物件、向其中新增項目，以及移除項目。我們也說明了如何在單一交易區塊中串接多個命令。本指南應能為你在 Sui 區塊鏈上建置自己的應用程式提供良好的起點！
