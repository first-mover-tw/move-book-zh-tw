---
description: 在 Sui 上的地址餘額 (Address balances)：無需 Coin 物件即可在地址直接持有同質化價值，使用 send_funds 傳送資金，並使用 Withdrawal 提領。
---

# 地址餘額 (Address Balances) {#address-balances}

[`Coin`](./balance-and-coin) 是一種物件：要花費它，交易必須以其 ID 參考它、取得它，並將它傳入。這對離散資產來說運作良好，但這會讓帳戶的資金變成一組必須被追蹤、合併與分割的個別物件。_地址餘額 (Address balances)_ 提供了不同的模型：以流水總數的形式直接持有於地址上的可替代價值，不需要管理任何物件。

在底層，該價值存在於以 `(address, type)` 這對鍵值索引的鏈上*累加器 (accumulator)* 中。某地址上 `T` 的餘額是單一數字，資金傳入時會增加，提領時會減少——這遠比一堆代幣的錢包更接近銀行帳戶的運作方式。

> 地址餘額是 Sui Framework 最近新增的功能。本節涵蓋核心的 `send_funds` / `redeem_funds` API、從物件提領，以及保護提領免於重放攻擊的交易層級規則。

## 傳送資金至地址 (Sending Funds to an Address) {#sending-funds-to-an-address}

任何 `Coin<T>` 或 [`Balance<T>`](./balance-and-coin#balance) 都可以透過 `send_funds` 存入地址餘額。該價值會被消耗並貸記到收款人的 `T` 餘額中：

```move file=packages/samples/sources/programmability/address-balances.move anchor=pay

```

`send_funds` 同時定義在 `Coin` 與 `Balance` 上。對於 `Coin` 而言，它會將代幣轉換為 `Balance` 並加入收款人的累加器；不會留下任何物件，收款人也不需要「接受」任何東西——餘額就這樣直接增加。

> 地址餘額的目前數值可以透過 Move 中的 `balance::settled_funds_value` 讀取，只要提供對系統 `AccumulatorRoot` 物件的參考即可。正如其名稱所示，它回報的是*已結算 (settled)* 資金，時間點為目前共識提交開始時——在該次提交中產生的存款尚不會反映在其中。

## 提領資金 (Withdrawing Funds) {#withdrawing-funds}

反向操作——從地址餘額*取出*價值——則被刻意設計成更加受限。你不能讀取任意地址的餘額並從中鑄造代幣；相反地，提領是以 `Withdrawal<Balance<T>>` 值來表示，該型別定義在 Sui Framework 的 `sui::funds_accumulator` 模組中：

```move
/// 允許從 `owner` 提領最多 `limit` 單位的 `T`。
public struct Withdrawal<phantom T: store> has drop {
    owner: address,
    limit: u256,
}
```

`Withdrawal` 是一種*授權 (authorization)*，而非資金本身。它記錄了要從誰的餘額中提領（`owner`）以及可提領的最大金額（`limit`）。它具有 `drop` 能力，因此未使用的 `Withdrawal` 可以直接被捨棄。交易會提供它——交易發送者的 `Withdrawal` 會由交易建構器以輸入的形式提供，其精神與 gas 代幣或[已接收物件](./../storage/transfer-to-object)相同。使用者程式碼中沒有它的建構函式。

因此，一筆從發送者地址餘額中花費的交易看起來會像這樣：`Withdrawal` 以輸入的形式傳入，在簽署時會針對發送者的餘額進行檢查，並由一個指令將其轉換為 `Coin`：

```text
// 從 sender 的地址餘額中提領 1_000 MIST
// Input 0: Withdrawal<Balance<SUI>> { owner: sender, limit: 1_000 }
// Input 1: recipient 地址
0: sui::coin::redeem_funds<SUI>(Input(0)); // -> Coin<SUI>
1: TransferObjects([Result(0)], Input(1));
```

一旦函式擁有 `Withdrawal`，就可以用 `redeem_funds` 將它兌換成真正的 `Coin`：

```move file=packages/samples/sources/programmability/address-balances.move anchor=collect

```

兌換正是金額真正從累加器中移出的時刻。它只能從定義該被提領型別的模組中被呼叫——這是透過[內部許可 (internal permit)](./../move-basics/internal-permit) 機制強制執行的，這也正是為什麼 `sui::coin` 與 `sui::balance`（分別定義 `Coin` 與 `Balance` 的模組）會是公開 `redeem_funds` 的模組。

## 檢查與分割 Withdrawal (Inspecting and Splitting a Withdrawal) {#inspecting-and-splitting-a-withdrawal}

在兌換之前，`Withdrawal` 可以被檢查與分割。當單一提領需要資助多項操作時，這會很有用：

```move file=packages/samples/sources/programmability/address-balances.move anchor=split_join

```

分割與合併 `Withdrawal` 只是在移動*額度 (limit)*；在呼叫 `redeem_funds` 之前，並不會有任何資金易手。合併需要兩個提領的 `owner` 相同，否則會中止。

## 從物件提領 (Withdrawing from an Object) {#withdrawing-from-an-object}

`Withdrawal` 的擁有者不一定要是帳戶——它也可以是物件。擁有地址餘額的物件可以透過 `withdraw_funds_from_object`，傳入其 `UID` 的可變參考，從自身資金中產生提領：

```move file=packages/samples/sources/programmability/address-balances.move anchor=object_withdraw

```

這讓任何物件——共享金庫、託管帳戶、財庫——都能持有並支付可替代價值，而不需要包裝個別的 `Coin` 物件。它所產生的提領會以與發送者相同的方式透過 `redeem_funds` 兌換。

## 重放保護與平行執行 (Replay Protection and Parallel Execution) {#replay-protection-and-parallel-execution}

地址餘額也改變了交易證明自身唯一且無法被重放的方式。一般的錨點是[擁有的物件 (owned object)](./../object/ownership#account-owner-or-single-owner)：每個物件都帶有一個[版本 (version)](./../object/object-model)，系統會在每次變更時遞增；因此參考該物件的已簽署交易只能執行一次——版本一旦變動，該交易就不再匹配。gas 代幣通常會免費提供這個錨點。

沒有任何擁有物件輸入的交易——例如直接從地址餘額支付 gas 的交易，或輸入僅為共享物件的交易——沒有任何東西可以作為錨點，因此它必須自行攜帶保護機制。交易資料中有兩個欄位涵蓋這一點。SDK 在建構此類交易時會設定這些欄位，因此這屬於交易*如何被建構*的問題，而非 Move 程式碼中的任何內容：

- **過期時間 (`ValidDuring`)。** 交易將其過期時間設定為 `TransactionExpiration::ValidDuring`，並附帶 `min_epoch` 與 `max_epoch`，兩者最多橫跨一個 epoch（`max_epoch <= min_epoch + 1`）。將有效性限制在狹窄的 epoch 視窗內，可以限縮該交易可能被重放的時間視窗，取代了保護擁有物件的版本檢查。
- **Nonce。** 交易包含一個 `nonce`——一個任意值，其唯一作用是讓兩筆原本相同的交易變得不同。與基於帳戶的鏈上 nonce 不同，它不是循序的，也沒有間隔問題；它只是讓原本會共享摘要值的交易得以共存。

正是這些特性使得此類交易得以保持可平行化：憑藉唯一的摘要值，再加上 Sui 已經在使用的[逐物件排序](./../object/fast-path-and-consensus#consensus-path)，彼此不衝突的提領永遠不需要互相等待。

## 總結 (Summary) {#summary}

- _地址餘額 (address balance)_ 是 `T` 型別的可替代價值，直接持有於鏈上累加器中的某個地址，而非以 `Coin` 物件的形式存在；
- `coin.send_funds(recipient)`（或 `balance.send_funds`）會將價值存入地址餘額，並消耗該代幣；
- 提領需要 `Withdrawal<Balance<T>>`——一種帶有 `owner` 與 `limit` 的授權——該授權由交易為發送者提供，或由物件為自身提供；
- `coin::redeem_funds` 會將 `Withdrawal` 轉換為 `Coin`，且只能透過[內部許可 (internal permit)](./../move-basics/internal-permit) 機制，從定義該型別的模組中呼叫；
- 沒有擁有物件輸入的交易（從地址餘額支付 gas，或僅使用共享物件）會攜帶自身的重放保護機制：限制在一個 epoch 內的 `ValidDuring` 過期時間，以及讓其摘要值保持唯一的 `nonce`。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::balance](https://docs.sui.io/references/framework/sui/balance) 模組文件。
- Sui 文件中的[使用地址餘額](https://docs.sui.io/onchain-finance/asset-custody/address-balances/using-address-balances)。
- [Balance and Coin](./balance-and-coin)：可替代代幣中以物件為基礎的一側。
