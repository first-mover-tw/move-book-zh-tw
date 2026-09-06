---
description: Sui 鏈上隨機性 (Onchain randomness)：使用 Random 共用物件，在 Move 智慧合約中產生安全的隨機值
title: 鏈上隨機性 (Onchain Randomness)
keywords:
  - Move
  - Sui
  - Move tutorial
  - onchain
  - randomness
questions:
  - What is Onchain Randomness in Move?
  - How do I use Onchain Randomness in Move?
  - What is The Random Object in Move?
  - What is Using Randomness in Move?
answer: 'Onchain randomness in Sui: generate secure random values in Move smart contracts using the Random shared object.'
goal:
  description: 'Reader understands onchain randomness in Sui: generate secure random values in Move smart contracts using the Random shared object'
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

# 鏈上隨機性 (Onchain Randomness) {#onchain-randomness}

對區塊鏈而言，隨機性是個出乎意料困難的問題。執行必須具備確定性——每個驗證者都必須執行交易並得出完全相同的結果——而且每個輸入都是公開的。看似隨機的值，例如[目前時間](./epoch-and-time)、epoch 或交易摘要，都是可預測的；更糟的是，還可能受到傳送者或驗證者影響。當涉及金錢時，「看起來隨機」並不足夠：任何可預測或可偏誤的隨機性來源，最終都會遭到利用。

為了解決這個問題，Sui 會*共同*產生隨機性：每個 epoch 開始時，驗證者會執行分散式金鑰產生協定，接著在每次共識提交時共同產生新的隨機值，沒有任何單一方——甚至驗證者——能事先得知該值。此值會寫入 `Random` 系統物件，並提供給 Move 程式使用。

## `Random` 物件 (The `Random` Object) {#the-random-object}

`Random` 物件定義於 `sui::random` 模組，並具有保留地址 `0x8`（請參閱[保留地址](./../appendix/reserved-addresses)）。此地址在每個網路上都相同——localnet、devnet、testnet 與 mainnet——因此可以安全地硬編碼於應用程式與用戶端原始碼中。如同 [Clock](./epoch-and-time#time) 物件，它是無法以可變方式存取的共享物件——嘗試透過可變參考取得它的交易將會失敗。這可讓隨機性被平行存取，並保護全域狀態免受竄改。

```move
module sui::random;

/// 儲存全域隨機性狀態的單例共享物件。
/// 實際狀態儲存在具版本的內部欄位中。
public struct Random has key {
    id: UID,
    inner: Versioned,
}
```

該物件的內部狀態會由系統在每次共識提交時更新，其不可預測性不會在 epoch 期間降低。

## 使用隨機性 (Using Randomness) {#using-randomness}

不會直接從 `Random` 物件讀取隨機性。相反地，交易會建立 `RandomGenerator`——衍生自全域狀態且為該交易專屬的區域隨機值來源。產生器提供常見需求的方法：布林值、各種大小的整數、範圍內的整數（界限值皆包含在內）、原始位元組，以及向量的隨機重排：

```move file=packages/samples/sources/programmability/randomness.move anchor=generator

```

典型用法如下：函式接收 `&Random`、使用 `new_generator` 建立產生器，並用它產生所需數量的值。以下範例鑄造具有隨機品質的 `Medal`——有 10% 機率為 Gold、30% 為 Silver，以及 60% 為 Bronze：

```move file=packages/samples/sources/programmability/randomness.move anchor=main

```

此範例刻意拆分為兩個函式，而這種拆分是建議用於組織使用隨機性原始碼的方式。以下說明原因。

## 正確封裝隨機性 (Encapsulating Randomness Correctly) {#encapsulating-randomness-correctly}

`mint_medal` 函式宣告為私有的 [entry](./../move-basics/visibility) 函式——它可由交易呼叫，但不能由其他模組呼叫。這是刻意設計，也是使用隨機性最重要的規則：

> 接收 `&Random`（或 `RandomGenerator`）作為參數的函式絕不可為 `public`。這包含 `public entry`——`public entry` 函式仍可由其他模組呼叫。處理隨機性時，一律使用私有的 `entry` 函式。

為了了解原因，以下違反此規則。這是同一函式的變體，該函式為 `public`，並回傳擲骰結果：

```move
/// 鑄造一個 `Medal`、將其轉移給呼叫者，並回傳品質。
public fun risky_mint(random: &Random, ctx: &mut TxContext): u8 {
    let mut generator = random.new_generator(ctx);
    let medal = mint_medal_impl(&mut generator, ctx);
    let quality = medal.quality;
    transfer::transfer(medal, ctx.sender());
    quality
}
```

沒有任何機制可阻止另一個模組包裝此函式、檢查結果，並在結果不理想時中止。中止會回復交易的所有效果，因此攻擊者只需支付 gas，即可「重新擲骰」——持續重試直到獲勝：

```move
/// 攻擊者的模組。
module attacker::exploit;

entry fun re_roll(random: &Random, ctx: &mut TxContext) {
    let quality = book::randomness::risky_mint(random, ctx);

    // 不是 Gold？中止、回復所有效果，並在下一筆交易中再次嘗試。
    assert!(quality == 0);
}
```

重要的是，這並非硬性限制——`risky_mint` 函式可以編譯。Move linter 會以 `public_random` 警告標示此具風險的簽章，除非你完全清楚自己正在做什麼，否則應將其視為錯誤：

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

Sui 確實會在協定層級強制執行的是交易組合：在可程式化交易區塊中，使用 `Random` 的命令後方只能接續 `TransferObjects` 或 `MergeCoins` 命令。兩者皆無法檢查值，或依據該值中止，因此隨機性在設計上*不可組合*：隨機擲骰的結果永遠無法由同一筆交易中的任何其他原始碼採取動作。結果僅會透過函式效果交付，例如轉移給呼叫者的 `Medal` 物件。

`entry` 函式仍不便於測試：它需要完整的 `Random` 物件——建立測試時需要額外作業的共享物件。因此，實際邏輯位於具有 `public(package)` 可見性的獨立函式中，該函式接收 `RandomGenerator` 而非 `Random`：

- `entry` 函式是薄型外觀：它建立產生器並將其傳遞出去；
- `public(package)` 函式包含邏輯、回傳值，且可在測試中直接呼叫——搭配僅供測試的產生器，無需 `Random` 物件。

請注意，內部函式同樣不可為 `public`——將 `RandomGenerator` 傳給不受信任的呼叫者，與傳遞 `Random` 一樣危險，因為呼叫者可以檢查結果並有條件地中止。linter 同樣會針對參數為 `RandomGenerator` 的 `public` 函式提出警告。

## 從交易呼叫 (Calling from a Transaction) {#calling-from-a-transaction}

若要呼叫預期接收 `&Random` 的 entry 函式，請將位於 `0x8` 的 `Random` 物件作為引數傳入——如前所述，此地址在每個網路上都相同。例如，使用 Sui CLI：

```bash
sui client ptb \
    --move-call $PACKAGE_ID::randomness::mint_medal @0x8
```

由於前一節所述的限制，此呼叫實際上必須是交易區塊中的最後一個命令——後方僅可接續 `TransferObjects` 與 `MergeCoins` 命令。

## 測試 (Testing) {#testing}

上述模式在測試中很有價值。`sui::random` 模組提供僅供測試使用的函式，可在沒有 `Random` 物件的情況下建立產生器：`new_generator_for_testing` 與 `new_generator_from_seed_for_testing`。具種子的產生器總是會產生相同的值序列，使測試可重現；由於不同種子會產生不同序列，你可以搜尋使測試進入特定分支的種子，以確定性方式涵蓋每一種結果。未設定種子的產生器適用於必須對任意結果皆成立的屬性風格檢查：

```move file=packages/samples/sources/programmability/randomness.move anchor=test_unit

```

若要測試 entry 函式本身——如同交易執行時的完整流程——請使用[測試情境](./../testing/test-scenario)，並透過 `random::create_for_testing` 建立共享的 `Random` 物件。請注意，`Random` 物件僅能由系統地址 `0x0` 建立與更新：

```move file=packages/samples/sources/programmability/randomness.move anchor=test_scenario

```

如需更多使用系統物件進行測試的詳細資訊，請參閱[在測試中建立及使用系統物件](./../testing/using-system-objects)。

> 鏈上隨機性不應與 [`#[random_test]`](./../testing/random-test) 屬性混淆，後者是用於產生隨機測試輸入的編譯器功能。

## 限制 (Limitations) {#limitations}

鏈上隨機性在交易執行*之前*不可預測，但它並非祕密：交易一旦提交，結果就會公開，如同鏈上的其他一切。這使其非常適合公平選擇——抽獎、掉落物表、配對、隨機重排——但不適合隱藏資訊。玩家持有隱藏手牌的紙牌遊戲無法僅建立於 `Random` 物件之上，而需要額外的密碼學技術。

其他限制源自上述安全規則：

- 隨機性在設計上不可組合：使用它的函式必須是 `entry`，且實際上是交易中的最後一個有意義命令，因此其結果無法在該交易中被檢查或採取動作——結果會透過效果交付，例如函式建立或轉移的物件；
- 結果無法事先得知——交易的模擬執行不會與實際執行相符；
- 隨機性僅於交易中可用，無法「偷看」下一個值。

## 攻擊與緩解措施 (Attacks and Mitigations) {#attacks-and-mitigations}

即使正確封裝，仍有一類攻擊存在，且是應用程式開發者的責任：*條件式失敗*攻擊。平台保證攻擊者無法選擇結果，但如果交易可在輸掉時比贏得時更常失敗（或反之），攻擊者仍可取得優勢——失敗的交易會回復一切，因而獲得免費重試機會。

主要變體是*以 gas 為基礎*的攻擊。若獲勝與失敗分支消耗不同數量的 gas，攻擊者可將 gas 預算設在兩者成本之間：成本較低的分支完成，而成本較高的分支因 gas 耗盡錯誤失敗，從而撤銷不利結果。類似技巧也可依賴其他受限資源，例如交易中新物件數量或動態欄位存取次數。

為降低風險：

- 讓所有結果的 gas 成本盡可能接近——避免只在其中一個分支執行昂貴邏輯（在 `Medal` 範例中，每個結果皆執行相同工作）；
- 若不同結果確實需要不同處理，請將流程拆為兩筆交易：第一筆交易抽取隨機性，並將原始結果儲存於物件中，且每個結果使用相同成本；第二筆交易則是一般函式，不再接觸 `Random`，負責套用後果；
- 絕不可透過 `public` 函式暴露 `Random` 或 `RandomGenerator`，並應一律在使用它的函式內建立新的產生器。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的 [Onchain Randomness](https://docs.sui.io/guides/developer/advanced/randomness-onchain) 指南。
- [sui::random](https://docs.sui.io/references/framework/sui/random) 模組文件。
