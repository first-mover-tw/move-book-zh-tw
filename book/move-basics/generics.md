---
description: Move (Move) 中的泛型 (Generics)：撰寫可搭配任何型別參數運作的可重複使用函式與型別，並使用虛擬型別與限制。
title: 泛型 (Generics)
keywords:
  - Move
  - Sui
  - Move tutorial
  - generics
questions:
  - What is Generics in Move?
  - How do I use Generics in Move?
  - What is The Problem Generics Solve in Move?
  - What is Generic Syntax in Move?
answer: 'Generics in Move: write reusable functions and types that work with any type parameter, with phantom types and constraints.'
goal:
  description: 'Reader understands generics in Move: write reusable functions and types that work with any type parameter, with phantom types and constraints'
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

# 泛型 (Generics) {#generics}

泛型是一種定義可處理任何型別（而非單一特定型別）的型別或函式的方法。你可能已在本章中使用過泛型而未察覺： [vector](./vector) 型別是泛型——單一的定義可保存任何型別的元素——[Option](./option) 也是如此，它可包裝任何值。泛型是集合、抽象實作，以及 Move 許多進階功能的基礎。

## 泛型解決的問題 (The Problem Generics Solve) {#the-problem-generics-solve}

假設我們需要一個包裝單一 `u64` 值的型別。這很簡單：

```move
public struct U64Container has drop {
    value: u64,
}
```

但如果我們還需要包裝 `bool` 呢？還有 `String` 呢？或是我們自行定義的結構呢？每個版本除了 `value` 欄位的型別外都完全相同，而每個處理容器的函式都必須為每個版本重複定義：

```move
public struct BoolContainer has drop { value: bool }
public struct StringContainer has drop { value: String }
// …為我們想儲存的每種型別建立新的 struct
```

泛型正好解決這個問題：我們只定義容器 _一次_，以預留位置取代具體型別，並在使用該型別時填入預留位置。

## 泛型語法 (Generic Syntax) {#generic-syntax}

若要定義泛型型別或函式，請在名稱後方加上以尖括號（`<` 與 `>`）包住的 _型別參數_ 清單。多個型別參數以逗號分隔。

```move file=packages/samples/sources/move-basics/generics.move anchor=container

```

在上述範例中，`Container` 是具有單一型別參數 `T` 的泛型型別，容器的 `value` 欄位會儲存型別為 `T` 的值。`T` 不是真正的型別——它是代表「某個待稍後指定的型別」的預留位置。`new` 函式是具有相同型別參數的泛型函式，並會回傳含有指定值的 `Container<T>`。

> 依慣例，型別參數會以單一大寫字母命名，例如 `T`、`U`、`K`、`V`。
> 不過，也可以使用任何有效名稱：例如，標準函式庫將 `vector` 的型別參數命名為 `Element`。

## 使用泛型型別 (Using Generic Types) {#using-generic-types}

建立泛型型別的執行個體時，預留位置會替換為具體型別。每次替換都會產生不同的型別：`Container<u8>`、`Container<bool>` 與 `Container<String>` 都源自相同定義，但它們是三種不同的型別。

具體型別可以明確寫出，或在大多數情況下由編譯器推斷：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_container

```

測試中的前三行是等效的——每一行都會建立 `Container<u8>`。由於數值字面值的型別具有歧義，我們必須在某處指定數字的型別：在變數的型別註記中、在 `new` 的明確型別引數中，或直接在字面值本身。一旦提供其中一種資訊，編譯器便會推斷其餘部分。對於型別明確的值，例如 `bool` 或 `String`，完全不需要註記。

## 多個型別參數 (Multiple Type Parameters) {#multiple-type-parameters}

型別或函式可具有多個型別參數，並以逗號分隔：

```move file=packages/samples/sources/move-basics/generics.move anchor=pair

```

在上述範例中，`Pair` 是具有兩個型別參數 `T` 與 `U` 的泛型型別，`new_pair` 函式會以指定的值建立 `Pair`。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair

```

型別參數的順序很重要。`Pair<u8, bool>` 與 `Pair<bool, u8>` 是兩種不同且不相容的型別——即使它們都是由相同定義建立，且儲存相同資料：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair_swap

```

由於 `pair1` 與 `pair2` 的型別不同，`pair1 == pair2` 比較無法通過編譯。只有在解構後，才能逐欄位比較這些值。

## 為何使用泛型？ (Why Generics?) {#why-generics}

到目前為止，我們著重於機制：如何定義泛型型別及建立其執行個體。泛型真正的力量在於一次定義共用資料與行為，並讓型別的一部分可以變動。考慮一個 `User` 型別，其中 `name` 與 `age` 欄位始終相同，但不同應用程式需要附加不同的額外資料：

```move file=packages/samples/sources/move-basics/generics.move anchor=user

```

為 `User<T>` 定義的函式不論 `metadata` 為何都能運作——它們處理共用欄位，且不需要知道 `T` 的具體型別：

```move file=packages/samples/sources/move-basics/generics.move anchor=update_user

```

```move file=packages/samples/sources/move-basics/generics.move anchor=test_user

```

在上述測試中，一個 `User` 執行個體將 `u64` 作為其中繼資料，另一個則儲存 `bool`；然而兩者都使用僅定義一次的相同 `update_name` 函式更新。

## 幽靈型別參數 (Phantom Type Parameters) {#phantom-type-parameters}

有時候，型別參數只需要作為 _標籤_，而無須儲存該型別的任何值。考慮 `Coin` 型別：實際資料只是數值 `value`，對所有貨幣皆相同。然而，美金與歐元的代幣絕不可混淆——在編譯器看來，它們應該是不同型別。為了表達這項需求，型別參數會宣告為 `phantom`——不會出現在任何欄位中的參數：

```move file=packages/samples/sources/move-basics/generics.move anchor=phantom

```

> Move 要求每個一般型別參數都必須用於結構的欄位中。由於 `T` 未儲存在 `Coin` 的任何位置，因此必須以 `phantom` 關鍵字標記。

接著可以將貨幣定義為空結構——它們不承載資料，只用作標籤：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_phantom

```

雖然 `Coin<USD>` 與 `Coin<EUR>` 儲存完全相同的資料，它們仍是不同型別；預期其中一種型別的函式不會接受另一種。此模式廣泛用於實際應用程式中：[Sui Framework](./../programmability/sui-framework) 的 `Coin` 型別正是以此方式定義。

## 型別參數的約束 (Constraints on Type Parameters) {#constraints-on-type-parameters}

預設情況下，型別參數可接受 _任何_ 型別。然而，有時內部型別必須允許某些行為，例如可被複製或捨棄；此時可約束型別參數必須具有特定的 [能力](./abilities-introduction)。語法為 `T: <ability> + <ability>`：

```move file=packages/samples/sources/move-basics/generics.move anchor=constraints

```

約束是具體型別必須遵守的承諾：Move 編譯器只允許以具有 [drop](./drop-ability) 能力的型別具現化 `Droppable<T>`，並以同時具有 [copy](./copy-ability) 與 `drop` 的型別具現化 `CopyableDroppable<T>`。不具備這些能力的型別無法通過編譯：

```move file=packages/samples/sources/move-basics/generics.move anchor=test_constraints

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Generics](./../../reference/generics)。
