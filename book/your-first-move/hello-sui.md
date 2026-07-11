---
description: 'Build and publish a todo list app on Sui: create an account, deploy a Move package, and send transactions via the CLI.'
---

# 你好，Sui！

在[上一節](./hello-world)中，我們建立了一個新的程式包，並展示了建立、建置和測試 Move 程式包的基本流程。在本節中，我們將編寫一個使用儲存模型並可與之互動的簡單應用程式。為此，我們將建立一個簡單的待辦事項清單應用程式。

## 建立新程式包

按照與 [Hello, World!](./hello-world) 相同的流程，我們將建立一個名為 `todo_list` 的新程式包。

```bash
$ sui move new todo_list
```

## 新增程式碼

為了加快進度並專注於應用程式邏輯，我們將提供待辦事項清單應用程式的程式碼。將 _sources/todo_list.move_ 檔案的內容替換為以下程式碼：

> 注意：儘管內容一開始可能看起來很複雜，我們將在後續章節中逐步解析。請先專注於當前的內容。

```move file=packages/todo_list/sources/todo_list.move anchor=all

```

## 建置程式包

為了確保我們一切都做對了，讓我們執行 `sui move build` 命令來建置程式包。如果一切正確，您應該會看到類似以下的輸出：

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

如果此輸出後沒有錯誤，則您已成功建置程式包。如果出現錯誤，請確保：

- 程式碼已正確複製
- 檔案名稱和程式包名稱正確

在此階段，程式碼失敗的原因通常不多。但如果您仍然遇到問題，請嘗試在[此處](https://github.com/MystenLabs/move-book/tree/main/packages/todo_list)查看程式包的結構。

## 設定帳戶

> 如果您已經設定了帳戶，您可以跳過此步驟。

為了發布程式包並與其互動，我們需要設定一個帳戶。在開發過程中，最好的方法是運行您自己的[本地網路](https://docs.sui.io/guides/developer/getting-started/local-network)。目前您只需執行 `RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis`。Sui 本地網路將在您機器的 9000 埠上運行，因此請確保該埠未被任何其他應用程式使用。

如果您是第一次操作，您將需要建立一個新帳戶。為此，請執行 `sui client` 命令，然後命令列介面 (CLI) 將提示您回答多個問題。答案在下面以 `>` 標示：

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

回答問題後，命令列介面 (CLI) 將產生一個新的金鑰對並將其儲存到組態檔中。您現在可以使用此帳戶與網路互動。

為確認帳戶已正確設定，請執行 `sui client active-address` 命令：

```bash
$ sui client active-address
0x....
```

該命令將輸出您的帳戶地址，它以 `0x` 開頭，後跟 64 個字元。

## 請求幣

在 _開發網路 (devnet)_ 和 _測試網路 (testnet)_ 環境中，命令列介面 (CLI) 提供了一種向您的帳戶請求幣的方式，以便您可以與網路互動。要請求幣，請執行 `sui client faucet` 命令：

```bash
$ sui client faucet
Request successful. It can take up to 1 minute to get the coin. Run sui client gas to check your gas coins.
```

稍等片刻後，您可以透過執行 `sui client balance` 命令來檢查 Coin 物件是否已發送到您的帳戶：

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

或者，您可以透過執行 `sui client objects` 命令來查詢您的帳戶擁有的 _物件_。實際輸出會有所不同，因為物件 ID 和摘要都是唯一的，但結構會相似：

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

現在我們已經設定好帳戶並在帳戶中擁有幣，我們可以與網路互動了。我們將從將程式包發布到網路開始。

## 發布

要將程式包發布到網路，我們將使用 `sui client publish` 命令。該命令將自動建置程式包並使用其位元組碼在單一交易中發布。

> 我們在發布時使用了 `--gas-budget` 參數。它指定了我們願意為該交易花費多少燃料費。我們不會在本節中深入探討這個主題，但重要的是要知道 Sui 中的每筆交易都會產生燃料費，而燃料費是用 SUI 幣支付的。值得注意的是，`--gas-budget` 不是一個必需的參數。如果您不設定它，將會有一個預設的消耗限制。

「燃料費預算 (gas-budget)」是以 _MISTs_ 為單位指定的。1 SUI 等於 10^9 MISTs。為了演示，我們將使用 100,000,000 MISTs，即 0.1 SUI。

```bash
# 從 `todo_list` 資料夾運行此命令
$ sui client publish --gas-budget 100000000

# 或者，您可以指定程式包的路徑
$ sui client publish --gas-budget 100000000 todo_list
```

發布命令的輸出相當長，因此我們將分部分展示和解釋它。

```bash
$ sui client publish --gas-budget 100000000
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING todo_list
Successfully verified dependencies on-chain against source.
Transaction Digest: GpcDV6JjjGQMRwHpEz582qsd5MpCYgSwrDAq1JXcpFjW
```

正如您所看到的，當我們執行 `publish` 命令時，命令列介面 (CLI) 首先建置程式包，然後驗證鏈上依賴項，最後發布程式包。命令的輸出是交易摘要，它是一個交易的唯一識別碼，可用於查詢交易狀態。

### 交易資料

標題為 `TransactionData` 的部分包含我們剛才發送的交易資訊。它包含諸如 `sender`（這是您的地址）、使用 `--gas-budget` 參數設定的 `gas_budget`（燃料費預算）以及我們用於支付的 Coin。它還會印出由命令列介面 (CLI) 執行的命令。在此範例中，執行了 `Publish` 和 `TransferObject` 命令，後者將一個特殊物件 `UpgradeCap` 轉移給發送者。

```plaintext
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Transaction Data                                                                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                                   │
│ Gas Owner: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                                │
│ Gas Budget: 100000000 MIST                                                                                   │
│ Gas Price: 1000 MIST                                                                                         │
│ Gas Payment:                                                                                                 │
│  ┌──                                                                                                         │
│  │ ID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                                    │
│  │ Version: 7                                                                                                │
│  │ Digest: AXYPnups8A5J6pkvLa6RekX2ye3qur66EZ88mEbaUDQ1                                                      │
│  └──                                                                                                         │
│                                                                                                              │
│ Transaction Kind: Programmable                                                                               │
│ ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
│ │ Input Objects                                                                                            │ │
│ ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ │ 0   Pure Arg: Type: address, Value: "0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1" │ │
│ ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯ │
│ ╭─────────────────────────────────────────────────────────────────────────╮                                  │
│ │ Commands                                                                │                                  │
│ ├─────────────────────────────────────────────────────────────────────────┤                                  │
│ │ 0  Publish:                                                             │                                  │
│ │  ┌                                                                      │                                  │
│ │  │ Dependencies:                                                        │                                  │
│ │  │   0x0000000000000000000000000000000000000000000000000000000000000001 │                                  │
│ │  │   0x0000000000000000000000000000000000000000000000000000000000000002 │                                  │
│ │  └                                                                      │                                  │
│ │                                                                         │                                  │
│ │ 1  TransferObjects:                                                     │                                  │
│ │  ┌                                                                      │                                  │
│ │  │ Arguments:                                                           │                                  │
│ │  │   Result 0                                                           │                                  │
│ │  │ Address: Input  0                                                    │                                  │
│ │  └                                                                      │                                  │
│ ╰─────────────────────────────────────────────────────────────────────────╯                                  │
│                                                                                                              │
│ Signatures:                                                                                                  │
│    gebjSbVwZwTkizfYg2XIuzdx+d66VxFz8EmVaisVFiV3GkDay6L+hQG3n2CQ1hrWphP6ZLc7bd1WRq4ss+hQAQ==                  │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 交易影響

交易影響 (Transaction Effects) 包含交易的狀態、該交易對網路狀態所做的更改以及交易中涉及的物件。

```plaintext
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
│ Gas Object:                                                                                       │
│  ┌──                                                                                              │
│  │ ID: 0x4ea1303e4f5e2f65fc3709bc0fb70a3035fdd2d53dbcff33e026a50a742ce0de                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 8                                                                                     │
│  │ Digest: 7ydahjaM47Gyb33PB4qnW2ZAGqZvDuWScV6sWPiv7LTc                                           │
│  └──                                                                                              │
│ Gas Cost Summary:                                                                                 │
│    Storage Cost: 10404400 MIST                                                                    │
│    Computation Cost: 1000000 MIST                                                                 │
│    Storage Rebate: 978120 MIST                                                                    │
│    Non-refundable Storage Fee: 9880 MIST                                                          │
│                                                                                                   │
│ Transaction Dependencies:                                                                         │
│    7Ukrc5GqdFqTA41wvWgreCdHn2vRLfgQ3YMFkdks72Vk                                                   │
│    7d4amuHGhjtYKujEs9YkJARzNEn4mRbWWv3fn4cdKdyh                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 事件

如果發出了任何 _事件_，您將在此部分看到它們。我們的程式包沒有使用事件，因此此部分為空。

```plaintext
╭─────────────────────────────╮
│ No transaction block events │
╰─────────────────────────────╯
```

### 物件變更

這些是交易對 _物件_ 所做的變更。在我們的案例中，我們 _建立_ 了一個新的 `UpgradeCap` 物件，它是一個特殊物件，允許發送者將來升級程式包，_變更_ 了 Gas 物件，並 _發布_ 了一個新程式包。程式包在 Sui 上也是物件。

```plaintext
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
│  │ Digest: 7ydahjaM47Gyb33PB4qnW2ZAGqZvDuWScV6sWPiv7LTc                                           │
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

### 餘額變更

最後這部分包含 SUI 幣的變更，在我們的案例中，我們 _花費_ 了約 0.015 SUI，轉換成 MISTs 為 10,500,000。您可以在輸出中的 _amount_ 欄位下看到它。

```plaintext
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

### 替代輸出

在發布時可以指定 `--json` 旗標，以 JSON 格式獲取輸出。如果您想以程式方式解析輸出或儲存以供後續使用，這會很有用。

```bash
$ sui client publish --gas-budget 100000000 --json
```

### 使用結果

程式包發布到鏈上後，我們就可以與其互動了。為此，我們需要找到程式包的地址（物件 ID）。它位於 `Object Changes` 輸出的 `Published Objects` 部分。每個程式包的地址都是唯一的，因此您需要從輸出中複製它。

在此範例中，地址為：

```plaintext
0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
```

現在我們有了地址，我們可以與程式包互動了。在下一節中，我們將展示如何透過發送交易來與程式包互動。

## 發送交易

為了演示與 `todo_list` 程式包的互動，我們將發送一筆交易來建立一個新清單並向其中新增一個項目。交易透過 `sui client ptb` 命令發送，它允許充分利用 [交易區塊 (Transaction Blocks)](./../concepts/what-is-a-transaction) 的功能。這個命令可能看起來龐大而複雜，但我們會逐步解釋。

### 準備變數 {#prepare-the-variables}

在我們建構命令之前，讓我們先儲存將在交易中使用的值。將 `0x4....` 替換為您已發布的程式包地址。而 `MY_ADDRESS` 變數將自動從命令列介面 (CLI) 輸出中設定為您的地址。

```bash
$ export PACKAGE_ID=0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe
$ export MY_ADDRESS=$(sui client active-address)
```

### 在命令列介面 (CLI) 中建構交易

現在來建構實際的交易。該交易將由兩部分組成：我們將呼叫 `todo_list` 程式包中的 `new` 函數來建立一個新清單，然後將該清單物件轉移到我們的帳戶。該交易將如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--assign sender @$MY_ADDRESS \
--move-call $PACKAGE_ID::todo_list::new \
--assign list \
--transfer-objects "[list]" sender
```

在此命令中，我們使用 `ptb` 子命令來建構交易。後面的參數定義了交易將執行的實際命令和動作。我們執行的前兩個呼叫是公用程式呼叫，用於將發送者地址設定為命令輸入，並設定交易的燃料費預算。

```bash
# 設定交易的燃料費預算
--gas-budget 100000000 \n
# 註冊變數 "sender=@..."
--assign sender @$MY_ADDRESS \n
```

然後我們執行對程式包中函數的實際呼叫。我們使用 `--move-call`，後面跟著程式包 ID、模組名稱和函數名稱。在此案例中，我們正在呼叫 `todo_list` 程式包中的 `new` 函數。

```bash
# 在 $PACKAGE_ID 地址下呼叫 "todo_list" 程式包中的 "new" 函數
--move-call $PACKAGE_ID::todo_list::new
```

我們定義的函數實際上會回傳一個值，我們希望儲存它。我們使用 `--assign` 命令為回傳值命名。在此案例中，我們將其命名為 `list`。然後我們將物件轉移到我們的帳戶。

```bash
--move-call $PACKAGE_ID::todo_list::new \
# 將 "new" 函數的結果指派給 "list" 變數（來自上一步驟）
--assign list \
# 將物件轉移給發送者
--transfer-objects "[list]" sender
```

一旦命令建構完成，您可以在終端機中執行它。如果一切正確，您應該會看到類似於前幾節中的輸出。輸出將包含交易摘要、交易資料和交易影響。

<details>
<summary><a>劇透：完整的交易輸出</a></summary>

```bash
Transaction Digest: BJwYEnuuMzU4Y8cTwMoJbbQA6cLwPmwxvsRpSmvThoK8
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Transaction Data                                                                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                                   │
│ Gas Owner: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                                │
│ Gas Budget: 100000000 MIST                                                                                  │
│ Gas Price: 1000 MIST                                                                                         │
│ Gas Payment:                                                                                                 │
│  ┌──                                                                                                         │
│  │ ID: 0xe5ddeb874a8d7ead328e9f2dd2ad8d25383ab40781a5f1aefa75600973b02bc4                                    │
│  │ Version: 22                                                                                               │
│  │ Digest: DiBrBMshDiD9cThpaEgpcYSF76uV4hCoE1qRyQ3rnYCB                                                      │
│  └──                                                                                                         │
│                                                                                                              │
│ Transaction Kind: Programmable                                                                               │
│ ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
│ │ Input Objects                                                                                            │ │
│ ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ │ 0   Pure Arg: Type: address, Value: "0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1" │ │
│ ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯ │
│ ╭──────────────────────────────────────────────────────────────────────────────────╮                         │
│ │ Commands                                                                         │                         │
│ ├──────────────────────────────────────────────────────────────────────────────────┤                         │
│ │ 0  MoveCall:                                                                     │                         │
│ │  ┌                                                                               │                         │
│ │  │ Function:  new                                                                │                         │
│ │  │ Module:    todo_list                                                          │                         │
│ │  │ Package:   0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe │                         │
│ │  └                                                                               │                         │
│ │                                                                                  │                         │
│ │ 1  TransferObjects:                                                              │                         │
│ │  ┌                                                                               │                         │
│ │  │ Arguments:                                                                    │                         │
│ │  │   Result 0                                                                    │                         │
│ │  │ Address: Input  0                                                             │                         │
│ │  └                                                                               │                         │
│ ╰──────────────────────────────────────────────────────────────────────────────────╯                         │
│                                                                                                              │
│ Signatures:                                                                                                  │
│    C5Lie4dtP5d3OkKzFBa+xM0BiNoB/A4ItthDCRTRBUrEE+jXeNs7mP4AuGwi3nzfTskh29+R1j1Kba4Wdy3QDA==                  │
│                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Transaction Effects                                                                               │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Digest: BJwYEnuuMzU4Y8cTwMoJbbQA6cLwPmwxvsRpSmvThoK8                                              │
│ Status: Success                                                                                   │
│ Executed Epoch: 1213                                                                              │
│                                                                                                   │
│ Created Objects:                                                                                  │
│  ┌──                                                                                              │
│  │ ID: 0x74973c4ea2e78dc409f60481e23761cee68a48156df93a93fbcceb77d1cacdf6                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 23                                                                                    │
│  │ Digest: DuHTozDHMsuA7cFnWRQ1Gb8FQghAEBaj3inasJxqYq1c                                           │
│  └──                                                                                              │
│ Mutated Objects:                                                                                  │
│  ┌──                                                                                              │
│  │ ID: 0xe5ddeb874a8d7ead328e9f2dd2ad8d25383ab40781a5f1aefa75600973b02bc4                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 23                                                                                    │
│  │ Digest: 82fwKarGuDhtomr5oS6ZGNvZNw9QVXLSbPdQu6jQgNV7                                           │
│  └──                                                                                              │
│ Gas Object:                                                                                       │
│  ┌──                                                                                              │
│  │ ID: 0xe5ddeb874a8d7ead328e9f2dd2ad8d25383ab40781a5f1aefa75600973b02bc4                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ Version: 23                                                                                    │
│  │ Digest: 82fwKarGuDhtomr5oS6ZGNvZNw9QVXLSbPdQu6jQgNV7                                           │
│  └──                                                                                              │
│ Gas Cost Summary:                                                                                 │
│    Storage Cost: 2318000 MIST                                                                     │
│    Computation Cost: 1000000 MIST                                                                 │
│    Storage Rebate: 978120 MIST                                                                    │
│    Non-refundable Storage Fee: 9880 MIST                                                          │
│                                                                                                   │
│ Transaction Dependencies:                                                                         │
│    FSz2fYXmKqTf77mFXNq5JK7cKY8agWja7V5yDKEgL8c3                                                   │
│    GgMZKTt482DYApbAZkPDtdssGHZLbxgjm2uMXhzJax8Q                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────╮
│ No transaction block events │
╰─────────────────────────────╯

╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Object Changes                                                                                        │
├───────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Created Objects:                                                                                      │
│  ┌──                                                                                                  │
│  │ ObjectID: 0x74973c4ea2e78dc409f60481e23761cee68a48156df93a93fbcceb77d1cacdf6                       │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )      │
│  │ ObjectType: 0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList  │
│  │ Version: 23                                                                                        │
│  │ Digest: DuHTozDHMsuA7cFnWRQ1Gb8FQghAEBaj3inasJxqYq1c                                               │
│  └──                                                                                                  │
│ Mutated Objects:                                                                                      │
│  ┌──                                                                                                  │
│  │ ObjectID: 0xe5ddeb874a8d7ead328e9f2dd2ad8d25383ab40781a5f1aefa75600973b02bc4                       │
│  │ Sender: 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1                         │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )      │
│  │ ObjectType: 0x2::coin::Coin<0x2::sui::SUI>                                                         │
│  │ Version: 23                                                                                        │
│  │ Digest: 82fwKarGuDhtomr5oS6ZGNvZNw9QVXLSbPdQu6jQgNV7                                               │
│  └──                                                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Balance Changes                                                                                   │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌──                                                                                              │
│  │ Owner: Account Address ( 0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1 )  │
│  │ CoinType: 0x2::sui::SUI                                                                        │
│  │ Amount: -2339880                                                                               │
│  └──                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</details>

我們想要關注的部分是「物件變更 (Object Changes)」。更具體地說，是其中的「已建立物件 (Created Objects)」部分。它包含了您所建立 `TodoList` 的物件 ID、類型和版本。我們將使用此物件 ID 來與清單互動。

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
│  │ Digest: DiBrBMshDiD9cThpaEgpcYSF76uV4hCoE1qRyQ3rnYCB                                               │
│  └──                                                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

在此範例中，物件 ID 為 `0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553`。所有者應該是您的帳戶地址。我們透過在交易的最後一個命令中將物件轉移給發送者來實現這一點。

另一種測試您是否成功建立清單的方法是檢查帳戶物件。

```bash
$ sui client objects
```

它應該有一個類似以下的物件：

```plaintext
╭  ...                                                                                  ╮
│ ╭────────────┬──────────────────────────────────────────────────────────────────────╮ │
│ │ objectId   │  0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553  │ │
│ │ version    │  22                                                                  │ │
│ │ digest     │  /DUEiCLkaNSgzpZSq2vSV0auQQEQhyH9occq9grMBZM=                        │ │
│ │ objectType │  0x468d..29fe::todo_list::TodoList                                   │ │
│ ╰────────────┴──────────────────────────────────────────────────────────────────────╯ │
|  ...                                                                                  |
```

### 將物件傳遞給函數

我們在上一步驟中建立的 TodoList 是一個您可以作為其所有者進行互動的物件。您可以對此物件呼叫 `todo_list` 模組中定義的函數。為了演示這一點，我們將向清單中新增一個項目。首先，我們只會新增一個項目，然後在第二筆交易中，我們將新增 3 個並移除另一個。

再次檢查您是否已從[上一步驟](#prepare-the-variables)設定好變數，然後為清單物件新增一個變數。

```bash
$ export LIST_ID=0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553
```

現在我們可以建構向清單中新增項目的交易。該命令將如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish the Hello, Sui chapter'"
```

在此命令中，我們正在呼叫 `todo_list` 程式包中的 `add` 函數。該函數接受兩個參數：清單物件和要新增的項目。該項目是一個字串，因此我們需要用單引號將其包起來。該命令將把項目新增到清單中。

如果一切正確，您應該會看到類似於前幾節中的輸出。現在您可以檢查清單物件，看看項目是否已新增。

```bash
$ sui client object $LIST_ID
```

輸出應該包含您已新增的項目。

```plaintext
╭───────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ objectId      │  0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553                                               │
│ version       │  24                                                                                                               │
│ digest        │  FGcXH8MGpMs5BdTnC62CQ3VLAwwexYg2id5DKU7Jr9aQ                                                                     │
│ objType       │  0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList                          │
│ owner         │ ╭──────────────┬──────────────────────────────────────────────────────────────────────╮                           │
│               │ │ AddressOwner │  0x091ef55506ad814920adcef32045f9078f2f6e9a72f4cf253a1e6274157380a1  │                           │
│               │ ╰──────────────┴──────────────────────────────────────────────────────────────────────╯                           │
│ prevTx        │  EJVK6FEHtfTdCuGkNsU1HcrmUBEN6H6jshfcptnw8Yt1                                                                     │
│ storageRebate │  1558000                                                                                                          │
│ content       │ ╭───────────────────┬───────────────────────────────────────────────────────────────────────────────────────────╮ │
│               │ │ dataType          │  moveObject                                                                               │ │
│               │ │ type              │  0x468daa33dfcb3e17162bbc8928f6ec73744bb08d838d1b6eb94eac99269b29fe::todo_list::TodoList  │ │
│               │ │ hasPublicTransfer │  true                                                                                     │ │
│               │ │ fields            │ ╭───────┬───────────────────────────────────────────────────────────────────────────────╮ │ │
│               │ │                   │ │ id    │ ╭────┬──────────────────────────────────────────────────────────────────────╮ │ │ │
│               │ │                   │ │       │ │ id │  0x20e0bede16de8a728ab25e228816b9059b45ebea49c8ad384e044580b2d3e553  │ │ │ │
│               │ │                   │ │       │ ╰────┴──────────────────────────────────────────────────────────────────────╯ │ │ │
│               │ │                   │ │ items │ ╭─────────────────────────────────╮                                           │ │ │
│               │ │                   │ │       │ │  finish the Hello, Sui chapter  │                                           │ │ │
│               │ │                   │ │       │ ╰─────────────────────────────────╯                                           │ │ │
│               │ │                   │ ╰───────┴───────────────────────────────────────────────────────────────────────────────╯ │ │
│               │ ╰───────────────────┴───────────────────────────────────────────────────────────────────────────────────────────╯ │
╰───────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

透過在命令中添加 `--json` 旗標，可以獲得物件的 JSON 表示。

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

### 鏈接命令

您可以在單一交易中鏈接多個命令。這展示了交易區塊 (Transaction Blocks) 的強大功能！使用相同的清單物件，我們將再新增三個項目並移除一個。該命令將如下所示：

```bash
$ sui client ptb \
--gas-budget 100000000 \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Finish Concepts chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Read the Move Basics chapter'" \
--move-call $PACKAGE_ID::todo_list::add @$LIST_ID "'Learn about Object Model'" \
--move-call $PACKAGE_ID::todo_list::remove @$LIST_ID 0
```

如果之前的命令成功，這個也應該沒有問題。您可以檢查清單物件，看看項目是否已新增和移除。JSON 表示方式會更具可讀性！

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

命令不必在同一個程式包中或操作相同的物件。在單一交易區塊中，您可以與多個程式包和物件互動。這是一個強大的功能，允許您在鏈上建立複雜的互動！

## 結論

在本指南中，我們展示了如何在 Move 區塊鏈上發布程式包，並使用 Sui 命令列介面 (CLI) 與其互動。我們演示了如何建立新的清單物件、向其中新增項目以及移除項目。我們還展示了如何在單一交易區塊中鏈接多個命令。本指南應為您在 Sui 區塊鏈上建立自己的應用程式提供一個良好的起點！
