---
title: 列舉 (Enumerations) | 參考手冊
description: Move 列舉 (enumerations) 參考：定義變體型別 (variant types)、使用 match 進行模式比對 (pattern matching)、能力 (abilities) 與列舉專用操作 (enum-specific operations)。
keywords:
  - Move
  - Sui
  - Move reference
  - enumerations
  - reference
questions:
  - How does Enumerations work in Move?
  - What is the syntax for Enumerations in Move?
  - What is Defining Enums in Move?
  - What is Visibility in Move?
answer: 'Move enumerations reference: define variant types, pattern matching with match, abilities, and enum-specific operations.'
goal:
  description: 'Reader understands move enumerations reference: define variant types, pattern matching with match, abilities, and enum-specific operations'
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

# 列舉 (Enumerations) {#enumerations}

_enum_ 是一種由使用者定義的資料結構，包含一個或多個 _變體_。每個變體可選擇性地包含具型別的欄位。列舉中每個變體的欄位數量與型別都可以不同。列舉中的欄位可儲存任何非參考、非元組型別，包括其他結構或列舉。

作為簡單範例，請考慮下列 Move 中的列舉定義：

```move
public enum Action {
    Stop,
    Pause { duration: u32 },
    MoveTo { x: u64, y: u64 },
    Jump(u64),
}
```

這會宣告一個列舉 `Action`，代表遊戲可採取的不同動作——你可以 `Stop`、在指定時間內 `Pause`、`MoveTo` 特定位置，或 `Jump` 至特定高度。

與結構類似，列舉可以具有控制可對其執行哪些操作的[能力](./abilities)。但請注意，列舉無法具有 `key` 能力，因為它們不能是頂層物件。

## 定義列舉 (Defining Enums) {#defining-enums}

列舉必須定義在模組中，列舉至少必須包含一個變體，而且列舉的每個變體可以沒有欄位、具有位置欄位，或具有具名欄位。以下是各類型的範例：

```move
module a::m;

public enum Foo has drop {
    VariantWithNoFields,
    //                 ^ 註：變體宣告後面可以有結尾逗號
}
public enum Bar has copy, drop {
    VariantWithPositionalFields(u64, bool),
}
public enum Baz has drop {
    VariantWithNamedFields { x: u64, y: bool, z: Bar },
}
```

列舉不能在其任何變體中遞迴，因此不允許下列列舉定義，因為它們至少會在一個變體中遞迴。

錯誤：

```move
module a::m;

public enum Foo {
    Recursive(Foo),
    //        ^ 錯誤：遞迴列舉變體
}
public enum List {
    Nil,
    Cons { head: u64, tail: List },
    //                      ^ 錯誤：遞迴列舉變體
}
public enum BTree<T> {
    Leaf(T),
    Node { left: BTree<T>, right: BTree<T> },
    //           ^ 錯誤：遞迴列舉變體
}

// 也不允許相互遞迴的列舉
public enum MutuallyRecursiveA {
    Base,
    Other(MutuallyRecursiveB),
    //    ^^^^^^^^^^^^^^^^^^ 錯誤：遞迴列舉變體
}

public enum MutuallyRecursiveB {
    Base,
    Other(MutuallyRecursiveA),
    //    ^^^^^^^^^^^^^^^^^^ 錯誤：遞迴列舉變體
}
```

## 可見性 (Visibility) {#visibility}

所有 enum 都宣告為 `public`。這表示 enum 的型別可從任何其他模組參考。然而，enum 的變體、每個變體中的欄位，以及建立或銷毀 enum 變體的能力，都僅限於定義該 enum 的模組內部。

### 能力 (Abilities) {#abilities}

與 struct 相同，enum 宣告在預設情況下是線性且暫時性的。若要以非線性或非暫時性的方式使用 enum 值——也就是複製、丟棄或儲存在 [物件](./abilities/object) 中——你需要透過 `has <ability>` 註記來授予它額外的[能力](./abilities)：

```move
module a::m;

public enum Foo has copy, drop {
    VariantWithNoFields,
}
```

能力宣告可以出現在 enum 變體之前或之後，但只能擇一使用，不能同時使用兩者。若在變體之後宣告，能力宣告必須以分號結尾：

```move
module a::m;

public enum PreNamedAbilities has copy, drop { Variant }
public enum PostNamedAbilities { Variant } has copy, drop;
public enum PostNamedAbilitiesInvalid { Variant } has copy, drop
//                                                              ^ 錯誤！缺少分號

public enum NamedInvalidAbilities has copy { Variant } has drop;
//                                                     ^ 錯誤！重複的能力宣告
```

如需更多詳細資訊，請參閱[註記能力](./abilities#annotating-structs-and-enums)章節。

## 命名 (Naming) {#naming}

列舉及列舉中的變體必須以大寫字母 `A` 至 `Z` 開頭。第一個字母之後，
列舉名稱可包含底線 `_`、小寫字母 `a` 至 `z`、大寫字母 `A` 至 `Z`，
或數字 `0` 至 `9`。

```move
public enum Foo { Variant }
public enum BAR { Variant }
public enum B_a_z_4_2 { V_a_riant_0 }
```

採用以 `A` 至 `Z` 開頭的命名限制，是為了保留未來語言功能的擴充空間。

## 使用列舉 (Using Enums) {#using-enums}

### 建立列舉變體 (Creating Enum Variants) {#creating-enum-variants}

列舉型別的值可透過指定列舉的某個變體，接著為該變體中的每個欄位提供一個值來建立（或「封裝」）。變體名稱一律必須以列舉名稱限定。

與結構類似，對於具有具名欄位的變體，欄位順序無關緊要，但必須提供欄位名稱。對於具有位置欄位的變體，欄位順序很重要，而且欄位順序必須與變體宣告中的順序相符。也必須使用 `()` 而非 `{}` 來建立。若變體沒有欄位，變體名稱本身即已足夠，無須使用 `()` 或 `{}`。

```move
module a::m;

public enum Action has drop {
    Stop,
    Pause { duration: u32 },
    MoveTo { x: u64, y: u64 },
    Jump(u64),
}
public enum Other has drop {
    Stop(u64),
}

fun example() {
    // 注意：`Action` 的 `Stop` 變體沒有欄位，因此不需要括號或大括號。
    let stop = Action::Stop;
    let pause = Action::Pause { duration: 10 };
    let move_to = Action::MoveTo { x: 10, y: 20 };
    let jump = Action::Jump(10);
    // 注意：`Other` 的 `Stop` 變體確實具有位置欄位，因此我們需要提供它們。
    let other_stop = Other::Stop(10);
}
```

對於具有具名欄位的變體，你也可以使用你可能已從結構中熟悉的簡寫語法來建立變體：

```move
let duration = 10;

let pause = Action::Pause { duration: duration };
// 等同於
let pause = Action::Pause { duration };
```

### 對列舉變體進行模式比對與解構 (Pattern Matching Enum Variants and Destructuring) {#pattern-matching-enum-variants-and-destructuring}

由於列舉值可以具有不同形狀，因此不允許像存取結構欄位那樣使用點記法存取變體欄位。相反地，若要存取變體中的欄位——無論是依值、不可變參考或可變參考——你必須使用模式比對。

你可以依值、不可變參考及可變參考對 Move 值進行模式比對。依值進行模式比對時，該值會被移動至比對分支中。依參考進行模式比對時，該值會被借用至比對分支中（不可變或可變）。此處我們會簡要說明如何使用 `match` 進行模式比對；如需更多關於在 Move 中使用 `match` 進行模式比對的資訊，請參閱 [模式比對](./control-flow/pattern-matching)章節。

`match` 陳述式用於對 Move 值進行模式比對，並由多個 _比對分支_ 組成。每個比對分支由一個模式、箭頭 `=>`、一個運算式，以及後方的逗號 `,` 組成。模式可以是結構、列舉變體、繫結（`x`、`y`）、萬用字元（`_` 或 `..`）、常數（`ConstValue`）或常值（`true`、`42` 等）。該值會由上而下與每個模式進行比對，並會符合第一個在結構上與該值相符的模式。值符合後，會執行 `=>` 右側的運算式。

此外，比對分支可以具有選用的 _防護條件_，會在模式符合後、運算式執行*之前*檢查。防護條件以 `if` 關鍵字指定，後接一個必須在 `=>` 前評估為布林值的運算式。

```move
module a::m;

public enum Action has drop {
    Stop,
    Pause { duration: u32 },
    MoveTo { x: u64, y: u64 },
    Jump(u64),
}

public struct GameState {
    // 包含遊戲狀態的欄位
    character_x: u64,
    character_y: u64,
    character_height: u64,
    // ...
}

fun perform_action(stat: &mut GameState, action: Action) {
    match (action) {
        // 處理 `Stop` 變體
        Action::Stop => state.stop(),
        // 處理 `Pause` 變體
        // 如果持續時間為 0，則不執行任何動作
        Action::Pause { duration: 0 } => (),
        Action::Pause { duration } => state.pause(duration),
        // 處理 `MoveTo` 變體
        Action::MoveTo { x, y } => state.move_to(x, y),
        // 處理 `Jump` 變體
        // 如果遊戲不允許跳躍，則不執行任何動作
        Action::Jump(_) if (state.jumps_not_allowed()) => (),
        // 否則，跳至指定高度
        Action::Jump(height) => state.jump(height),
    }
}
```

若要了解如何對列舉進行模式比對，以可變方式更新其中的值，請考慮以下簡單列舉範例；它有兩個變體，每個變體各有一個欄位。接著我們可以撰寫兩個函式：一個只遞增第一個變體的值，另一個只遞增第二個變體的值：

```move
module a::m;

public enum SimpleEnum {
    Variant1(u64),
    Variant2(u64),
}

public fun incr_enum_variant1(simple_enum: &mut SimpleEnum) {
    match (simple_enum) {
        SimpleEnum::Variant1(mut value) => *value += 1,
        _ => (),
    }
}

public fun incr_enum_variant2(simple_enum: &mut SimpleEnum) {
    match (simple_enum) {
        SimpleEnum::Variant2(mut value) => *value += 1,
        _ => (),
    }
}
```

現在，如果我們有一個 `SimpleEnum` 值，便可以使用這些函式遞增此變體的值：

```move
let mut x = SimpleEnum::Variant1(10);
incr_enum_variant1(&mut x);
assert!(x == SimpleEnum::Variant1(11));
// 不會遞增，因為它遞增的是不同的變體
incr_enum_variant2(&mut x);
assert!(x == SimpleEnum::Variant1(11));
```

對不具有 `drop` 能力的 Move 值進行模式比對時，該值必須在每個比對分支中被消耗或解構。若該值未在比對分支中被消耗或解構，編譯器將引發錯誤。這是為了確保所有可能的值都會在 `match` 陳述式中得到處理。

例如，請考慮下列程式碼：

```move
module a::m;

public enum X { Variant { x: u64 } }

public fun bad(x: X) {
    match (x) {
        _ => (),
    // ^ 錯誤！型別為 `X` 的值未在此比對分支中被消耗或解構
    }
}
```

若要正確處理此情況，你需要在 `match` 的分支中解構 `X` 及其所有變體：

```move
module a::m;

public enum X { Variant { x: u64 } }

public fun good(x: X) {
    match (x) {
        // 正常！由於該值已被解構，因此可編譯
        X::Variant { x: _ } => (),
    }
}
```

### 覆寫為列舉值 (Overwriting to Enum Values) {#overwriting-to-enum-values}

只要列舉具有 `drop` 能力，你就可以如同處理 Move 中的其他值一般，以相同型別的新值覆寫列舉值。

```move
module a::m;

public enum X has drop {
    A(u64),
    B(u64),
}

public fun overwrite_enum(x: &mut X) {
    *x = X::A(10);
}
```

```move
let mut x = X::B(20);
overwrite_enum(&mut x);
assert!(x == X::A(10));
```
