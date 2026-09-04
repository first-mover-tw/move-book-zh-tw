---
description: Move 中的見證者模式 (Witness pattern)：透過結構體實例化 (struct instantiation) 證明型別所有權 (type ownership)，以在 Sui 智慧合約 (smart contracts) 中實現型別安全授權 (type-safe authorization)。
title: 模式：見證人 (Witness)
keywords:
  - Move
  - Sui
  - Move tutorial
  - pattern
  - witness
  - design patterns
  - witness pattern
questions:
  - 'What is Pattern: Witness in Move?'
  - 'How do I use Pattern: Witness in Move?'
  - What is Witness in Move in Move?
  - What is Instantiating a Generic Type in Move?
answer: 'The Witness pattern in Move: prove type ownership through struct instantiation for type-safe authorization in Sui smart contracts.'
goal:
  description: 'Reader understands the Witness pattern in Move: prove type ownership through struct instantiation for type-safe authorization in Sui smart contracts'
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

# 模式：見證 (Pattern: Witness) {#pattern-witness}

見證是一種透過建構證據來證明事實的模式。在程式設計的情境中，見證是藉由提供一個只有在該性質成立時才能建構的值，來證明系統具有特定性質的方法。

## Move 中的見證 (Witness in Move) {#witness-in-move}

在 [Struct](./../move-basics/struct) 章節中，我們說明了結構只能由定義它的模組建立——或稱為 _packed_。因此，在 Move 中，模組透過建構型別來證明其擁有該型別。這是 Move 最重要的模式之一，並廣泛用於泛型型別具現化與授權。

實務上，若要使用見證，必須有一個函式將見證作為引數接受。在下方範例中，`new` 函式需要一個 `T` 型別的見證，以建立 `Instance<T>`。

> 見證通常會被捨棄而非儲存，因此這類函式通常要求見證型別具有 [drop](./../move-basics/drop-ability) 能力。

```move file=packages/samples/sources/programmability/witness-pattern-2.move anchor=main

```

建構 `Instance<T>` 的唯一方式，是使用型別 `T` 的執行個體呼叫 `new` 函式。這是 Move 中見證模式的基本範例。提供見證的模組通常會有對應的實作，例如下方的 `book::witness_source` 模組：

```move file=packages/samples/sources/programmability/witness-pattern-3.move anchor=source

```

結構 `W` 的執行個體會傳入 `new_instance` 函式以建立 `Instance<W>`，從而證明 `book::witness_source` 模組擁有型別 `W`。

## 泛型型別具現化 (Instantiating a Generic Type) {#instantiating-a-generic-type}

見證允許使用具體型別來具現化泛型型別。若模組提供這項能力，這對於繼承型別的相關行為，並選擇擴充這些行為相當實用。

```move
module sui::balance;

/// T 的供應量。用於鑄造與銷毀。
/// 在 `Coin` 模組中包裝為 `TreasuryCap`。
public struct Supply<phantom T> has store {
    value: u64,
}

/// 為型別 T 建立新的供應量。
public fun create_supply<T: drop>(_: T): Supply<T> {
    Supply { value: 0 }
}

/// 取得 `Supply` 值。
public fun supply_value<T>(supply: &Supply<T>): u64 {
    supply.value
}
```

在上述範例中，其取自 [Sui Framework](./sui-framework) 的 [`balance` 模組][balance-framework]，`Supply` 是一個泛型結構，只能藉由提供型別 `T` 的見證來建構。見證會以值的方式取得並 _捨棄_，因此 `T` 必須具有 [drop](./../move-basics/drop-ability) 能力。

[balance-framework]: https://docs.sui.io/references/framework/sui/balance

具現化後的 `Supply<T>` 可用於鑄造新的 `Balance<T>`，其中 `T` 是供應量的型別。

```move
module sui::balance;

const EOverflow: u64 = 1;

/// 可儲存的餘額——Coin 型別的內部結構。
/// 可用於儲存不需要 key 能力的代幣。
public struct Balance<phantom T> has store {
    value: u64,
}

/// 將供應量增加 `value`，並以此值建立新的 `Balance<T>`。
public fun increase_supply<T>(self: &mut Supply<T>, value: u64): Balance<T> {
    assert!(value <= (std::u64::max_value!() - self.value), EOverflow);
    self.value = self.value + value;
    Balance { value }
}
```

這是 Sui 上通常建立新貨幣的方式：`TreasuryCap`——本章稍早說明的 [能力](./capability)——是以見證具現化的 `Supply<T>` 包裝器。

## 使用見證進行授權 (Authorization with Witness) {#authorization-with-witness}

具現化型別並非見證的唯一用途：任何函式都可以要求見證，使得只有定義 `T` 的模組能夠呼叫它。下方模組實作了泛型 `RegulatedCoin`，其中具特權的操作——`mint`、`burn` 與 `transfer`——需要見證，而共用功能——`join`——則對所有人開放：

```move file=packages/samples/sources/programmability/witness-pattern.move anchor=regulated_coin

```

定義見證型別並呼叫 `mint` 的模組可取得自己的受監管貨幣：只有它能決定如何——以及是否——公開其代幣的鑄造、銷毀與轉移功能，而基礎模組則實作所有這類貨幣共用的邏輯。

見證的這種用法與 [Capability](./capability) 模式相近，但有一項重要差異：能力是一種物件，因此它會授權擁有它的人——即帳戶；見證只能由定義它的模組建構，因此它會授權原始碼。使用見證的授權在撰寫原始碼時便已決定，不需要儲存，也無法轉移。

## 一次性見證 (One Time Witness) {#one-time-witness}

雖然結構可以建立任意次數，但有些情況下必須保證結構只能建立一次。為此，Sui 提供「一次性見證」——只能使用一次的特殊見證。我們會在[下一節](./one-time-witness)中更詳細說明。

> 標準函式庫也提供此證明的現成形式：
> [Internal Permit](./../move-basics/internal-permit)。`internal::Permit<T>` 可證明呼叫已獲定義 `T` 的模組授權——函式庫無須設計自訂見證型別，或要求 `T` 本身具有 `drop`。

## 總結 (Summary) {#summary}

- 見證是一種透過建構證明來驗證特定性質的模式。
- 在 Move 中，模組透過建構型別來證明其擁有該型別。
- 見證常用於泛型型別具現化與授權。

## 後續步驟 (Next Steps) {#next-steps}

在下一節中，我們將學習 [一次性見證](./one-time-witness) 模式。
