---
description: Move 中的入口函式 (entry functions)：entry 修飾詞 (entry modifier) 如何將函式限制為僅限交易呼叫，以及其引數獲得的靜態燙手山芋保證 (static hot-potato guarantee)。
title: 入口函式 (Entry Functions)
keywords:
  - Move
  - Sui
  - Move tutorial
  - entry
  - functions
questions:
  - What is Entry Functions in Move?
  - How do I use Entry Functions in Move?
  - What is The Hot Potato Guarantee in Move?
  - What is The Rules in Move?
answer: 'Entry functions in Move: how the entry modifier restricts a function to transaction-only calls, and the static hot-potato guarantee its arguments receive in return.'
goal:
  description: 'Reader understands entry functions in Move: how the entry modifier restricts a function to transaction-only calls, and the static hot-potato guarantee its arguments receive in return'
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

# 入口函式 (Entry Functions) {#entry-functions}

[`entry`](./../move-basics/visibility#entry-modifier) 函式是一種特殊的可由交易呼叫的函式——它刻意 _限制_ 呼叫端的選項。如同 [可見性修飾詞](./../move-basics/visibility)章節所述，`entry` 並非可見性層級，也不是讓函式通常可從[交易](./../concepts/what-is-a-transaction)呼叫的方式——`public` 函式本來就可以，且 `public` 仍是預設值。`entry` 修飾詞只對 _非公開_ 函式有意義——私有或 `public(package)`——它建立的是一個雙向縮限契約的函式：

- _誰能呼叫它：_ 在自身模組（或套件）外部，此函式只能作為交易中的命令呼叫——其他套件無法包裝它、對其結果進行操作，或將其建構到更大的邏輯中；
- _此呼叫可與什麼結合：_ 傳遞給它的引數不得帶有同一筆交易中其他命令建立的義務——系統會檢查其行為是否如同 `entry` 函式是唯一的命令。

第一項限制直接源於可見性規則，並已在 Move 基礎中說明。本章描述第二項——關於引數的靜態保證及其背後規則。本內容需要熟悉[燙手山芋模式](./../programmability/hot-potato-pattern)、[能力](./../move-basics/abilities-introduction)，以及交易的結構，因此放在此處而非 Move 基礎。

## 燙手山芋保證 (The Hot Potato Guarantee) {#the-hot-potato-guarantee}

非 `public` `entry` 函式（私有或 `public(package)`）的引數不能與[燙手山芋](./../programmability/hot-potato-pattern)產生 _糾纏_——亦即型別同時不具有 `store` 與 `drop`，因而必須在交易結束前處理的值。實務上，這表示引數的行為如同 `entry` 函式是交易中唯一的命令：在呼叫 `entry` 函式後，任何先前命令都無法強制交易執行某種行為。

> 此保證會在交易開始執行前 _靜態_ 檢查。違反此保證的交易會驗證失敗，且不會執行。這些規則於 Sui v1.62 導入，取代先前限制更多的一組規則。

最典型的動機是 _閃電貸款_——借入必須在同一筆交易中償還的資金。簡化版的貸款方如下：

```move
module flash::loan;

use sui::balance::Balance;
use sui::sui::SUI;

public struct Bank has key {
    id: UID,
    holdings: Balance<SUI>,
}

/// 燙手山芋：沒有 `store`、沒有 `drop`。一旦發出，交易
/// 必須透過呼叫 `repay` 將其銷毀，否則無法成功。
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

開發者在撰寫接受 `Coin` 的 `entry` 函式時，可能想確保該代幣確實由傳送者「擁有」，而非向具有未償還義務的銀行借得。`entry` 規則正好提供此保證。

## 規則 (The Rules) {#the-rules}

驗證會追蹤有多少燙手山芋值尚未處理，以及它們可能影響哪些值。部分術語如下：

- _值_ 是交易命令的任何引數：交易輸入、前一個命令的結果，或 gas 代幣。
- 若值的型別同時不具有 `store` 與 `drop`，該值即為 _熱_ 值。這留下三種可能形狀：完全沒有能力的型別、只有 `copy` 的型別，或只有 `key` 的型別（型別不能同時具有 `key` 與 `copy`，因為 `sui::object::UID` 沒有 `copy`）。
- 每個值都屬於一個 _集團_——一組曾一同作為命令引數使用的值，以及該命令的結果。每個集團都會計算其尚未處理的熱值。

演算法依序走訪交易的命令：

1. 每個交易輸入一開始各自位於一個計數為零的集團。
2. 當值一同用於某個命令時——以值或參考方式——其集團會合併，並將計數相加。
3. 每個 _移入_ 命令的熱值都會使計數遞減（以值取得，而非複製）。
4. 若命令呼叫非 `public` 的 `entry` 函式，合併後集團的計數此時必須為零。請注意，這表示 `entry` 函式 _可以_ 接受熱值——它們只需是其集團中最後的熱值。
5. 命令的結果會加入合併後的集團，且每個熱結果都會使計數遞增。

讓我們實際看看。假設某模組具有下列函式：

```move
module book::example;

use sui::coin::Coin;
use sui::sui::SUI;

public struct HotPotato()

public fun hot(coin: &mut Coin<SUI>): HotPotato { /* ... */ HotPotato() }
public fun cool(potato: HotPotato) { let HotPotato() = potato; }

entry fun spend(coin: &mut Coin<SUI>) { /* ... */ }
```

下列交易會遭拒絕。對 `hot` 的呼叫產生了一個燙手山芋，因此呼叫 `spend` 時，`Input(0)` 所在的集團具有尚未處理的熱值：

```text
// 無效交易
// 輸入 0：Coin<SUI>
// 集團：{ Input(0) } => 0
0: book::example::hot(Input(0));
// 集團：{ Input(0), Result(0) } => 1
1: book::example::spend(Input(0)); // 無效，Input(0) 的集團計數 > 0
2: book::example::cool(Result(0));
```

先銷毀燙手山芋可使計數回到零，相同的呼叫便會有效：

```text
// 有效交易
// 輸入 0：Coin<SUI>
// 集團：{ Input(0) } => 0
0: book::example::hot(Input(0));
// 集團：{ Input(0), Result(0) } => 1
1: book::example::cool(Result(0));
// 集團：{ Input(0) } => 0
2: book::example::spend(Input(0)); // 有效！Input(0) 的集團計數為 0
```

集團讓這項規則更加穩固：糾纏會透過 _任何_ 共用使用方式傳播，而不只是直接使用。使用 `flash::loan` 模組時，下方的 `Coin` 是由借出的 `Balance` 建立，且從未直接接觸 `Loan`——但它們位於相同集團中，因此在償還貸款前，無法將它傳遞給 `entry` 函式：

```text
// 無效交易
// 輸入 0：flash::loan::Bank
// 輸入 1：u64
// 集團：{ Input(0) } => 0，{ Input(1) } => 0
0: flash::loan::issue(Input(0), Input(1));
// 集團：{ Input(0), NestedResult(0,0), NestedResult(0,1) } => 1
1: sui::coin::from_balance(NestedResult(0,0));
// 集團：{ Input(0), NestedResult(0,1), Result(1) } => 1
2: book::example::spend(Result(1)); // 無效，Result(1) 的集團計數 > 0
3: sui::coin::into_balance(Result(1));
4: flash::loan::repay(Input(0), NestedResult(0,1), Result(3));
```

若在呼叫 `spend` 前償還貸款，該交易即可通過驗證。

## 共用物件 (Shared Objects) {#shared-objects}

有一個特殊情況：當命令以值接受 _共用物件_ 時，合併後集團的計數會設為無限大。非 `public` 的 `entry` 函式仍可直接以值接受共用物件，但不能接受其集團先前曾與共用物件互動的值。

原因是以值接受的共用物件，能像燙手山芋一樣強制交易其餘部分執行某種行為：它無法被包裝或轉移，因此必須在交易結束前重新設為共用或刪除。但不同於燙手山芋，這項義務無法從型別的能力中看出，因此驗證必須採取最保守的假設。

以值接受的 [Party 物件](./../appendix/transfer-functions)也受相同限制，但適用情況比共用物件更窄。

> 由於規則在執行前靜態套用，因此刻意採取保守判斷：動態檢查可以更精確，但靜態檢查更容易描述且可據以依賴。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 基礎中的 [可見性修飾詞](./../move-basics/visibility)，了解 `entry` 的基礎。
- Move 參考文件中的 [可見性](./../../reference/functions#visibility)。
