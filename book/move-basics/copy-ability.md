---
description: 複製能力 (copy ability) 使值可以被複製。學習如何為自訂型別新增 copy，並了解它在資源安全 (resource safety) 中扮演的角色。
---

# Abilities: 複製能力 (Abilities: Copy) {#abilities-copy}

在[所有權與作用域](./ownership-and-scope)一節中，我們看到基本型別的值是**複製**而非移動的：把一個數字賦值給新變數，兩個變數都還能用。`copy` 能力正是實現這個行為的關鍵——雖然它內建於基本型別中，但對自訂型別而言**並非**預設行為。Move 的設計目的是表達數位資產與資源，而一個可以被任意複製的資源就稱不上是資源了。因此，複製是型別必須明確選擇加入的能力：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable

```

一旦型別擁有 `copy` 能力，只要原本會發生移動、且原始值之後仍被需要的地方，它的值就會被複製——這是隱含發生的，不需要任何特殊語法。`copy` 關鍵字可以用來明確表示這個複製動作：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copyable_test

```

在上面的範例中，`a` 被隱含地複製到 `b`——編譯器發現 `a` 之後還會被使用，因此複製了這個值而不是移動它。接著 `a` 又用 `copy` 關鍵字明確地複製到 `c`。經過這三次賦值後，會有三個獨立的 `Copyable` 實例——而每一個都必須被個別處理。

> 請注意範例最後的拆解：`Copyable` 擁有 `copy`，但沒有 `drop`，所以每個實例——包括每一份複製——都必須被使用，測試中拆解了全部三個實例。複製一個值並不會繞過使用規則；它只是產生了更多需要遵守這些規則的值。

## 複製與丟棄能力 (Copying and Drop) {#copying-and-drop}

如範例所示，只有 `copy` 而沒有 `drop` 是相當不方便的組合：允許複製，但每一份複製仍然需要明確處理。這正是為什麼這兩種能力幾乎總是成對出現——一個複製成本低廉的值，實務上通常也適合被捨棄。攜帶純粹資料（而非資產）的型別，通常會同時宣告這兩種能力：

```move file=packages/samples/sources/move-basics/copy-ability.move anchor=copy_drop

```

所有基本型別的行為都彷彿擁有 `copy` 和 `drop`：它們在賦值時被複製，並且可以毫不猶豫地被捨棄——這一切都由編譯器負責管理。

複製並不是讓程式的多個部分讀取同一個值的唯一方式。在[參考](./references)一節中，我們會說明如何**借用**一個值來完全避免複製；以及[解參考運算子](./references#dereferencing) `*` 如何將一個參考轉回一份複製，而這只允許用於擁有 `copy` 能力的型別。

## 擁有 `copy` 能力的型別 (Types with the `copy` Ability) {#types-with-the-copy-ability}

Move 中所有原生型別都擁有 `copy` 能力，這包括：

- [`bool`](./../move-basics/primitive-types#booleans)
- [無號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 擁有 `copy` 時的 [`vector<T>`](./../move-basics/vector)
- [`address`](./../move-basics/address)

標準函式庫中定義的所有型別也都擁有 `copy` 能力，這包括：

- 當 `T` 擁有 `copy` 時的 [`Option<T>`](./../move-basics/option)
- [`String`](./../move-basics/string)
- [`TypeName`](./../move-basics/type-reflection)

正如[`drop`](./drop-ability#types-with-the-drop-ability)一節所述，容器型別只有在其內容物本身可複製時才是可複製的：`vector<T>` 只有在 `T` 本身允許複製的前提下才能被複製。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力 (Type Abilities)](./../../reference/abilities)。
