---
description: Move 中的複製能力 (copy ability) 可啟用值複製 (value duplication)。了解如何將 copy 新增至自訂型別 (custom types)，並理解它在資源安全性 (resource safety) 中的角色。
title: 能力 (Abilities)：複製
keywords:
  - Move
  - Sui
  - Move tutorial
  - abilities
  - copy
questions:
  - 'What is Abilities: Copy in Move?'
  - 'How do I use Abilities: Copy in Move?'
  - What is Copying and Drop in Move?
  - What is Types with the copy Ability in Move?
answer: The copy ability in Move enables value duplication. Learn how to add copy to custom types and understand its role in resource safety.
goal:
  description: Reader understands the copy ability in Move enables value duplication. Learn how to add copy to custom types and understand its role in resource safety
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

# 複製能力 (Abilities: Copy) {#abilities-copy}

在 [所有權與作用域](./ownership-and-scope)章節中，我們看到基本值會被*複製*而非移動：將數字指定給新的變數後，兩個變數仍可使用。`copy` 能力正是啟用此行為的機制——雖然它內建於基本型別，但對自訂型別而言，這*不是*預設行為。Move 的設計目的是表達數位資產與資源，而可以自由複製的資源就不太像資源。因此，型別必須明確選擇允許複製：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable

```

一旦型別具有 `copy` 能力，在原本會發生移動且仍需要原始值的位置，其值便會被複製——隱含地進行，不需要任何特殊語法。你可以使用 `copy` 關鍵字明確寫出複製操作：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable_test

```

在上述範例中，`a` 會隱含地複製到 `b`——編譯器發現之後還會使用 `a`，因此複製該值而非移動它。接著，使用 `copy` 關鍵字將 `a` 明確複製到 `c`。完成三次指定後，會有三個彼此獨立的 `Copyable` 執行個體——每一個都必須分別處理。

> 請注意範例結尾的解構：`Copyable` 具有 `copy`，但沒有 `drop`，因此每個執行個體——包括每一份複製——都必須被使用，測試會解構這三個執行個體。複製值絕不會略過使用規則；它只會建立更多適用這些規則的值。

## 複製與丟棄 (Copying and Drop) {#copying-and-drop}

如範例所示，只有 `copy` 而沒有 `drop` 是相當不方便的組合：允許複製，但每個複本仍需要明確處理。這就是兩種能力幾乎總是一起出現的原因——實務上，可以輕易複製的值通常也可以安全丟棄。承載一般資料而非資產的型別，通常會同時宣告這兩種能力：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copy_drop

```

所有基本型別的行為都如同具有 `copy` 和 `drop`：它們在指定時會被複製，也能直接丟棄——所有這些處理都由編譯器管理。

複製並不是讓程式多個部分讀取同一個值的唯一方法。在 [參考](./references)章節中，我們說明如何改為*借用*值，完全避免複製；以及[解除參考運算子](./references#dereferencing) `*` 如何將參考轉回複本，而這只允許用於具有 `copy` 能力的型別。

## 具有 `copy` 能力的型別 (Types with the `copy` Ability) {#types-with-the-copy-ability}

Move 中所有原生型別都具有 `copy` 能力，包括：

- [`bool`](./../move-basics/primitive-types#booleans)
- [無號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 具有 `copy` 時的 [`vector<T>`](./../move-basics/vector)
- [`address`](./../move-basics/address)

標準函式庫中定義的所有型別也都具有 `copy` 能力，包括：

- 當 `T` 具有 `copy` 時的 [`Option<T>`](./../move-basics/option)
- [`String`](./../move-basics/string)
- [`TypeName`](./../move-basics/type-reflection)

如同 [`drop`](./drop-ability#types-with-the-drop-ability)，容器型別只有在其內容可複製時才能複製：只有在原本允許複製 `T` 的情況下，`vector<T>` 才能被複製。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力](./../../reference/abilities)。
