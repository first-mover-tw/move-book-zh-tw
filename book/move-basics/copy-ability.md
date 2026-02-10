# 能力：複製 (Copy)

在 Move 中，類型上的 **copy** 能力表示該類型的實例或值可以被複製或複製。雖然在使用數字或其他原始類型時預設提供了此行為，但對於自定義類型，這並非預設行為。Move 旨在表達數位資產 and 資源，而控制複製資源的能力是資源模型的一個核心原則。然而，Move 類型系統允許您為自定義類型添加 **copy** 能力：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable

```

在上面的範例中，我們定義了一個具有 **copy** 能力的自定義類型 `Copyable`。這意味著 `Copyable` 的實例可以被隱式或顯式地複製。

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable_test

```

在上面的範例中，`a` 被隱式複製到 `b`，然後使用解參照 (dereference) 運算子顯式複製到 `c`。如果 `Copyable` 不具備 **copy** 能力，程式碼將無法編譯，且 Move 編譯器會發出錯誤。

> 注意：在 Move 中，使用空括號進行解構通常用於消耗未使用的變數，特別是對於不具備 drop 能力的類型。這可以防止由於值在沒有明確使用的情況下超出作用域而導致的編譯器錯誤。此外，Move 在解構時需要類型名稱（例如 `let Copyable {} = a;` 中的 `Copyable`），因為它強制執行嚴格的類型和所有權規則。

## 複製與捨棄 (Copying and Drop)

`copy` 能力與 [`drop` 能力](./drop-ability) 密切相關。如果一個類型具有 **copy** 能力，它很可能也應該具有 `drop` 能力。這是因為當實例不再需要時，需要具備 **drop** 能力來清理資源。如果一個類型僅具備 **copy**，管理其實例會變得更為複雜，因為實例必須被明確使用或消耗。

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copy_drop

```

Move 中的所有原始類型其行為就像它們同時具備 **copy** 和 **drop** 能力。這意味著它們可以被複製和捨棄，且 Move 編譯器會為它們處理記憶體管理。

## 具備 `copy` 能力的類型

Move 中的所有原生類型都具備 `copy` 能力。這包括：

- [布林值 (bool)](./../move-basics/primitive-types#booleans)
- [無號整數 (unsigned integers)](./../move-basics/primitive-types#integer-types)
- [向量 (vector)](./../move-basics/vector)
- [地址 (address)](./../move-basics/address)

標準庫中定義的所有類型同樣具備 `copy` 能力。這包括：

- [選項 (Option)](./../move-basics/option)
- [字串 (String)](./../move-basics/string)
- [類型名稱 (TypeName)](./../move-basics/type-reflection)

## 延伸閱讀

- Move 參考手冊中的 [類型能力 (Type Abilities)](./../../reference/abilities)。
