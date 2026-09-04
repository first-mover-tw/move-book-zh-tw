---
description: Sui 上的地址餘額 (Address balances)：無須 Coin 物件 (Coin object)，直接在地址持有可替代價值；使用 `send_funds` 傳送資金，並透過提款 (Withdrawal) 提領。
title: 地址餘額 (Address Balances)
keywords:
  - Move
  - Sui
  - Move tutorial
  - address
  - balances
questions:
  - What is Address Balances in Move?
  - How do I use Address Balances in Move?
  - What is Sending Funds to an Address in Move?
  - What is Withdrawing Funds in Move?
answer: 'Address balances on Sui: hold fungible value directly at an address without a Coin object, send funds with send_funds, and withdraw them with a Withdrawal.'
goal:
  description: 'Reader understands address balances on Sui: hold fungible value directly at an address without a Coin object, send funds with send_funds, and withdraw them with a Withdrawal'
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

# 地址餘額 (Address Balances) {#address-balances}

[`Coin`](./balance-and-coin) 是一種物件：若要花費它，交易必須透過其 ID 參考、擷取並傳入它。這對離散資產很適用，但會讓帳戶的資金成為一組必須追蹤、合併及分割的個別物件。*地址餘額*提供了不同的模型：可互換價值會以累計總額的形式直接持有於地址，不需要管理任何物件。

在底層，該價值存在鏈上以 `(address, type)` 配對為索引鍵的*累加器*中。地址上的 `T` 餘額是一個單一數值；資金轉入時增加，提領時減少——比起裝滿代幣的錢包，更接近銀行帳戶的運作方式。

> 地址餘額是 Sui Framework 最近新增的功能。本節涵蓋核心的 `send_funds` / `redeem_funds` API、從物件提領資金，以及保護提領操作免於重放的交易層級規則。

## 將資金傳送至地址 (Sending Funds to an Address) {#sending-funds-to-an-address}

任何 `Coin<T>` 或 [`Balance<T>`](./balance-and-coin#balance) 都可透過 `send_funds` 存入地址餘額。該價值會被消耗，並記入收款者的 `T` 餘額：

```move file=packages/samples/sources/programmability/address-balances.move anchor=pay

```

`send_funds` 同時定義於 `Coin` 和 `Balance`。對 `Coin` 而言，它會將代幣轉為 `Balance`，並加入收款者的累加器；不會留下任何物件，收款者也不需要「接受」任何東西——餘額會直接增加。

> 地址餘額的目前價值可在 Move 中透過 `balance::settled_funds_value` 讀取，並須提供系統 `AccumulatorRoot` 物件的參考。如名稱所示，它會回報目前共識提交開始時已*結算*的資金——在該提交期間所存入的資金尚無法從中看見。

## 提領資金 (Withdrawing Funds) {#withdrawing-funds}

反方向操作——從地址餘額*取出*價值——受到刻意更嚴格的限制。你無法讀取任意地址的餘額並從中鑄造代幣；相反地，提領會由 `Withdrawal<Balance<T>>` 值表示，它定義於 Sui Framework 的 `sui::funds_accumulator` 模組中：

```move
/// 從 `owner` 提領最多 `limit` 單位 `T` 的權限。
public struct Withdrawal<phantom T: store> has drop {
    owner: address,
    limit: u256,
}
```

`Withdrawal` 是一種*授權*，不是資金本身。它記錄要從誰的餘額扣除（`owner`），以及可取出的最大數量（`limit`）。它具有 `drop`，因此未使用的值可直接丟棄。交易會提供它——交易建置工具會將交易傳送者的 `Withdrawal` 作為輸入提供，其概念與 gas 代幣或[接收的物件](./../storage/transfer-to-object)相同。使用者原始碼中沒有可建立它的建構子。

因此，從傳送者地址餘額花費資金的交易如下：`Withdrawal` 會作為輸入傳入，在簽署時依傳送者餘額驗證，並由一個命令將它轉為 `Coin`：

```text
// 從傳送者的地址餘額花費 1_000 MIST
// 輸入 0：Withdrawal<Balance<SUI>> { owner: sender, limit: 1_000 }
// 輸入 1：收款者地址
0: sui::coin::redeem_funds<SUI>(Input(0)); // -> Coin<SUI>
1: TransferObjects([Result(0)], Input(1));
```

函式一旦取得 `Withdrawal`，便可使用 `redeem_funds` 將其兌換為真正的 `Coin`：

```move file=packages/samples/sources/programmability/address-balances.move anchor=collect

```

兌換時才會真正將數量從累加器中移出。它只能由定義被提領型別的模組執行——這由[內部許可](./../move-basics/internal-permit)機制強制執行；這也正是 `sui::coin` 與 `sui::balance`（定義 `Coin` 與 `Balance` 的模組）會公開 `redeem_funds` 的原因。

## 檢查與分割 Withdrawal (Inspecting and Splitting a Withdrawal) {#inspecting-and-splitting-a-withdrawal}

在兌換前，可檢查並分割 `Withdrawal`。這在單一提領需支應多項操作時很有用：

```move file=packages/samples/sources/programmability/address-balances.move anchor=split_join

```

分割與合併 `Withdrawal` 只會移動*上限*；在呼叫 `redeem_funds` 前，不會有任何資金轉移。合併要求兩個提領具有相同的 `owner`，否則會中止。

## 從物件提領資金 (Withdrawing from an Object) {#withdrawing-from-an-object}

`Withdrawal` 的擁有者不一定是帳戶——也可以是物件。具有地址餘額的物件可透過 `withdraw_funds_from_object` 從自身資金建立提領，並傳入其 `UID` 的可變參考：

```move file=packages/samples/sources/programmability/address-balances.move anchor=object_withdraw

```

這讓任何物件——共享金庫、託管帳戶或國庫——都能持有並支付可互換價值，而無須封裝個別的 `Coin` 物件。它所建立的提領會以與傳送者提領相同的方式透過 `redeem_funds` 兌換。

## 重放保護與平行執行 (Replay Protection and Parallel Execution) {#replay-protection-and-parallel-execution}

地址餘額也改變了交易證明其唯一性且無法被重放的方式。通常的錨點是[受擁有物件](./../object/ownership#account-owner-or-single-owner)：每個物件都帶有系統會在每次變更時遞增的[版本](./../object/object-model)，因此參考該物件的已簽署交易只能執行一次——版本變更後，交易便不再相符。gas 代幣通常會免費提供這個錨點。

沒有受擁有物件輸入的交易——例如直接從地址餘額支付 gas，或輸入僅包含共享物件的交易——沒有可用的錨點，因此必須自行攜帶保護機制。交易資料的兩個欄位涵蓋此需求。SDK 會在建置這類交易時設定它們，因此這關乎交易如何被*建立*，而非 Move 原始碼中的任何內容：

- **到期時間 (`ValidDuring`)。** 交易會將其到期時間設定為 `TransactionExpiration::ValidDuring`，並指定 `min_epoch` 與 `max_epoch`，範圍最多跨越一個 epoch（`max_epoch <= min_epoch + 1`）。將有效性限制於狹窄的 epoch 視窗，可限制交易可能遭重放的時間視窗，取代保護受擁有物件的版本檢查。
- **Nonce。** 交易包含 `nonce`——其唯一用途是讓兩筆原本完全相同的交易有所區別的任意值。與帳戶型區塊鏈的 nonce 不同，它不具連續性，也沒有間隔問題；它只是讓原本會共用摘要的交易能夠共存。

這些相同屬性也使這類交易可平行化：藉由唯一摘要，以及 Sui 已採用的[逐物件排序](./../object/fast-path-and-consensus#consensus-path)，沒有衝突的提領操作永遠不必彼此等待。

## 總結 (Summary) {#summary}

- *地址餘額*是直接以鏈上累加器形式持有於地址上的 `T` 型別可互換價值，而非 `Coin` 物件；
- `coin.send_funds(recipient)`（或 `balance.send_funds`）會將價值存入地址餘額，並消耗該代幣；
- 提領需要 `Withdrawal<Balance<T>>`——具有 `owner` 與 `limit` 的授權——交易會為傳送者提供它，或物件會為自身提供它；
- `coin::redeem_funds` 會將 `Withdrawal` 轉為 `Coin`，且只能透過[內部許可](./../move-basics/internal-permit)機制，從定義該型別的模組中呼叫；
- 沒有受擁有物件輸入的交易（從地址餘額支付 gas，或僅使用共享物件）會自行攜帶重放保護：限制於一個 epoch 的 `ValidDuring` 到期時間，以及使其摘要唯一的 `nonce`。

## 延伸閱讀 (Further Reading) {#further-reading}

- [sui::balance](https://docs.sui.io/references/framework/sui/balance) 模組文件。
- Sui 文件中的[使用地址餘額](https://docs.sui.io/onchain-finance/asset-custody/address-balances/using-address-balances)。
- [Balance and Coin](./balance-and-coin)，了解可互換代幣以物件為基礎的一面。
