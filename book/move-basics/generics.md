---
description: 'Generics in Move: write reusable functions and types that work with any type parameter, with phantom types and constraints.'
---

# 泛型 (Generics)

泛型是一種定義可以與任何類型協同工作的類型或函式的方式。當您想編寫一個可以與不同類型一起使用的函式，或者想定義一個可以容納任何其他類型的類型時，這非常有用。泛型是 Move 中許多進階功能的基礎，包括集合、抽象實作等。

## 在標準庫中

在本章中我們已經提到了 [向量 (vector)](./vector) 類型，它是一種可以容納任何其他類型的泛型。標準庫中另一個泛型類型的例子是 [選項 (Option)](./option) 類型，它用於表示一個可能存在也可能不存在的值。

## 泛型語法 (Generic Syntax)

要定義泛型類型或函式，類型特徵需要具有包含在角括號 (`<` 和 `>`) 中的泛型參數清單。泛型參數之間以逗號分隔。

```move file=packages/samples/sources/move-basics/generics.move anchor=container

```

在上面的範例中，`Container` 是一個具有單一類型參數 `T` 的泛型類型，該容器的 `value` 欄位儲存 `T`。`new` 函式是一個具有單一類型參數 `T` 的泛型函式，它傳回一個包含給定值的 `Container`。泛型類型必須使用具體類型進行初始化，且泛型函式必須使用具體類型進行呼叫，儘管在某些情況下 Move 編譯器可以推斷出正確的類型。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_container

```

在測試函式 `test_container` 中，我們演示了三種建立具有 `u8` 值的新 `Container` 的等效方法。因為數值常值具有歧義類型，我們必須在某處指定數字常值的類型（在容器的類型、`new` 的參數或數字常值本身之中）；一旦我們指定了其中之一，編譯器就可以推斷出其他部分。

## 多個類型參數

您可以定義具有多個類型參數的類型或函式。類型參數之間以逗號分隔。

```move file=packages/samples/sources/move-basics/generics.move anchor=pair

```

在上面的範例中，`Pair` 是一個具有兩個類型參數 `T` 和 `U` 的泛型類型，而 `new_pair` 函式是一個具有兩個類型參數 `T` 和 `U` 的泛型函式。該函式傳回一個具有給定值的 `Pair`。類型參數的順序很重要，應與類型特徵中類型參數的順序相匹配。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair

```

如果我們添加另一個在 `new_pair` 函式中交換類型參數的實例，並嘗試比較這兩個類型，我們會發現類型特徵是不同的，且無法進行比較。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_pair_swap

```

由於 `pair1` 和 `pair2` 的類型不同，比較 `pair1 == pair2` 將無法編譯。

## 為什麼需要泛型？

在上面的範例中，我們重點介紹了實體化泛型類型和呼叫泛型函式以建立這些類型的實例。然而，泛型真正的實力在於它們定義基礎泛型類型的共享行為，然後獨立於具體類型來使用它的能力。這在處理集合、抽象實作和 Move 中的其他進階功能時特別有用。

```move file=packages/samples/sources/move-basics/generics.move anchor=user

```

在上面的範例中，`User` 是一個具有單一類型參數 `T` 的泛型類型，具有共享欄位 `name`、`age` 以及泛型的 `metadata` 欄位（可以儲存任何類型）。無論 `metadata` 是什麼，`User` 的所有實例都將包含相同的欄位和方法。

```move file=packages/samples/sources/move-basics/generics.move anchor=update_user

```

## 幽靈類型參數 (Phantom Type Parameters)

在某些情況下，您可能希望定義一個具有在該類型的欄位或方法中未使用的類型參數的泛型類型。這被稱為 **幽靈類型參數 (phantom type parameter)**。當您想要定義一個可以容納任何其他類型的類型，但又想對類型參數強制執行某些約束時，幽靈類型參數非常有用。

```move file=packages/samples/sources/move-basics/generics.move anchor=phantom

```

這裡的 `Coin` 類型不包含任何使用類型參數 `T` 的欄位或方法。它被用來區分不同類型的代幣，並對類型參數 `T` 強制執行某些約束。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_phantom

```

在上面的範例中，我們演示了如何建立兩個具有不同幽靈類型參數 `USD` 和 `EUR` 的不同 `Coin` 實例。類型參數 `T` 未用於 `Coin` 類型的欄位或方法中，但它用於區分不同類型的代幣。這有助於確保 `USD` 和 `EUR` 代幣不會被錯誤地混淆。

## 類型參數的約束 (Constraints on Type Parameters) {#constraints-on-type-parameters}

可以約束類型參數以使其具備某些能力。這在您需要內部類型允許某些行為（如 _copy_ 或 _drop_）時非常有用。約束類型參數的語法為 `T: <能力> + <能力>`。

```move file=packages/samples/sources/move-basics/generics.move anchor=constraints

```

Move 編譯器將強制執行類型參數 `T` 具有指定的能力。如果類型參數不具備指定的能力，則程式碼將無法編譯。

```move file=packages/samples/sources/move-basics/generics.move anchor=test_constraints

```

## 延伸閱讀

- Move 參考手冊中的 [泛型](./../../reference/generics)。
