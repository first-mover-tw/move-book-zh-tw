---
description: 在 Sui 上建立並發布一個待辦事項清單應用程式：建立帳戶、部署 Move 套件，並透過 CLI 傳送交易
---

# Sui，你好！ (Hello, Sui!) {#hello-sui}

在[上一節](./hello-world)中，我們建立了一個新的套件，並示範了建立、建置與測試 Move 套件的基本流程。在本節中，我們將撰寫一個簡單的應用程式，使用儲存模型並可與之互動。為此，我們將建立一個簡單的待辦事項清單應用程式。

## 建立新套件 (Create a New Package) {#create-a-new-package}

依照與 [Hello, World!](./hello-world) 相同的流程，我們將建立一個名為
`todo_list` 的新套件。

```bash
$ sui move new todo_list
```

## 加入程式碼 (Add the Code) {#add-the-code}

為了加快進度並專注於應用程式邏輯，我們將提供待辦事項清單應用程式的程式碼。請將 _sources/todo_list.move_ 檔案的內容替換為以下程式碼：

> 注意：雖然一開始內容看起來可能令人不知所措，但我們會在接下來的章節中逐一拆解說明。請先專注在眼前的內容即可。

```move file=packages/todo_list/sources/todo_list.move anchor=all

```

## 建置套件 (Build the Package) {#build-the-package}

為了確保我們一切都做得正確，讓我們透過執行 `sui move build` 指令來建置套件。如果一切正確，你應該會看到類似以下的輸出：

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

如果在此輸出之後沒有出現任何錯誤，代表你已成功建置套件。如果出現錯誤，請確認：

- 程式碼是否正確複製
- 檔案名稱與套件名稱是否正確

在這個階段，程式碼失敗的原因不會有太多其他可能性。但如果你仍然遇到問題，可以嘗試在
[這個位置](https://github.com/MystenLabs/move-book/tree/main/packages/todo_list)查閱套件的結構。

## 設定帳戶 (Set Up an Account) {#set-up-an-account}

> 如果你已經設定好帳戶，可以跳過這個步驟。

為了發布並與套件互動，我們需要設定一個帳戶。在開發過程中，最好的方式是執行你自己的
[本地網路](https://docs.sui.io/guides/developer/getting-started/local-network)。現在你只需要執行
`RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis`。Sui
本地網路會在你機器的 9000 埠上執行，所以請確認這個埠沒有被其他應用程式佔用。

如果你是第一次執行，你需要建立一個新帳戶。請執行
`sui client` 指令，然後 CLI 會詢問你多個問題。答案標示在下方的 `>` 之後：

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

回答完問題後，CLI 會產生一組新的金鑰對並儲存到設定檔中。你現在可以使用這個帳戶與網路互動。

要確認我們的帳戶設定正確，請執行 `sui client active-address` 指令：

```bash
$ sui client active-address
0x....
```

這個指令會輸出你帳戶的地址，它以 `0x` 開頭，後面接著 64 個字元。

## 請求代幣 (Requesting Coins) {#requesting-coins}

在 _devnet_ 和 _testnet_ 環境中,CLI 提供了一種方式來請求代幣到你的帳戶,
讓你可以與網路互動。要請求代幣,執行 `sui client faucet` 指令:

```bash
$ sui client faucet
Request successful. It can take up to 1 minute to get the coin. Run sui client gas to check your gas coins.
```

稍等片刻後,你可以透過執行 `sui client balance` 指令,確認 Coin 物件已經
傳送到你的帳戶:

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

另外,你也可以透過執行 `sui client objects` 指令,查詢你帳戶擁有的 _objects_。
實際輸出會有所不同,因為物件 ID 是唯一的,digest 也是唯一的,但
結構會類似:

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

現在我們已經設定好帳戶並在帳戶中擁有代幣,我們可以與網路互動了。
我們將從發布套件到網路開始。

## Publish 發布 (Publish) {#publish}

要將套件發布到網路上,我們會使用 `sui client publish` 指令。此指令會自動建置套件,並使用其位元組碼在單一交易中發布。

> 我們在發布時使用了 `--gas-budget` 參數。它指定了我們願意在此交易上花費多少 gas。我們不會在本節深入探討這個主題,但重要的是要知道,Sui 上的每筆交易都需要花費 gas,而 gas 是以 SUI 幣支付的。
> 值得注意的是,`--gas-budget` 並非必要參數。當你不設定它時,會有一個預設的消耗上限。

`gas-budget` 是以 _MIST_ 為單位指定的。1 SUI 等於 10^9 MIST。為了示範,我們將使用 100,000,000 MIST,也就是 0.1 SUI。

```bash
# 從 `todo_list` 資料夾執行此指令
$ sui client publish --gas-budget 100000000

# 或者，你也可以指定套件的路徑
$ sui client publish --gas-budget 100000000 todo_list
```

publish 指令的輸出相當冗長,因此我們會分段展示並解說。

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

如你所見,當我們執行 `publish` 指令時,CLI 會先建置套件,接著在鏈上驗證相依套件,最後再發布套件。指令的輸出是交易摘要(transaction digest),它是該筆交易的唯一識別碼,可用來查詢交易狀態。

### 交易資料 (Transaction Data) {#transaction-data}

標題為 `TransactionData` 的區塊包含了我們剛送出的交易資訊。它包含了像是 `sender` 這樣的欄位,也就是你的地址、以 `--gas-budget` 參數設定的 `gas_budget`,以及我們用來支付的 Coin。它同時也印出了 CLI 所執行的 Commands。在此範例中,執行了 `Publish` 和 `TransferObject` 這兩個指令——後者將一個特殊物件 `UpgradeCap` 轉移給發送者。

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

Transaction Effects 包含了交易的狀態、該筆交易對網路狀態所做的變更,以及交易中涉及的物件。

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

如果有任何 _事件(events)_ 被發出,你會在這個區塊看到它們。我們的套件並未使用事件,因此該區塊是空的。

```table
╭─────────────────────────────╮
│ No transaction block events │
╰─────────────────────────────╯
```

### 物件變更 (Object Changes) {#object-changes}

這些是該筆交易對 _物件(objects)_ 所做的變更。在我們的例子中,我們 _建立_ 了一個新的 `UpgradeCap` 物件,這是一個允許發送者未來升級套件的特殊物件,_修改_ 了 Gas 物件,並 _發布_ 了一個新套件。套件在 Sui 上同樣也是物件。

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

最後這個區塊包含了 SUI 幣的變更,在我們的例子中,我們 _花費_ 了大約 0.015 SUI,換算成 MIST 是 10,500,000。你可以在輸出中的 _amount_ 欄位看到這個數字。

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

### 替代輸出 (Alternative Output) {#alternative-output}

在發布時可以指定 `--json` 旗標,以 JSON 格式取得輸出。如果你想以程式方式解析輸出或儲存以供之後使用,這會很有幫助。

```bash
$ sui client publish --gas-budget 100000000 --json
```

### 使用發布結果 (Using the Results) {#using-the-results}

套件在鏈上發布後,我們就可以與它互動了。要做到這點,我們需要找到套件的地址(物件 ID)。它位於 `Object Changes` 輸出的 `Published Objects` 區塊下。每個套件的地址都是唯一的,所以你需要從輸出中複製它。

在這個範例中,地址是:

```table
0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
```

現在我們有了地址,就可以與套件互動了。在下一節,我們會展示如何透過發送交易來與套件互動。

## 傳送交易 (Sending Transactions) {#sending-transactions}

為了示範與 `todo_list` package 的互動，我們將傳送一筆交易來建立一個新的 list，並在其中新增一個項目。交易是透過 `sui client ptb` 指令傳送的，它能完整發揮
[Transaction Blocks](./../concepts/what-is-a-transaction) 的能力。這個指令看起來可能很長很複雜，但我們會逐步說明。

### 準備變數 (Prepare the Variables) {#prepare-the-variables}

在建構指令之前，先儲存我們在交易中會用到的值。把 `0x4....` 換成你所發布 package 的地址。`MY_ADDRESS` 變數則會從 CLI 的輸出自動設為你的地址。

```bash
$ export PACKAGE_ID=0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
$ export MY_ADDRESS=$(sui client active-address)
```

### 在 CLI 中建構交易 (Building the Transaction in CLI) {#building-the-transaction-in-cli}

現在來建構實際的交易。這筆交易會包含兩個部分：呼叫 `todo_list` package 中的 `new` 函式來建立一個新的 list，然後將這個 list 物件轉移到我們的帳戶。交易看起來會像這樣：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--assign sender @$MY_ADDRESS \
--move-call $PACKAGE_ID::todo_list::new \
--assign list \
--transfer-objects "[list]" sender
```

在這個指令中，我們使用 `ptb` 子指令來建構一筆交易。接續在後面的參數定義了這筆交易將執行的實際指令與動作。我們所做的前兩個呼叫是工具性的呼叫，用來將寄件者地址設為指令輸入，並設定這筆交易的 gas 預算。

```bash
# 設定這筆交易的 gas 預算
--gas-budget 100000000 \n
# 註冊一個變數 "sender=@..."
--assign sender @$MY_ADDRESS \n
```

接著我們對 package 中的一個函式進行實際的呼叫。我們使用 `--move-call`，後面接著 package ID、模組名稱與函式名稱。在這個例子中，我們呼叫的是 `todo_list` package 中的 `new` 函式。

```bash
# 呼叫位於 $PACKAGE_ID 地址下 "todo_list" package 中的 "new" 函式
--move-call $PACKAGE_ID::todo_list::new
```

我們所定義的函式實際上會回傳一個值，而我們想要把它儲存起來。我們使用 `--assign` 指令來為回傳值命名。在這個例子中，我們把它命名為 `list`。然後將這個物件轉移到我們的帳戶。

```bash
--move-call $PACKAGE_ID::todo_list::new \
# 將 "new" 函式的結果指派給 "list" 變數（承接自前一步）
--assign list \
# 將物件轉移給寄件者
--transfer-objects "[list]" sender
```

指令建構完成後，你可以在終端機中執行它。如果一切正確，你應該會看到與前面章節相似的輸出。輸出將包含交易摘要（transaction digest）、交易資料，以及交易效果。

我們要關注的部分是「Object Changes」，更確切地說，是其中的「Created Objects」部分。它包含你所建立的 `TodoList` 的物件 ID、型別與版本。我們會用這個物件 ID 來與這個 list 互動。

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

在這個範例中，物件 ID 是
`0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553`。而擁有者應該是你的帳戶地址。我們透過在交易的最後一個指令中將物件轉移給寄件者，達成了這一點。

另一種驗證你已成功建立 list 的方式，是檢查帳戶的物件。

```bash
$ sui client objects
```

它應該會有一個看起來類似這樣的物件：

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

### 將物件傳入函式 (Passing Objects to Functions) {#passing-objects-to-functions}

我們在前一步建立的 TodoList 是一個你可以以其擁有者身分與之互動的物件。你可以對這個物件呼叫 `todo_list` 模組中定義的函式。為了示範這一點，我們將在 list 中新增一個項目。首先，我們只新增一個項目，然後在第二筆交易中新增三個並移除另一個。

再次確認你已經[在前一步](#prepare-the-variables)設定好變數，然後為這個 list 物件多加一個變數。

```bash
$ export LIST_ID=0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553
```

現在我們可以建構在 list 中新增一個項目的交易。指令看起來會像這樣：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish the Hello, Sui chapter'"
```

在這個指令中，我們呼叫的是 `todo_list` package 中的 `add` 函式。這個函式接收兩個引數：list 物件與要新增的項目。這個項目是一個字串，所以我們需要用單引號把它包起來。這個指令會把該項目新增到 list 中。

如果一切正確，你應該會看到與前面章節相似的輸出。現在你可以檢查這個 list 物件，看看項目是否已被新增。

```bash
$ sui client object $LIST_ID
```

輸出應該會包含你所新增的項目。物件中的 `items` 欄位會顯示項目清單。你可以加上 `--json` 旗標來取得該物件的 JSON 表示：

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

### 串接指令 (Chaining Commands) {#chaining-commands}

你可以在單一筆交易中串接多個指令。這展現了 Transaction Blocks 的強大之處！我們會使用同一個 list 物件，再新增三個項目並移除一個。指令看起來會像這樣：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish Concepts chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Read the Move Basics chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Learn about Object Model'" \
--move-call $PACKAGE_ID::todo_list::remove @$LIST_ID 0
```

如果前面的指令都執行成功，這個應該也不會有什麼不同。你可以檢查這個 list 物件，看看項目是否已被新增與移除。JSON 表示會比較容易閱讀一些！

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

指令不必來自同一個 package，也不必操作同一個物件。在單一筆交易區塊中，你可以與多個 package 及物件互動。這是一項強大的功能，讓你能夠在鏈上建構複雜的互動！

## 總結 (Conclusion) {#conclusion}

在本指南中，我們展示了如何在 Move 區塊鏈上發布套件並使用 Sui CLI 與其互動。我們示範了如何建立新的清單物件、加入項目，以及移除項目。我們也展示了如何在單一交易區塊中串連多個指令。本指南應能為你在 Sui 區塊鏈上建構自己的應用程式提供良好的起點！
