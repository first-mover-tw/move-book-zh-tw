---
description:
  Move 中的見證者模式 (Witness Pattern)：透過結構體實例化 (struct instantiation) 證明型別所有權，用於
  Sui 智能合約中的型別安全授權。
---

# 樣式：見證 (Pattern: Witness) {#pattern-witness}

見證是一種透過建構證據來證明事實的樣式。在程式設計的情境中，見證是一種透過提供一個值來證明系統某項屬性的方法，而該值只有在該屬性成立時才能被建構出來。

## Move 中的見證 (Witness in Move) {#witness-in-move}

在 [Struct](./../move-basics/struct) 章節中，我們展示過一個 struct 只能由定義它的模組建立——或稱為 _打包（packed）_。因此，在 Move 中，模組透過建構型別來證明對該型別的擁有權。這是 Move 中最重要的樣式之一，廣泛應用於泛型型別實例化與授權。

實務上，要使用見證，必須有一個函式預期接收見證作為引數。在下面的範例中，`new` 函式預期接收一個 `T` 型別的見證，以建立 `Instance<T>`。

> 見證通常會被捨棄而非儲存，這也是為什麼此類函式通常要求見證型別具備 [drop](./../move-basics/drop-ability) 能力的原因。

```move file=packages/samples/sources/programmability/witness-pattern-2.move anchor=main

```

建構 `Instance<T>` 的唯一方法是以型別 `T` 的實例呼叫 `new` 函式。這是 Move 中見證樣式的基本範例。提供見證的模組通常會有對應的實作，如下面的 `book::witness_source` 模組：

```move file=packages/samples/sources/programmability/witness-pattern-3.move anchor=source

```

struct `W` 的實例被傳入 `new_instance` 函式以建立 `Instance<W>`，藉此證明模組 `book::witness_source` 擁有型別 `W`。

## 實例化泛型型別 (Instantiating a Generic Type) {#instantiating-a-generic-type}

見證讓泛型型別可以用具體型別實例化。這對於從該型別繼承相關行為並在模組提供能力時選擇性擴充它們，非常有用。

```move
module sui::balance;

/// 一種 T 的 Supply。用於鑄造與銷毀。
/// 在 `Coin` 模組中被包裝成 `TreasuryCap`。
public struct Supply<phantom T> has store {
    value: u64,
}

/// 為型別 T 建立一個新的 supply。
public fun create_supply<T: drop>(_: T): Supply<T> {
    Supply { value: 0 }
}

/// 取得 `Supply` 的值。
public fun supply_value<T>(supply: &Supply<T>): u64 {
    supply.value
}
```

在上面借用自 [Sui Framework](./sui-framework) 的 [`balance` 模組][balance-framework] 的範例中，`Supply` 是一個泛型 struct，只能透過提供型別 `T` 的見證來建構。見證是以值的方式取得並被 _捨棄_——因此 `T` 必須具備 [drop](./../move-basics/drop-ability) 能力。

[balance-framework]: https://docs.sui.io/references/framework/sui/balance

實例化後的 `Supply<T>` 接著可用來鑄造新的 `Balance<T>`，其中 `T` 即為該 supply 的型別。

```move
module sui::balance;

const EOverflow: u64 = 1;

/// 可儲存的 balance——Coin 型別的內部結構。
/// 可用於儲存不需要 key ability 的 coin。
public struct Balance<phantom T> has store {
    value: u64,
}

/// 將 supply 增加 `value`，並以此值建立一個新的 `Balance<T>`。
public fun increase_supply<T>(self: &mut Supply<T>, value: u64): Balance<T> {
    assert!(value <= (std::u64::max_value!() - self.value), EOverflow);
    self.value = self.value + value;
    Balance { value }
}
```

這就是 Sui 上通常建立新貨幣的方式：本章前面介紹過的 `TreasuryCap`——一種 [capability](./capability)——是 `Supply<T>` 的包裝器，以見證實例化而成。

## 使用見證進行授權 (Authorization with Witness) {#authorization-with-witness}

實例化型別並非見證的唯一用途：任何函式都可以要求見證，使得該呼叫只對定義 `T` 的模組可用。下面的模組實作了一個泛型 `RegulatedCoin`，其中特權操作——`mint`、`burn` 與 `transfer`——需要見證，而共用功能——`join`——則對所有人開放：

```move file=packages/samples/sources/programmability/witness-pattern.move anchor=regulated_coin

```

定義見證型別並呼叫 `mint` 的模組會取得屬於自己的受規範貨幣：它可以獨自決定如何——以及是否——公開其代幣的鑄造、銷毀與轉帳功能，而基礎模組則實作所有此類貨幣共用的邏輯。

見證的這種用法與 [Capability](./capability) 樣式相近，但有一個重要差異：capability 是一個物件，因此它授權給擁有它的人——也就是帳戶；而見證只能由定義它的模組建構，因此它授權的是程式碼。使用見證進行授權是在程式碼撰寫時就決定的，不需要儲存空間，也無法被轉移。

## 一次性見證 (One Time Witness) {#one-time-witness}

雖然一個 struct 可以被建立任意次數，但在某些情況下，struct 應該被保證只能建立一次。為此，Sui 提供了「一次性見證（One-Time Witness）」——一種只能使用一次的特殊見證。我們會在[下一節](./one-time-witness)中更詳細地說明。

> 標準函式庫也提供了一種現成的證明形式：[Internal Permit](./../move-basics/internal-permit)。`internal::Permit<T>` 證明該呼叫已由定義 `T` 的模組授權——而不需要函式庫設計自訂的見證型別，或要求 `T` 本身具備 `drop`。

## 總結 (Summary) {#summary}

- 見證是一種透過建構證明來證明某項屬性的樣式。
- 在 Move 中，模組透過建構型別來證明對該型別的擁有權。
- 見證通常用於泛型型別實例化與授權。

## 下一步 (Next Steps) {#next-steps}

在下一節中，我們將學習[一次性見證](./one-time-witness)樣式。
