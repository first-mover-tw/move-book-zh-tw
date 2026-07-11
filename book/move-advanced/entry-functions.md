---
description:
  Move 中的入口函式 (entry function)：entry 修飾詞如何限制函式只能透過交易呼叫，以及其引數 (argument)
  因此獲得的靜態燙手山芋保證 (hot-potato guarantee)。
---

# 入口函式 (Entry Functions) {#entry-functions}

一個 [`entry`](./../move-basics/visibility#entry-modifier) 函式是一種特殊的可交易呼叫函式——它會刻意*限制*呼叫者的選項。如
[可見性修飾詞 (Visibility Modifiers)](./../move-basics/visibility) 一章所述，`entry` 不是一種可見性層級，也不是讓函式能夠從
[交易 (transaction)](./../concepts/what-is-a-transaction) 中被呼叫的常規方式——`public` 函式本來就已經可以被呼叫，而 `public`
仍然是預設值。`entry` 修飾詞只在*非 public* 函式上才有意義——私有函式或
`public(package)` 函式——它所建立的是一個具有收窄合約（narrowed contract）的函式，方向有兩個：

- *誰能呼叫它：*在自己的模組（或套件）之外，這個函式只能作為交易中的一個命令被呼叫——沒有其他套件能包裝它、對它的結果進行操作，或將它組合進更大的邏輯中；
- *呼叫能與什麼組合：*傳入的引數必須不受同一筆交易中其他命令所建立的義務所牽連——系統會檢查它們的行為，就像該 `entry`
  函式是這筆交易中唯一的命令一樣。

第一項限制直接來自可見性規則，已在 Move 基礎篇中介紹過。本章描述的是第二項——關於引數的靜態保證，以及背後的規則。這部分內容需要熟悉
[熱土豆模式 (hot potato pattern)](./../programmability/hot-potato-pattern)、
[能力 (abilities)](./../move-basics/abilities-introduction)，以及交易的結構方式，這也是為什麼它被放在這裡而不是 Move 基礎篇的原因。

## 熱土豆保證 (The Hot Potato Guarantee) {#the-hot-potato-guarantee}

非 `public` 的 `entry` 函式（無論是私有的還是 `public(package)`）的引數，不能與
[熱土豆 (hot potato)](./../programmability/hot-potato-pattern)——一種型別既沒有 `store` 也沒有 `drop`，因此必須在交易結束前被處理掉的值——有所*糾纏（entangled）*。
在實務上，這代表引數的行為就像該 `entry` 函式是交易中唯一的命令一樣：在呼叫該 `entry` 函式之後，之前的命令都無法對交易的行為強加影響。

> 這項保證是在交易開始執行*之前*以靜態方式檢查的。違反此規則的交易會驗證失敗，不會被執行。這些規則是在 Sui v1.62 引入的，
> 取代了先前一套更為嚴格的規則。

典型的動機是*閃電貸 (flash loan)*——借出的資金必須在同一筆交易內償還。一個簡化版的放款方看起來像這樣：

```move
module flash::loan;

use sui::balance::Balance;
use sui::sui::SUI;

public struct Bank has key {
    id: UID,
    holdings: Balance<SUI>,
}

/// 一個熱土豆：沒有 `store`，沒有 `drop`。一旦被發出，
/// 交易在它被 `repay` 銷毀之前都無法成功。
public struct Loan {
    amount: u64,
}

public fun issue(bank: &mut Bank, amount: u64): (Balance<SUI>, Loan) {
    assert!(bank.holdings.value() >= amount);
    let loaned = bank.holdings.split(amount);
    (loaned, Loan { amount })
}

public fun repay(bank: &mut Bank, loan: Loan, repayment: Balance<SUI>) {
    let Loan { amount } = loan;
    assert!(repayment.value() == amount);
    bank.holdings.join(repayment);
}
```

一個撰寫接受 `Coin` 的 `entry` 函式的開發者，可能會想確保這個 coin 真的是被發送者「擁有」的，而不是從這樣一個
還有未償還義務的 bank 借來的。`entry` 規則正好提供了這樣的保證。

## 規則 (The Rules) {#the-rules}

驗證機制會追蹤有多少個熱土豆值處於未結清狀態，以及它們可能影響哪些值。以下是一些術語：

- 一個*值 (value)*是交易命令的任何引數：一個交易輸入、前一個命令的結果，或是 gas coin。
- 若一個值的型別既沒有 `store` 也沒有 `drop`，該值就是*熱的 (hot)*。這樣就剩下三種可能的形狀：完全沒有任何能力的型別、
  只有 `copy` 的型別，或只有 `key` 的型別（一個型別不能同時擁有 `key` 和 `copy`，因為 `sui::object::UID` 沒有
  `copy`）。
- 每個值都屬於一個*集團 (clique)*——一群曾被一起用作某個命令引數的值，加上該命令的結果。每個集團都會計算其未結清的熱值數量。

演算法會依序走訪交易中的命令：

1. 每個交易輸入都以計數為零的方式，開始於自己獨立的集團中。
2. 當多個值被一起用於某個命令中——無論是傳值還是傳參考——它們的集團會被合併，計數也會相加。
3. 每有一個熱值被*移動 (moved)*進該命令（以傳值方式取得，而非複製），計數就會遞減。
4. 若該命令呼叫的是一個非 `public` 的 `entry` 函式，此時合併後集團的計數必須為零。請注意，這代表一個 `entry` 函式*可以*
   接受熱值——只要它們是所在集團中最後的熱值即可。
5. 該命令的結果會加入合併後的集團，且每有一個熱結果，計數就會遞增。

讓我們實際走一遍。假設有一個模組包含以下函式：

```move
module book::example;

use sui::coin::Coin;
use sui::sui::SUI;

public struct HotPotato()

public fun hot(coin: &mut Coin<SUI>): HotPotato { /* ... */ HotPotato() }
public fun cool(potato: HotPotato) { let HotPotato() = potato; }

entry fun spend(coin: &mut Coin<SUI>) { /* ... */ }
```

下面這筆交易會被拒絕。對 `hot` 的呼叫產生了一個熱土豆，因此當 `spend` 被呼叫時，`Input(0)`
所在的集團仍有未結清的熱值：

```text
// 無效交易
// Input 0: Coin<SUI>
// cliques: { Input(0) } => 0
0: book::example::hot(Input(0));
// cliques: { Input(0), Result(0) } => 1
1: book::example::spend(Input(0)); // 無效，Input(0) 所在集團的計數 > 0
2: book::example::cool(Result(0));
```

先銷毀熱土豆會讓計數重新歸零，同樣的呼叫就會變成有效：

```text
// 有效交易
// Input 0: Coin<SUI>
// cliques: { Input(0) } => 0
0: book::example::hot(Input(0));
// cliques: { Input(0), Result(0) } => 1
1: book::example::cool(Result(0));
// cliques: { Input(0) } => 0
2: book::example::spend(Input(0)); // 有效！Input(0) 所在集團的計數為 0
```

集團正是讓這條規則穩固的原因：糾纏會透過*任何*共用的使用方式擴散，而不僅限於直接的方式。以 `flash::loan`
模組為例，下面的 `Coin` 是從借來的 `Balance` 建立的，從未直接接觸過 `Loan`——但它仍屬於同一個集團，
在貸款償還之前無法傳入該 `entry` 函式：

```text
// 無效交易
// Input 0: flash::loan::Bank
// Input 1: u64
// cliques: { Input(0) } => 0, { Input(1) } => 0
0: flash::loan::issue(Input(0), Input(1));
// cliques: { Input(0), NestedResult(0,0), NestedResult(0,1) } => 1
1: sui::coin::from_balance(NestedResult(0,0));
// cliques: { Input(0), NestedResult(0,1), Result(1) } => 1
2: book::example::spend(Result(1)); // 無效，Result(1) 所在集團的計數 > 0
3: sui::coin::into_balance(Result(1));
4: flash::loan::repay(Input(0), NestedResult(0,1), Result(3));
```

如果貸款在呼叫 `spend` 之前就已償還，這筆交易就會通過驗證。

## 共享物件 (Shared Objects) {#shared-objects}

有一種特殊情況：當一個命令以傳值方式接受一個*共享物件 (shared object)*時，合併後集團的計數會被設為無窮大。
一個非 `public` 的 `entry` 函式仍然可以直接以傳值方式接受一個共享物件，但不能接受一個先前所在集團曾與共享物件互動過的值。

原因在於，以傳值方式取得的共享物件可以像熱土豆一樣，強迫交易其餘部分的行為：它無法被包裝或轉移，因此在交易結束前
必須被重新共享或刪除。但與熱土豆不同的是，這項義務並不會反映在型別的能力上，因此驗證機制必須假設最壞的情況。

以傳值方式取得的 [Party 物件](./../appendix/transfer-functions) 也受到相同的限制，
不過適用範圍比共享物件更窄。

> 由於這些規則是在執行前以靜態方式套用的，因此它們刻意採取悲觀態度：動態檢查可以更精確，
> 但靜態檢查更容易描述，也更容易依賴。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 基礎篇中的 [可見性修飾詞 (Visibility Modifiers)](./../move-basics/visibility)，介紹 `entry` 的基本概念。
- Move 參考手冊中的 [可見性 (Visibility)](./../../reference/functions#visibility)。
