---
description: Sui 鏈上隨機性 (Onchain Randomness in Sui)：使用 Random 共享物件 (shared object) 在 Move 智慧合約 (smart contract) 中產生安全的隨機值。
---

# 鏈上隨機性 (Onchain Randomness) {#onchain-randomness}

隨機性對區塊鏈來說是個出乎意料棘手的問題。執行必須具備確定性——每個驗證者都必須執行一筆交易並得出完全相同的結果——而且每個輸入都是公開的。看起來隨機的值，例如[目前時間](./epoch-and-time)、epoch、或交易摘要（transaction digest），其實是可預測的，甚至更糟的是，可能被發送者或驗證者影響。當牽涉到金錢時，「看起來隨機」是不夠的：任何可被預測或操縱的隨機性來源，最終都會被利用。

為了解決這個問題，Sui 採用*集體*產生隨機性的方式：在每個 epoch 開始時，驗證者會執行一個分散式金鑰產生協定（distributed key generation protocol），接著在每次共識提交（consensus commit）時，共同產生一個新的隨機值，這個值沒有任何單一方——甚至連驗證者也不例外——能夠事先得知。這個值會被寫入 `Random` 系統物件，並提供給 Move 程式使用。

## `Random` 物件 (The `Random` Object) {#the-random-object}

`Random` 物件定義於 `sui::random` 模組中，並擁有保留地址 `0x8`（參見[保留地址](./../appendix/reserved-addresses)）。這個地址在每個網路上都相同——localnet、devnet、testnet 與 mainnet——因此可以安全地寫死（hardcode）在應用程式與客戶端程式碼中。與[時鐘（Clock）](./epoch-and-time#time)物件類似，它是一個共享物件，無法以可變的方式存取——嘗試以可變參考取得它的交易會失敗。這使得隨機性可以被平行存取，同時保護全域狀態不被竄改。

```move
module sui::random;

/// 儲存全域隨機性狀態的單例共享物件。
/// 實際狀態儲存在一個帶版本的內部欄位中。
public struct Random has key {
    id: UID,
    inner: Versioned,
}
```

該物件的內部狀態會在每次共識提交時由系統更新，其不可預測性不會隨著 epoch 的推進而降低。

## 使用隨機性 (Using Randomness) {#using-randomness}

隨機性不會直接從 `Random` 物件讀取。相反地，交易會建立一個 `RandomGenerator`——一個本地的隨機值來源，衍生自全域狀態並且對該交易來說是唯一的。這個產生器提供了滿足常見需求的方法：布林值、各種大小的整數、範圍內的整數（邊界為包含性）、原始位元組，以及向量的洗牌：

```move file=packages/samples/sources/programmability/randomness.move anchor=generator

```

典型的用法如下：一個函式接受 `&Random`，用 `new_generator` 建立一個產生器，並用它來產生所需數量的值。以下範例會鑄造一枚具有隨機品質的 `Medal`——10% 機率為 Gold、30% 機率為 Silver、60% 機率為 Bronze：

```move file=packages/samples/sources/programmability/randomness.move anchor=main

```

這個範例刻意被拆成兩個函式，而這種拆分方式正是使用隨機性時建議採用的程式碼結構。讓我們來看看原因。

## 正確封裝隨機性 (Encapsulating Randomness Correctly) {#encapsulating-randomness-correctly}

`mint_medal` 函式被宣告為私有的 [entry](./../move-basics/visibility) 函式——它可以從交易中呼叫，但無法從其他模組呼叫。這是刻意設計的，也是使用隨機性時最重要的一條規則：

> 接受 `&Random`（或 `RandomGenerator`）作為參數的函式，永遠不應該是 `public`。這包括 `public entry`——`public entry` 函式仍然可以從其他模組呼叫。對於隨機性，一律使用私有的 `entry` 函式。

為了理解原因，讓我們來打破這條規則。以下是同一個函式的變體，它是 `public` 的，並回傳擲骰結果：

```move
/// 鑄造一枚 `Medal`，將其轉移給呼叫者，並回傳其品質。
public fun risky_mint(random: &Random, ctx: &mut TxContext): u8 {
    let mut generator = random.new_generator(ctx);
    let medal = mint_medal_impl(&mut generator, ctx);
    let quality = medal.quality;
    transfer::transfer(medal, ctx.sender());
    quality
}
```

沒有任何機制能阻止另一個模組包裝這個函式、檢查結果，並在結果不理想時中止（abort）。中止會回滾交易的所有效果，因此攻擊者只需付出 gas 的代價，就能「重新擲骰」——不斷重試直到獲勝：

```move
/// 攻擊者的模組。
module attacker::exploit;

entry fun re_roll(random: &Random, ctx: &mut TxContext) {
    let quality = book::randomness::risky_mint(random, ctx);

    // 不是 Gold？中止、回滾所有效果，
    // 然後在下一筆交易中重試。
    assert!(quality == 0);
}
```

值得注意的是，這並非硬性限制——`risky_mint` 函式是可以編譯通過的。Move linter 會用 `public_random` 警告標記出這種風險簽章，除非你非常清楚自己在做什麼，否則應該將它視為錯誤：

```
warning[Lint W99006]: Risky use of 'sui::random'
  │
  │ public fun risky_mint(random: &Random, ctx: &mut TxContext): u8 {
  │                               ^^^^^^^ 'public' function 'risky_mint' accepts 'Random' as a parameter
  │
  = Functions that accept 'sui::random::Random' as a parameter might be abused by attackers
    by inspecting the results of randomness
  = Non-public functions are preferred
```

Sui 在協定層級真正強制執行的，是交易組合方式：在一個可程式化交易區塊（programmable transaction block）中，使用 `Random` 的指令後面只能接著 `TransferObjects` 或 `MergeCoins` 指令。兩者都無法檢查值或根據值中止，這使得隨機性在設計上*無法被組合*：隨機擲骰的結果永遠無法在同一筆交易中被任何其他程式碼所操作。結果只能透過函式的效果來傳遞——例如轉移給呼叫者的 `Medal` 物件。

`entry` 函式仍然不便於測試：它需要完整的 `Random` 物件——一個需要花費力氣才能在測試中建立的共享物件。這就是為什麼實際邏輯放在一個獨立的、具有 `public(package)` 可見性的函式中，該函式接受 `RandomGenerator` 而非 `Random`：

- `entry` 函式只是一個薄薄的外殼：它建立產生器並將其傳遞下去；
- `public(package)` 函式包含邏輯，回傳一個值，並且可以在測試中直接呼叫——使用僅供測試的產生器，不需要 `Random` 物件。

請注意，內層函式同樣不能是 `public`——將 `RandomGenerator` 傳遞給不受信任的呼叫者，其危險程度與傳遞 `Random` 相同，因為呼叫者可以檢查結果並有條件地中止。Linter 對於帶有 `RandomGenerator` 參數的 `public` 函式同樣會發出警告。

## 從交易中呼叫 (Calling from a Transaction) {#calling-from-a-transaction}

要呼叫一個接受 `&Random` 的 entry 函式，請將位於 `0x8` 的 `Random` 物件作為引數傳入——如前所述，這個地址在每個網路上都相同。舉例來說，使用 Sui CLI：

```bash
sui client ptb \
    --move-call $PACKAGE_ID::randomness::mint_medal @0x8
```

由於前一節所描述的限制，該呼叫實際上必須是交易區塊中的最後一個指令——只有 `TransferObjects` 與 `MergeCoins` 指令可以接在它後面。

## 執行測試 (Testing) {#testing}

上述模式在測試中會帶來回報。`sui::random` 模組提供了僅供測試使用的函式，可以在不需要 `Random` 物件的情況下建立產生器：`new_generator_for_testing` 與 `new_generator_from_seed_for_testing`。帶種子（seeded）的產生器總是會產生相同的數值序列，這使得測試可重現——而由於不同的種子會產生不同的序列，你可以搜尋能讓測試進入特定分支的種子，以確定性的方式涵蓋每一種結果。不帶種子的產生器則適用於必須對任何結果都成立的屬性式檢查：

```move file=packages/samples/sources/programmability/randomness.move anchor=test_unit

```

若要測試 entry 函式本身——也就是交易實際執行時的完整流程——請使用 [Test Scenario](./../testing/test-scenario)，並用 `random::create_for_testing` 建立共享的 `Random` 物件。請注意，`Random` 物件只能由系統地址 `0x0` 建立與更新：

```move file=packages/samples/sources/programmability/randomness.move anchor=test_scenario

```

關於在測試中使用系統物件的更多細節，請參見[在測試中建立與使用系統物件](./../testing/using-system-objects)。

> 鏈上隨機性不應與 [`#[random_test]`](./../testing/random-test) 屬性混淆，後者是用於產生隨機測試輸入的編譯器功能。

## 限制 (Limitations) {#limitations}

鏈上隨機性在交易執行*之前*是不可預測的，但它並非秘密：一旦交易被提交，結果就會像鏈上其他一切一樣公開。這使得它非常適合公平的選擇機制——抽獎、戰利品表、配對、洗牌——但不適合隱藏資訊。玩家持有隱藏手牌的卡牌遊戲無法單靠 `Random` 物件來建構，還需要額外的密碼學技術。

其他限制則源自上述的安全規則：

- 隨機性在設計上是無法組合的：使用隨機性的函式必須是 `entry`，並且實際上是交易中最後一個有意義的指令，因此其結果無法在同一筆交易中被檢查或操作——結果只能透過效果（effects）傳遞，例如該函式建立或轉移的物件；
- 結果無法事先得知——交易的試跑（dry run）不會與實際執行的結果相符；
- 隨機性僅在交易中可用，沒有辦法「偷看」下一個值。

## 攻擊與緩解措施 (Attacks and Mitigations) {#attacks-and-mitigations}

即使正確封裝，仍然存在一類攻擊，需要由應用程式開發者負責：_條件性失敗（conditional failure）_ 攻擊。平台可以保證攻擊者無法選擇結果，但如果交易在輸掉時比贏得時更容易失敗（或反之），攻擊者仍然能佔到便宜——失敗的交易會回滾一切，等於獲得一次免費重試。

主要的變體是*基於 gas 的*攻擊。如果贏和輸的分支消耗不同數量的 gas，攻擊者就可以將 gas 預算設定在兩者成本之間：較便宜的分支會執行成功，而較昂貴的分支則會因 gas 不足錯誤而失敗，藉此撤銷不利的結果。類似的手法也可能依賴其他有限的資源，例如交易中新物件的數量或動態欄位的存取次數。

為了降低風險：

- 讓所有結果的 gas 成本盡可能接近——避免只在其中一個分支執行昂貴邏輯（在 `Medal` 範例中，每種結果都執行相同的工作）；
- 如果不同結果確實需要不同的處理，可將流程拆成兩筆交易：第一筆交易擲出隨機結果，並將原始結果儲存在物件中，每種結果的成本都相同；第二筆交易——一個不再存取 `Random` 的一般函式——則套用相應的後果；
- 永遠不要透過 `public` 函式暴露 `Random` 或 `RandomGenerator`，並且務必在使用它的函式內部建立一個全新的產生器。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的[鏈上隨機性](https://docs.sui.io/guides/developer/advanced/randomness-onchain)指南。
- [sui::random](https://docs.sui.io/references/framework/sui/random) 模組文件。
