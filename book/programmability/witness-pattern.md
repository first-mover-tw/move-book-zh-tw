---
description: 'The Witness pattern in Move: prove type ownership through struct instantiation for type-safe authorization in Sui smart contracts.'
---

# 模式：見證 (Pattern: Witness)

見證 (Witness) 是一種透過建構證明來證實存在性的模式。在程式設計的語境下，見證是一種透過提供一個「只有在某種屬性成立時才能被建構」的數值，來證明該系統具有某種屬性的方式。

## Move 中的見證

在 [結構 (Struct)](./../move-basics/struct) 章節中，我們展示了結構只能由定義它的模組來建立（或稱之為「封箱」，pack）。因此，在 Move 中，一個模組透過建構某種類型來證明對該類型的所有權。這是 Move 中最重要的模式之一，廣泛用於泛型類型的實例化和授權。

實際操作上，要使用見證，必須有一個預期接收見證作為參數的函式。在下面的範例中，`new` 函式預期接收一個 `T` 類型的見證來建立一個 `Instance<T>` 執行個體。

> 見證結構通常不會被存儲，因此該函式可能要求該類型具有 [Drop](./../move-basics/drop-ability) 能力。

```move
module book::witness;

/// 一個需要見證才能建立的結構。
public struct Instance<T> { t: T }

/// 使用提供的 T 建立一個新的 `Instance<T>` 執行個體。
public fun new<T>(witness: T): Instance<T> {
    Instance { t: witness }
}
```

建構 `Instance<T>` 的唯一方法是呼叫 `new` 函式並傳入類型 `T` 的執行個體。這是 Move 中見證模式的一個基本範例。提供見證的模組通常具有相應的實作，如下面的 `book::witness_source` 模組：

```move
module book::witness_source;

use book::witness::{Self, Instance};

/// 用作見證的結構。
public struct W {}

/// 建立一個新的 `Instance<W>` 執行個體。
public fun new_instance(): Instance<W> {
    witness::new(W {})
}
```

結構 `W` 的執行個體被傳入 `new_instance` 函式以建立 `Instance<W>`，從而證明 `book::witness_source` 模組擁有了類型 `W`。

## 實例化泛型類型 (Instantiating a Generic Type)

見證允許使用具體類型來實例化泛型類型。如果模組提供了相應的能力，這對於從該類型繼承相關行為並擴展它們非常有用。

```move
module sui::balance;

/// T 的供應量 (Supply)。用於鑄造和銷毀。
public struct Supply<phantom T> has store {
    value: u64,
}

/// 使用提供的見證為類型 T 建立新的供應量。
public fun create_supply<T: drop>(_w: T): Supply<T> {
    Supply { value: 0 }
}

/// 獲取 `Supply` 的數值。
public fun supply_value<T>(supply: &Supply<T>): u64 {
    supply.value
}
```

在上面的範例（借用自 [Sui 框架](./sui-framework) 的 [`balance` 模組][balance-framework]）中，`Supply` 是一个泛型結構，只能透過提供類型 `T` 的見證來建構。見證按值接收並被「丟棄」——因此 `T` 必須具有 [drop](./../move-basics/drop-ability) 能力。

[balance-framework]: https://docs.sui.io/references/framework/sui/balance

實例化後的 `Supply<T>` 之後可以用於鑄造新的 `Balance<T>`，其中 `T` 是該供應量的類型。

```move
module sui::balance;

const EOverflow: u64 = 0;

/// 可存儲的餘額 (Balance)。
public struct Balance<phantom T> has store {
    value: u64,
}

/// 將供應量增加 `value` 並以此數值建立新的 `Balance<T>`。
public fun increase_supply<T>(self: &mut Supply<T>, value: u64): Balance<T> {
    assert!(value < (std::u64::max_value!() - self.value), EOverflow);
    self.value = self.value + value;
    Balance { value }
}
```

## 一次性見證 (One Time Witness)

雖然結構可以被建立任意次數，但在某些情況下，我們需要保證結構僅被建立一次。為此，Sui 提供了一次性見證 (One-Time Witness) —— 一種特殊的、只能使用一次的見證。我們將在 [下一節](./one-time-witness) 中詳細介紹。

## 總結

- 見證 (Witness) 是一種透過建構證明來證實某種屬性的模式。
- 在 Move 中，一個模組透過建構類型的執行個體來證明對該類型的所有權。
- 見證常用於泛型類型的實例化和授權。

## 下一步

在下一節中，我們將學習 [一次性見證 (One Time Witness)](./one-time-witness) 模式。
