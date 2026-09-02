---
description: 泛型 (Generics) in Move：撰寫可重複使用的函式與型別，適用於任何型別參數，並包含幻影型別 (Phantom Types) 與限制條件。
---

# 泛型 (Generics) {#generics}

Generics 是一種定義型別或函式的方式，讓它能與任何型別搭配運作，而不是綁定單一特定型別。你在本章中其實已經用過 generics，只是可能沒有注意到：[vector](./vector) 型別就是泛型的——單一定義即可容納任何型別的元素——[Option](./option) 也是，它能包裝任何值。Generics 是集合、抽象實作以及 Move 許多進階功能的基礎。

## Generics 解決的問題 (The Problem Generics Solve) {#the-problem-generics-solve}

假設我們需要一個能包裝單一 `u64` 值的型別。很簡單：

```move
public struct U64Container has drop {
    value: u64,
}
```

但如果我們也需要包裝一個 `bool` 呢？還有 `String`？還有我們自己的 struct？每個版本除了 `value` 欄位的型別之外都完全相同，而每個處理容器的函式也都需要為每個版本重複撰寫一次：

```move
public struct BoolContainer has drop { value: bool }
public struct StringContainer has drop { value: String }
// ...每個想儲存的型別都要一個新的 struct
```

Generics 正是為了解決這個問題：我們只定義容器**一次**，用一個佔位符取代具體型別，並在使用該型別時再填入實際型別。

## Generic 語法 (Generic Syntax) {#generic-syntax}

要定義泛型型別或函式，在名稱後面加上一組以角括號（`<` 和 `>`）括住的**型別參數**列表。多個型別參數以逗號分隔。

```move file=packages/samples/sources/move-basics/generics.move anchor=container

```

在上面的範例中，`Container` 是一個帶有單一型別參數 `T` 的泛型型別，容器的 `value` 欄位儲存型別為 `T` 的值。`T` 並不是真實的型別——它是一個佔位符，代表「某個型別，稍後再指定」。`new` 函式是帶有相同型別參數的泛型函式，它會回傳一個帶有給定值的 `Container<T>`。

> 依照慣例，型別參數以單一大寫字母命名——`T`、`U`、`K`、`V`。不過，也可以使用任何合法的名稱：例如標準函式庫就將 `vector` 的型別參數命名為 `Element`。

## 使用泛型型別 (Using Generic Types) {#using-generic-types}

當我們建立泛型型別的實例時，佔位符會被替換為具體型別。每次替換都會產生一個不同的型別：`Container<u8>`、`Container<bool>` 與 `Container<String>` 雖然來自同一個定義，卻是三種不同的型別。

具體型別可以明確寫出，或在大多數情況下由編譯器推斷：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_container

```

測試的前三行是等價的——每一行都建立了一個 `Container<u8>`。因為數字字面值的型別是模糊的，我們必須在某處指定該數字的型別：在變數的型別標註中、在 `new` 的明確型別引數中，或是在字面值本身。只要給定其中一項，編譯器就能推斷出其餘部分。對於型別不模糊的值，例如 `bool` 或 `String`，則完全不需要任何標註。

## 多個型別參數 (Multiple Type Parameters) {#multiple-type-parameters}

型別或函式可以有多個以逗號分隔的型別參數：

```move file=packages/samples/sources/move-basics/generics.move anchor=pair

```

在上面的範例中，`Pair` 是一個帶有兩個型別參數 `T` 和 `U` 的泛型型別，`new_pair` 函式會建立一個帶有給定值的 `Pair`。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair

```

型別參數的順序很重要。`Pair<u8, bool>` 與 `Pair<bool, u8>` 是兩個不同、互不相容的型別——即使它們是由相同的定義建構出來，並儲存相同的資料：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair_swap

```

由於 `pair1` 與 `pair2` 的型別不同，`pair1 == pair2` 這樣的比較將無法編譯。這些值只能在拆解之後逐欄位比較。

## 為何使用 Generics？ (Why Generics?) {#why-generics}

到目前為止，我們專注於機制層面：如何定義泛型型別並建立其實例。Generics 真正的威力在於能夠只定義一次共用的資料與行為，並讓型別的一部分保持可變。考慮一個 `User` 型別，其中 `name` 與 `age` 欄位始終相同，但不同的應用程式需要附加不同的額外資料：

```move file=packages/samples/sources/move-basics/generics.move anchor=user

```

為 `User<T>` 定義的函式無論 `metadata` 是什麼型別都能運作——它們操作共用欄位，並不需要知道 `T` 的具體型別：

```move file=packages/samples/sources/move-basics/generics.move anchor=update_user

```

```move file=packages/samples/sources/move-basics/generics.move anchor=test_user

```

在上面的測試中，一個 `User` 實例將 `u64` 儲存為其中繼資料，另一個則儲存 `bool`，但兩者都能透過同一個只定義一次的 `update_name` 函式來更新。

## 虛擬型別參數 (Phantom Type Parameters) {#phantom-type-parameters}

有時候，型別參數只需要作為一個**標籤**使用，而不需要儲存該型別的任何值。考慮一個 `Coin` 型別：實際資料只是一個數值 `value`，對每一種貨幣都相同。然而，一枚美元硬幣與一枚歐元硬幣絕不能混淆——在編譯器眼中它們應該是不同的型別。為了表達這一點，該型別參數會被宣告為 `phantom`——一個不出現在任何欄位中的參數：

```move file=packages/samples/sources/move-basics/generics.move anchor=phantom

```

> Move 要求每個一般型別參數都必須用於 struct 的欄位中。由於 `T` 並未儲存在 `Coin` 的任何地方，它必須以 `phantom` 關鍵字標記。

貨幣接著可以被定義為空的 struct——它們不攜帶任何資料，存在的目的僅僅是作為標籤使用：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_phantom

```

即使 `Coin<USD>` 與 `Coin<EUR>` 儲存的資料完全相同，它們仍是不同的型別，而預期其中一種型別的函式將不會接受另一種型別。這種模式在實際應用中被廣泛使用：舉例來說，[Sui Framework](./../programmability/sui-framework) 中的 `Coin` 型別正是以這種方式定義的。

## 型別參數的約束 (Constraints on Type Parameters) {#constraints-on-type-parameters}

預設情況下，型別參數接受**任何**型別。然而，有時內部型別必須允許特定行為，例如可被複製或捨棄，為此可以將型別參數約束為具有特定[能力 (abilities)](./abilities-introduction)。語法為 `T: <ability> + <ability>`：

```move file=packages/samples/sources/move-basics/generics.move anchor=constraints

```

約束是具體型別必須遵守的承諾：Move 編譯器只允許用具有 [drop](./drop-ability) 能力的型別來實例化 `Droppable<T>`，並且只允許用同時具有 [copy](./copy-ability) 與 `drop` 能力的型別來實例化 `CopyableDroppable<T>`。不具備這些能力的型別將無法通過編譯：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_constraints

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[Generics](./../../reference/generics)。
