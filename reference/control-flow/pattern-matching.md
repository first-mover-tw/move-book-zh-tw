---
title: 模式匹配 (Pattern Matching) | 參考手冊
description: Move 模式比對參考手冊 (Move pattern matching reference)：match 運算式、解構、守衛、萬用字元與窮盡比對規則。
---

# 模式匹配 (Pattern Matching)

`match` 運算式是一種強大的控制結構，它允許你將一個值與一系列模式進行比較，然後根據哪個模式首先匹配來執行程式碼。模式可以是從簡單的字面值到複雜的、巢狀的結構體 (struct) 和列舉 (enum) 定義。與根據 `bool` 型別的測試運算式改變控制流的 `if` 運算式不同，`match` 運算式對任何型別的值進行操作，並選擇多個分支 (arms) 之一。

`match` 運算式可以匹配 Move 數值以及可變或不可變參考，並據此綁定子模式。

例如：

```move
fun run(x: u64): u64 {
    match (x) {
        1 => 2,
        2 => 3,
        x => x,
    }
}

run(1); // 回傳 2
run(2); // 回傳 3
run(3); // 回傳 3
run(0); // 回傳 0
```

## `match` 語法

`match` 接受一個運算式和一系列以逗號分隔的非空「模式分支 (match arms)」。

每個模式分支由一個模式 (`p`)、一個可選的守衛 (guard) (`if (g)`，其中 `g` 是型別為 `bool` 的運算式)、一個箭頭 (`=>`) 和一個在模式匹配時執行的分支運算式 (`e`) 組成。例如：

```move
match (運算式) {
    模式1 if (守衛運算式) => 運算式1,
    模式2 => 運算式2,
    模式3 => { 運算式3, 運算式4, ... },
}
```

模式分支按從上到下的順序檢查，第一個匹配的模式（如果存在守衛運算式，則其求值結果必須為 `true`）將被執行。

請注意，`match` 內的一系列模式分支必須是 **窮舉的 (exhaustive)**，這意味著被匹配型別的每個可能值都必須由 `match` 中的其中一個模式覆蓋。如果模式分支系列不具備窮舉性，編譯器將報錯。

## 模式語法

如果數值等於模式，且變數和萬用字元（如 `x`、`y`、`_` 或 `..`）與任何事物都「相等」，則該模式與該數值匹配。

模式用於匹配數值。模式可以是：

| 模式                       | 描述                                                            |
| -------------------------- | --------------------------------------------------------------- |
| 字面值 (Literal)           | 字面數值，例如 `1`, `true`, `@0x1`                              |
| 常數 (Constant)            | 常數值，例如 `MyConstant`                                       |
| 變數 (Variable)            | 變數，例如 `x`, `y`, `z`                                        |
| 萬用字元 (Wildcard)        | 萬用字元，例如 `_`                                              |
| 建構子 (Constructor)       | 建構子模式，例如 `MyStruct { x, y }`, `MyEnum::Variant(x)`      |
| At 模式 (@-pattern)        | At 模式，例如 `x @ MyEnum::Variant(..)`                         |
| Or 模式 (Or-pattern)       | Or 模式，例如 `MyEnum::Variant(..) \| MyEnum::OtherVariant(..)` |
| 多數量萬用字元             | 多數量萬用字元，例如 `MyEnum::Variant(..)`                      |
| 可變綁定 (Mutable-binding) | 可變綁定模式，例如 `mut x`                                      |

Move 中的模式具有以下語法規律：

```bnf
pattern = <字面值>
        | <常數>
        | <變數>
        | _
        | C { <變數> : 內部模式 ["," <變數> : 內部模式]* } // 其中 C 是結構體或列舉變體
        | C ( 內部模式 ["," 內部模式]* ... )                       // 其中 C 是結構體或列舉變體
        | C                                                      // 其中 C 是列舉變體
        | <變數> @ 頂層模式
        | 模式 | 模式
        | mut <變數>
inner-pattern = 模式
              | ..     // 多數量萬用字元
```

一些模式範例如下：

```move
// 字面值模式
1

// 常數模式
MyConstant

// 變數模式
x

// 萬用字元模式
_

// 建構子模式，匹配具有欄位 `1` 和 `true` 的 `MyEnum::Variant`
MyEnum::Variant(1, true)

// 建構子模式，匹配具有欄位 `1` 的 `MyEnum::Variant` 並將第二個欄位的值綁定到 `x`
MyEnum::Variant(1, x)

// 多數量萬用字元模式，匹配 `MyEnum::Variant` 變體內的多個欄位
MyEnum::Variant(..)

// 建構子模式，匹配 `MyStruct` 的 `x` 欄位並將 `y` 欄位綁定到 `other_variable`
MyStruct { x, y: other_variable }

// at-模式，匹配 `MyEnum::Variant` 並將整個值綁定到 `x`
x @ MyEnum::Variant(..)

// or-模式，匹配 `MyEnum::Variant` 或 `MyEnum::OtherVariant`
MyEnum::Variant(..) | MyEnum::OtherVariant(..)

// 與上述 or-模式相同，但帶有顯式萬用字元
MyEnum::Variant(_, _) | MyEnum::OtherVariant(_, _)

// or-模式，匹配 `MyEnum::Variant` 或 `MyEnum::OtherVariant` 並將 u64 欄位綁定到 `x`
MyEnum::Variant(x, _) | MyEnum::OtherVariant(_, x)

// 建構子模式，匹配 `OtherEnum::V` 以及內部的 `MyEnum` 是否為 `MyEnum::Variant`
OtherEnum::V(MyEnum::Variant(..))
```

### 模式與變數

包含變數的模式會將它們綁定到正在匹配的 match 物件或其子組件。這些變數隨後可以用於任何模式守衛運算式中，或用於模式分支的右側。例如：

```move
public struct Wrapper(u64)

fun add_under_wrapper_unless_equal(wrapper: Wrapper, x: u64): Wrapper {
    match (wrapper) {
        Wrapper(y) if (y == x) => Wrapper(y),
        Wrapper(y) => Wrapper(y + x),
    }
}
add_under_wrapper_unless_equal(Wrapper(1), 2); // 回傳 Wrapper(3)
add_under_wrapper_unless_equal(Wrapper(2), 3); // 回傳 Wrapper(5)
add_under_wrapper_unless_equal(Wrapper(3), 3); // 回傳 Wrapper(3)
```

### 組合模式

模式可以巢狀，也可以使用 or 運算子 (`|`) 組合。例如，如果 `p1` 或 `p2` 其中之一與物件匹配，則 `p1 | p2` 成功。這種模式可以出現在任何地方 —— 無論是作為頂層模式還是作為另一個模式內的子模式。

```move
public enum MyEnum has drop {
    Variant(u64, bool),
    OtherVariant(bool, u64),
}

fun test_or_pattern(x: u64): u64 {
    match (x) {
        MyEnum::Variant(1 | 2 | 3, true) | MyEnum::OtherVariant(true, 1 | 2 | 3) => 1,
        MyEnum::Variant(8, true) | MyEnum::OtherVariant(_, 6 | 7) => 2,
        _ => 3,
    }
}

test_or_pattern(MyEnum::Variant(3, true)); // 回傳 1
test_or_pattern(MyEnum::OtherVariant(true, 2)); // 回傳 1
test_or_pattern(MyEnum::Variant(8, true)); // 回傳 2
test_or_pattern(MyEnum::OtherVariant(false, 7)); // 回傳 2
test_or_pattern(MyEnum::OtherVariant(false, 80)); // 回傳 3
```

### 特定模式的限制

`mut` 和 `..` 模式在使用時、位置和方式上也有特定的限制，詳見 [特定模式的限制](#特定模式的限制)。從高級別來看，`mut` 修飾符只能用於變數模式，而 `..` 模式在建構子模式中只能使用一次 —— 且不能作為頂層模式。

以下是對 `..` 模式的 **無效** 使用，因為它被用作頂層模式：

```move
match (x) {
    .. => 1,
    // 錯誤：`..` 模式只能在建構子模式內使用
}

match (x) {
    MyStruct(.., ..) => 1,
    // 錯誤：   ^^  `..` 模式在建構子模式中只能使用一次
}
```

### 模式型別 (Pattern Typing)

模式本身不是運算式，但它們仍然具備型別。這意味著模式的型別必須與它匹配的值的型別匹配。例如，模式 `1` 具有整數型別，模式 `MyEnum::Variant(1, true)` 具有型別 `MyEnum`，模式 `MyStruct { x, y }` 具有型別 `MyStruct`，而 `OtherStruct<bool> { x: true, y: 1}` 具有型別 `OtherStruct<bool>`。如果你嘗試匹配一個與模式型別不同的運算式，將導致型別錯誤。例如：

```move
match (1) {
    // `true` 字面值模式的型別是 `bool`，因此這是一個型別錯誤。
    true => 1,
    // 型別錯誤：預期型別為 u64，發現 bool
    _ => 2,
}
```

同樣地，以下情況也會導致型別錯誤，因為 `MyEnum` 和 `MyStruct` 是不同的型別：

```move
match (MyStruct { x: 0, y: 0 }) {
    MyEnum::Variant(..) => 1,
    // 型別錯誤：預期型別為 MyEnum，發現 MyStruct
}
```

## 匹配 (Matching)

在深入探討模式匹配的細節以及數值「匹配」模式的意義之前，讓我們檢視幾個範例，以提供對該概念的直觀理解。

```move
fun test_lit(x: u64): u8 {
    match (x) {
        1 => 2,
        2 => 3,
        _ => 4,
    }
}
test_lit(1); // 回傳 2
test_lit(2); // 回傳 3
test_lit(3); // 回傳 4
test_lit(10); // 回傳 4

fun test_var(x: u64): u64 {
    match (x) {
        y => y,
    }
}
test_var(1); // 回傳 1
test_var(2); // 回傳 2
test_var(3); // 回傳 3
...

const MyConstant: u64 = 10;
fun test_constant(x: u64): u64 {
    match (x) {
        MyConstant => 1,
        _ => 2,
    }
}
test_constant(MyConstant); // 回傳 1
test_constant(10); // 回傳 1
test_constant(20); // 回傳 2

fun test_or_pattern(x: u64): u64 {
    match (x) {
        1 | 2 | 3 => 1,
        4 | 5 | 6 => 2,
        _ => 3,
    }
}
test_or_pattern(3); // 回傳 1
test_or_pattern(5); // 回傳 2
test_or_pattern(70); // 回傳 3

fun test_or_at_pattern(x: u64): u64 {
    match (x) {
        x @ (1 | 2 | 3) => x + 1,
        y @ (4 | 5 | 6) => y + 2,
        z => z + 3,
    }
}
test_or_pattern(2); // 回傳 3
test_or_pattern(5); // 回傳 7
test_or_pattern(70); // 回傳 73
```

從這些範例中可以注意到最重要的一點是：如果數值等於模式，則模式匹配該數值，而萬用字元/變數模式可以匹配任何事物。這對於字面值、變數和常數都是正確的。例如，在 `test_lit` 函式中，數值 `1` 匹配模式 `1`，數值 `2` 匹配模式 `2`，而數值 `3` 匹配萬用字元 `_`。同樣地，在 `test_var` 函式中，數值 `1` 和數值 `2` 都匹配模式 `y`。

變數 `x` 匹配（或「等於」）任何數值，萬用字元 `_` 匹配任何數值（但僅匹配一個值）。Or 模式就像邏輯或 (OR)，如果數值匹配 or 模式中的任何模式，則該數值匹配該模式，因此 `p1 | p2 | p3` 應解讀為「匹配 p1，或 p2，或 p3」。

### 匹配建構子 (Matching Constructors)

模式匹配包含建構子模式的概念。這些模式允許你檢查並深入存取結構體和列舉，是模式匹配中最強大的部分之一。建構子模式配合變數綁定，允許你根據結構匹配數值，並提取出你感興趣的部分數值，以便在模式分支的右側使用。

請看以下範例：

```move
fun f(x: MyEnum): u64 {
    match (x) {
        MyEnum::Variant(1, true) => 1,
        MyEnum::OtherVariant(_, 3) => 2,
        MyEnum::Variant(..) => 3,
        MyEnum::OtherVariant(..) => 4,
    }
}
f(MyEnum::Variant(1, true)); // 回傳 1
f(MyEnum::Variant(2, true)); // 回傳 3
f(MyEnum::OtherVariant(false, 3)); // 回傳 2
f(MyEnum::OtherVariant(true, 3)); // 回傳 2
f(MyEnum::OtherVariant(true, 2)); // 回傳 4
```

這是在說：「如果 `x` 是帶有欄位 `1` 和 `true` 的 `MyEnum::Variant`，則回傳 `1`。如果它是 `MyEnum::OtherVariant` 且第一個欄位為任何值、第二個欄位為 `3`，則回傳 `2`。如果它是帶有任何欄位的 `MyEnum::Variant`，則回傳 `3`。最後，如果它是帶有任何欄位的 `MyEnum::OtherVariant`，則回傳 `4`」。

你還可以巢狀模式。因此，如果你想匹配 1、2 或 10，而不僅僅是匹配之前 `MyEnum::Variant` 中的 1，你可以使用 or 模式來實現：

```move
fun f(x: MyEnum): u64 {
    match (x) {
        MyEnum::Variant(1 | 2 | 10, true) => 1,
        MyEnum::OtherVariant(_, 3) => 2,
        MyEnum::Variant(..) => 3,
        MyEnum::OtherVariant(..) => 4,
    }
}
f(MyEnum::Variant(1, true)); // 回傳 1
f(MyEnum::Variant(2, true)); // 回傳 1
f(MyEnum::Variant(10, true)); // 回傳 1
f(MyEnum::Variant(10, false)); // 回傳 3
```

### 能力約束 (Ability Constraints)

此外，match 綁定受到與 Move 其他面向相同的能力限制。特別是，如果你嘗試使用萬用字元匹配一個沒有 `drop` 能力的數值（非參考），編譯器將發出錯誤，因為萬用字元預期會丟棄 (drop) 該數值。同樣地，如果你使用綁定器 (binder) 綁定了一個非 `drop` 數值，它必須在模式分支的右側使用。此外，如果你完全解構該值，你就已經拆解 (unpacked) 了它，這符合 [非 `drop` 結構體拆解](./../structs#透過模式匹配銷毀結構體-destroying-structs-via-pattern-matching) 的語義。詳情請參閱 [能力章節中的 `drop`](./../abilities#drop)。

```move
public struct NonDrop(u64)

fun drop_nondrop(x: NonDrop): u64 {
    match (x) {
        NonDrop(1) => 1,
        _ => 2
        // 錯誤：無法在不可丟棄的數值上進行萬用字元匹配
    }
}

fun destructure_nondrop(x: NonDrop): u64 {
    match (x) {
        NonDrop(1) => 1,
        NonDrop(_) => 2
        // 沒問題！
    }
}

fun use_nondrop(x: NonDrop): NonDrop {
    match (x) {
        NonDrop(1) => NonDrop(8),
        x => x
    }
}
```

## 窮舉性 (Exhaustiveness)

Move 中的 `match` 運算式必須是 **窮舉的**：被匹配型別的每個可能值都必須由 match 其中一個分支中的其中一個模式覆蓋。如果模式分支系列不具備窮舉性，編譯器將報錯。請注意，任何帶有守衛運算式的分支都不會對匹配窮舉性做出貢獻，因為它在執行階段可能會匹配失敗。

舉例來說，針對 `u8` 的匹配只有在匹配了從 0 到 255 的 **每個** 數字（除非存在萬用字元或變數模式）時才是窮舉的。同樣地，針對 `bool` 的匹配需要匹配 `true` 和 `false`，除非存在萬用字元或變數模式。

對於結構體，由於該型別只有一種建構子，因此只需匹配一個建構子，但結構體內的欄位也需要窮舉式匹配。相反地，列舉可能定義多個變體，且每個變體（包括任何子欄位）都必須被匹配，match 才會被認為是窮舉的。

因為底線和變數是匹配任何事物的萬用字元，所以它們算作匹配在該位置被匹配型別的所有數值。此外，多數量萬用字元模式 `..` 可用於匹配結構體或列舉變體內的多個數值。

要查看一些 **非窮舉性** 匹配的範例，請看以下內容：

```move
public enum MyEnum {
    Variant(u64, bool),
    OtherVariant(bool, u64),
}

public struct Pair<T>(T, T)

fun f(x: MyEnum): u8 {
    match (x) {
        MyEnum::Variant(1, true) => 1,
        MyEnum::Variant(_, _) => 1,
        MyEnum::OtherVariant(_, 3) => 2,
        // 錯誤：非窮舉，因為數值 `MyEnum::OtherVariant(_, 4)` 未被匹配。
    }
}

fun match_pair_bool(x: Pair<bool>): u8 {
    match (x) {
        Pair(true, true) => 1,
        Pair(true, false) => 1,
        Pair(false, false) => 1,
        // 錯誤：非窮舉，因為數值 `Pair(false, true)` 未被匹配。
    }
}
```

這些範例可以透過向模式分支末端加上萬用字元模式，或透過完全匹配剩餘數值來使其具備窮舉性：

```move
fun f(x: MyEnum): u8 {
    match (x) {
        MyEnum::Variant(1, true) => 1,
        MyEnum::Variant(_, _) => 1,
        MyEnum::OtherVariant(_, 3) => 2,
        // 現在是窮舉的，因為這將匹配 MyEnum::OtherVariant 的所有值
        MyEnum::OtherVariant(..) => 2,

    }
}

fun match_pair_bool(x: Pair<bool>): u8 {
    match (x) {
        Pair(true, true) => 1,
        Pair(true, false) => 1,
        Pair(false, false) => 1,
        // 現在是窮舉的，因為這將匹配 Pair<bool> 的所有值
        Pair(false, true) => 1,
    }
}
```

## 守衛 (Guards)

如前所述，你可以透過在模式後加上 `if` 子句來為模式分支加上守衛。此守衛將在模式匹配 **之後**、但在箭頭右側的運算式求值 **之前** 執行。如果守衛運算式的求值結果為 `true`，則評估箭頭右側的運算式；如果求值結果為 `false`，則將其視為失敗的匹配，並檢查 `match` 運算式中的下一個模式分支。

```move
fun match_with_guard(x: u64): u64 {
    match (x) {
        1 if (false) => 1,
        1 => 2,
        _ => 3,
    }
}

match_with_guard(1); // 回傳 2
match_with_guard(0); // 回傳 3
```

守衛運算式在求值期間可以參考模式中綁定的變數。但請注意，無論匹配模式為何 —— 即使變數上有可變性規範，或者模式是按值匹配的 —— _變數在守衛中僅作為不可變參考可用_。

```move
fun incr(x: &mut u64) {
    *x = *x + 1;
}

fun match_with_guard_incr(x: u64): u64 {
    match (x) {
        x if ({ incr(&mut x); x == 1 }) => 1,
        // 錯誤：    ^^^ 對不可變值的無效借用
        _ => 2,
    }
}

fun match_with_guard_incr2(x: &mut u64): u64 {
    match (x) {
        x if ({ incr(&mut x); x == 1 }) => 1,
        // 錯誤：    ^^^ 對不可變值的無效借用
        _ => 2,
    }
}
```

此外，重要的是要注意，任何帶有守衛運算式的模式分支都不會被考慮用於窮舉性分析，因為編譯器無法靜態求值守衛運算式。

## 特定模式的限制

關於在模式中何時、何地以及如何使用 `..` 和 `mut` 模式修飾符，存在一些限制。

### 可變性用法 (Mutability Usage)

可以在變數模式上放置 `mut` 修飾符，以指定該 **變數** 將在模式分支的右側運算式中被修改。請注意，由於 `mut` 修飾符僅表示該變數將被修改，而非底層資料，因此這可以用於所有型別的匹配（按值、不可變參考和可變參考）。

請注意，`mut` 修飾符只能應用於變數，而不能應用於其他型別的模式。

```move
public struct MyStruct(u64)

fun top_level_mut(x: MyStruct): u64 {
    match (x) {
        mut MyStruct(y) => 1,
        // 錯誤：不能在非變數模式上使用 mut
    }
}

fun mut_on_immut(x: &MyStruct): u64 {
    match (x) {
        MyStruct(mut y) => {
            y = &(*y + 1);
            *y
        }
    }
}

fun mut_on_value(x: MyStruct): u64 {
    match (x) {
        MyStruct(mut y) => {
            *y = *y + 1;
            *y
        },
    }
}

fun mut_on_mut(x: &mut MyStruct): u64 {
    match (x) {
        MyStruct(mut y) => {
            *y = *y + 1;
            *y
        },
    }
}

let mut x = MyStruct(1);

mut_on_mut(&mut x); // 回傳 2
x.0; // 回傳 2

mut_on_immut(&x); // 回傳 3
x.0; // 回傳 2

mut_on_value(x); // 回傳 3
```

### `..` 用法

`..` 模式只能在建構子模式中作為萬用字元使用，以匹配任意數量的欄位 —— 編譯器會將 `..` 展開為在建構子模式（如果有）中任何缺失的欄位中插入 `_`。因此，`MyStruct(_, _, _)` 與 `MyStruct(..)` 相同，`MyStruct(1, _, _)` 與 `MyStruct(1, ..)` 相同。正因如此，關於 `..` 模式的使用方式和位置存在一些限制：

- 它在建構子模式中只能使用 **一次**；
- 在位置參數 (positional arguments) 中，它可以用於建構子內模式的開頭、中間或結尾；
- 在具名參數 (named arguments) 中，它只能用於建構子內模式的結尾。

```move
public struct MyStruct(u64, u64, u64, u64) has drop;

public struct MyStruct2 {
    x: u64,
    y: u64,
    z: u64,
    w: u64,
}

fun wild_match(x: MyStruct): u64 {
    match (x) {
        MyStruct(.., 1) => 1,
        // OK! `..` 模式可用於建構子模式的開頭
        MyStruct(1, ..) => 2,
        // OK! `..` 模式可用於建構子模式的結尾
        MyStruct(1, .., 1) => 3,
        // OK! `..` 模式可用於建構子模式的中間
        MyStruct(1, .., 1, 1) => 4,
        MyStruct(..) => 5,
    }
}

fun wild_match2(x: MyStruct2): u64 {
    match (x) {
        MyStruct2 { x: 1, .. } => 1,
        MyStruct2 { x: 1, w: 2 .. } => 2,
        MyStruct2 { .. } => 3,
    }
}
```
