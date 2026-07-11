---
title: 列舉 (Enumerations) | 參考
description: Move 列舉型別參考手冊：定義變體型別、使用 match 進行模式比對、能力，以及列舉特有的操作。
---

# 列舉 (Enumerations)

_列舉_ 是一個使用者定義的資料結構，包含一個或多個 _變體_。每個變體可以選擇性地包含型別化欄位。這些欄位的數量和型別可以在列舉中的每個變體之間不同。列舉中的欄位可以存儲任何非參考、非元組型別，包括其他結構體或列舉。

作為簡單示例，考慮以下 Move 中的列舉定義：

```move
public enum Action {
    Stop,
    Pause { duration: u32 },
    MoveTo { x: u64, y: u64 },
    Jump(u64),
}
```

這聲明了一個列舉 `Action`，代表遊戲中可以採取的不同動作 -- 你可以 `Stop`（停止）、`Pause`（暫停）一段時間、`MoveTo`（移動到）特定位置，或 `Jump`（跳躍）到特定高度。

類似於結構體，列舉可以有 [能力](./abilities)，控制可以對其執行什麼操作。但重要的是要注意，列舉不能具有 `key` 能力，因為它們不能是頂級物件。

## 定義列舉 (Defining Enums)

列舉必須在模組中定義，列舉必須至少包含一個變體，列舉的每個變體可以沒有欄位、位置欄位或命名欄位。以下是每種情況的示例：

```move
module a::m;

public enum Foo has drop {
    VariantWithNoFields,
    //                 ^ 注：在變體聲明後面有尾隨逗號是可以的
}
public enum Bar has copy, drop {
    VariantWithPositionalFields(u64, bool),
}
public enum Baz has drop {
    VariantWithNamedFields { x: u64, y: bool, z: Bar },
}
```

列舉不能在任何變體中遞迴，所以以下列舉定義是不允許的，因為它們在至少一個變體中是遞迴的。

不正確的：

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

// 相互遞迴的列舉也不允許
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

## 可見性 (Visibility)

所有列舉都聲明為 `public`。這意味著列舉的型別可以從任何其他模組參考。但是，列舉的變體、每個變體內的欄位以及建立或銷毀列舉變體的能力在定義列舉的模組內部。

### 能力 (Abilities)

就像結構體一樣，預設情況下列舉聲明是線性和短暫的。要以非線性或非短暫的方式使用列舉值 -- 即複製、丟棄或存儲在 [物件](./abilities/object) -- 你需要通過使用 `has <ability>` 註釋來賦予它額外的 [能力](./abilities)：

```move
module a::m;

public enum Foo has copy, drop {
    VariantWithNoFields,
}
```

能力聲明可以在列舉變體之前或之後出現，但只能使用其中一個，不能同時使用兩個。如果在變體後聲明，能力聲明必須以分號終止：

```move
module a::m;

public enum PreNamedAbilities has copy, drop { Variant }
public enum PostNamedAbilities { Variant } has copy, drop;
public enum PostNamedAbilitiesInvalid { Variant } has copy, drop
//                                                              ^ 錯誤！缺少分號

public enum NamedInvalidAbilities has copy { Variant } has drop;
//                                                     ^ 錯誤！重複的能力聲明
```

有關更多詳細資訊，請參閱[註釋能力](./abilities#annotating-structs-and-enums)部分。

## 命名 (Naming)

列舉和列舉中的變體必須以大寫字母 `A` 到 `Z` 開頭。在第一個字母後，列舉名稱可以包含底線 `_`、小寫字母 `a` 到 `z`、大寫字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
public enum Foo { Variant }
public enum BAR { Variant }
public enum B_a_z_4_2 { V_a_riant_0 }
```

這種以 `A` 到 `Z` 開頭的命名限制是為了為未來的語言功能留出空間。

## 使用列舉 (Using Enums)

### 建立列舉變體 (Creating Enum Variants)

列舉型別的值可以通過指示列舉的變體來建立（或"打包"），然後是變體中每個欄位的值。變體名稱必須始終由列舉名稱限定。

類似於結構體，對於具有命名欄位的變體，欄位的順序無關，但需要提供欄位名稱。對於具有位置欄位的變體，欄位的順序很重要，欄位的順序必須與變體聲明中的順序匹配。它也必須使用 `()` 而不是 `{}` 來建立。如果變體沒有欄位，變體名稱就足夠了，不需要使用 `()` 或 `{}`。

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
    // 注：`Action` 的 `Stop` 變體沒有欄位，所以不需要括號或花括號。
    let stop = Action::Stop;
    let pause = Action::Pause { duration: 10 };
    let move_to = Action::MoveTo { x: 10, y: 20 };
    let jump = Action::Jump(10);
    // 注：`Other` 的 `Stop` 變體有位置欄位，所以我們需要提供它們。
    let other_stop = Other::Stop(10);
}
```

對於具有命名欄位的變體，你也可以使用可能從結構體中熟悉的簡寫語法來建立變體：

```move
let duration = 10;

let pause = Action::Pause { duration: duration };
// 等同於
let pause = Action::Pause { duration };
```

### 模式匹配列舉變體和解構 (Pattern Matching Enum Variants and Destructuring)

由於列舉值可以採用不同的形狀，不允許像結構體欄位那樣對變體的欄位進行點訪問。相反，要訪問變體內的欄位 -- 無論是按值、還是不可變參考或可變參考 -- 你必須使用模式匹配。

你可以按值、不可變參考和可變參考對 Move 值進行模式匹配。按值進行模式匹配時，該值被移動到匹配臂中。按參考進行模式匹配時，該值被借用到匹配臂中（不可變或可變地）。我們將在這裡簡要介紹使用 `match` 的模式匹配，但有關在 Move 中使用 `match` 的模式匹配的更多資訊，請參閱 [模式匹配](./control-flow/pattern-matching) 部分。

`match` 陳述用於對 Move 值進行模式匹配，由許多 _匹配臂_ 組成。每個匹配臂由一個模式、一個箭頭 `=>`、一個表達式和一個逗號 `,` 組成。模式可以是結構體、列舉變體、綁定（`x`、`y`）、萬用字元（`_` 或 `..`）、常數（`ConstValue`）或字面值（`true`、`42` 等）。值從上到下與每個模式匹配，將匹配在結構上匹配該值的第一個模式。一旦值被匹配，`=>` 右邊的表達式就會被執行。

此外，匹配臂可以具有可選的 _守衛_，在模式匹配後但 _在_ 表達式執行之前檢查。守衛由 `if` 關鍵字後跟必須在 `=>` 前評估為布林值的表達式指定。

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
        // 如果持續時間為 0，不執行任何操作
        Action::Pause { duration: 0 } => (),
        Action::Pause { duration } => state.pause(duration),
        // 處理 `MoveTo` 變體
        Action::MoveTo { x, y } => state.move_to(x, y),
        // 處理 `Jump` 變體
        // 如果遊戲不允許跳躍，則不執行任何操作
        Action::Jump(_) if (state.jumps_not_allowed()) => (),
        // 否則，跳到指定的高度
        Action::Jump(height) => state.jump(height),
    }
}
```

要了解如何對列舉進行模式匹配以可變方式更新其中的值，請看以下簡單列舉的示例，它有兩個變體，每個變體都有一個欄位。然後我們可以編寫兩個函式，一個僅遞增第一個變體的值，另一個僅遞增第二個變體的值：

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

現在，如果我們有一個 `SimpleEnum` 的值，我們可以使用這些函式來遞增此變體的值：

```move
let mut x = SimpleEnum::Variant1(10);
incr_enum_variant1(&mut x);
assert!(x == SimpleEnum::Variant1(11));
// 不遞增，因為它遞增了不同的變體
incr_enum_variant2(&mut x);
assert!(x == SimpleEnum::Variant1(11));
```

當對沒有 `drop` 能力的 Move 值進行模式匹配時，該值必須在每個匹配臂中被消耗或解構。如果該值在匹配臂中未被消耗或解構，編譯器將引發錯誤。這是為了確保匹配陳述中的所有可能值都被處理。

例如，考慮以下程式碼：

```move
module a::m;

public enum X { Variant { x: u64 } }

public fun bad(x: X) {
    match (x) {
        _ => (),
    // ^ 錯誤！型別為 `X` 的值在此匹配臂中未被消耗或解構
    }
}
```

要正確處理此問題，你需要在匹配臂中解構 `X` 及其所有變體：

```move
module a::m;

public enum X { Variant { x: u64 } }

public fun good(x: X) {
    match (x) {
        // 確定！編譯成功，因為該值已被解構
        X::Variant { x: _ } => (),
    }
}
```

### 覆蓋列舉值 (Overwriting to Enum Values)

只要列舉具有 `drop` 能力，你可以用相同型別的新值覆蓋列舉的值，就像你對 Move 中的其他值可能做的那樣。

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
