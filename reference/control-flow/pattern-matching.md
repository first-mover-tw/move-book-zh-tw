---
title: 模式比對 (Pattern Matching) | 參考手冊
description: Move 模式比對 (pattern matching) 參考：match 運算式 (match expressions)、解構 (destructuring)、守衛 (guards)、萬用字元 (wildcards)，以及完整比對規則 (exhaustive matching rules)。
keywords:
  - Move
  - Sui
  - Move reference
  - pattern
  - matching
  - reference
  - design patterns
questions:
  - How does Pattern Matching work in Move?
  - What is the syntax for Pattern Matching in Move?
  - What is match Syntax in Move?
  - What is Pattern Syntax in Move?
answer: 'Move pattern matching reference: match expressions, destructuring, guards, wildcards, and exhaustive matching rules.'
goal:
  description: 'Reader understands move pattern matching reference: match expressions, destructuring, guards, wildcards, and exhaustive matching rules'
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

# 模式比對 (Pattern Matching) {#pattern-matching}

`match` 運算式是一種強大的控制結構，可讓你將某個值與一系列模式進行比較，然後根據最先符合的模式執行程式碼。模式可以是簡單的常值，也可以是複雜、巢狀的結構體與列舉定義。相較於會根據 `bool` 型別的測試運算式改變控制流程的 `if` 運算式，`match` 運算式可對任何型別的值運作，並從多個分支中選擇一個。

`match` 運算式可比對 Move 值，以及可變或不可變參考，並據此繫結子模式。

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

## `match` 語法 (`match` Syntax) {#match-syntax}

`match` 接受一個運算式與一系列以逗號分隔、非空的 _match 分支_。

每個 match 分支包含一個模式（`p`）、一個選用的守衛條件（`if (g)`，其中 `g` 是型別為 `bool` 的運算式）、一個箭頭（`=>`），以及當模式相符時要執行的分支運算式（`e`）。例如：

```move
match (expression) {
    pattern1 if (guard_expression) => expression1,
    pattern2 => expression2,
    pattern3 => { expression3, expression4, ... },
}
```

Match 分支會依序由上而下檢查，第一個相符的模式（若有守衛運算式，則其必須評估為 `true`）將會執行。

請注意，`match` 內的一系列 match 分支必須具備窮盡性，亦即被比對型別的每一種可能值，都必須由 `match` 中其中一個模式涵蓋。若這系列 match 分支不具備窮盡性，編譯器將會提出錯誤。

## 模式語法 (Pattern Syntax) {#pattern-syntax}

如果一個值等於某個模式，則該值會與該模式相符；其中變數與萬用字元（例如 `x`、`y`、`_` 或 `..`）會與任何值「相等」。

模式用於比對值。模式可以是：

| 模式           | 說明                                                            |
| -------------- | --------------------------------------------------------------- |
| 字面值         | 字面值，例如 `1`、`true`、`@0x1`                                |
| 常數           | 常數值，例如 `MyConstant`                                       |
| 變數           | 變數，例如 `x`、`y`、`z`                                        |
| 萬用字元       | 萬用字元，例如 `_`                                              |
| 建構子         | 建構子模式，例如 `MyStruct { x, y }`、`MyEnum::Variant(x)`      |
| At 模式        | At 模式，例如 `x @ MyEnum::Variant(..)`                         |
| Or 模式        | Or 模式，例如 `MyEnum::Variant(..) \| MyEnum::OtherVariant(..)` |
| 多元數萬用字元 | 多元數萬用字元，例如 `MyEnum::Variant(..)`                      |
| 可變綁定       | 可變綁定模式，例如 `mut x`                                      |

Move 中的模式具有以下文法：

```bnf
pattern = <literal>
        | <constant>
        | <variable>
        | _
        | C { <variable> : inner-pattern ["," <variable> : inner-pattern]* } // 其中 C 為結構或列舉變體
        | C ( inner-pattern ["," inner-pattern]* ... )                       // 其中 C 為結構或列舉變體
        | C                                                                  // 其中 C 為列舉變體
        | <variable> @ top-level-pattern
        | pattern | pattern
        | mut <variable>
inner-pattern = pattern
              | ..     // 多元數萬用字元
```

以下是一些模式範例：

```move
// 字面值模式
1

// 常數模式
MyConstant

// 變數模式
x

// 萬用字元模式
_

// 與欄位 `1` 和 `true` 的 `MyEnum::Variant` 相符的建構子模式
MyEnum::Variant(1, true)

// 與第一個欄位為 `1` 的 `MyEnum::Variant` 相符，並將第二個欄位的值綁定至 `x` 的建構子模式
MyEnum::Variant(1, x)

// 與 `MyEnum::Variant` 變體內多個欄位相符的多元數萬用字元模式
MyEnum::Variant(..)

// 與 `MyStruct` 的 `x` 欄位相符，並將 `y` 欄位綁定至 `other_variable` 的建構子模式
MyStruct { x, y: other_variable }

// 與 `MyEnum::Variant` 相符，並將整個值綁定至 `x` 的 At 模式
x @ MyEnum::Variant(..)

// 與 `MyEnum::Variant` 或 `MyEnum::OtherVariant` 任一者相符的 Or 模式
MyEnum::Variant(..) | MyEnum::OtherVariant(..)

// 與上述 Or 模式相同，但使用明確的萬用字元
MyEnum::Variant(_, _) | MyEnum::OtherVariant(_, _)

// 與 `MyEnum::Variant` 或 `MyEnum::OtherVariant` 任一者相符，並將 u64 欄位綁定至 `x` 的 Or 模式
MyEnum::Variant(x, _) | MyEnum::OtherVariant(_, x)

// 與 `OtherEnum::V` 相符，且其內部 `MyEnum` 為 `MyEnum::Variant` 的建構子模式
OtherEnum::V(MyEnum::Variant(..))
```

### 模式與變數 (Patterns and Variables) {#patterns-and-variables}

包含變數的模式會將其繫結至相符主體或正在比對的主體子元件。這些變數接著可用於任何比對守衛運算式，或用於比對分支的右側。例如：

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

### 組合模式 (Combining Patterns) {#combining-patterns}

模式可以巢狀使用，也可以使用 or 運算子（`|`）加以組合。例如，若模式 `p1` 或 `p2` 任一者符合受檢物件，`p1 | p2` 就會成功。此模式可出現在任何位置——可作為最上層模式，或作為另一個模式中的子模式。

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

### 部分模式的限制 (Restrictions on Some Patterns) {#restrictions-on-some-patterns}

`mut` 與 `..` 模式在可使用的時機、位置與方式上也有特定條件，如[特定模式的限制](#limitations-on-specific-patterns)所詳述。概括而言，`mut` 修飾詞只能用於變數模式，而 `..` 模式在建構子模式中只能使用一次——且不能作為頂層模式使用。

以下為 `..` 模式的*無效*用法，因為它被作為頂層模式使用：

```move
match (x) {
    .. => 1,
    // 錯誤：`..` 模式只能在建構子模式中使用
}

match (x) {
    MyStruct(.., ..) => 1,
    // 錯誤：    ^^  `..` 模式在建構子模式中只能使用一次
}
```

### 模式型別檢查 (Pattern Typing) {#pattern-typing}

模式不是運算式，但仍會進行型別檢查。這表示模式的型別必須與其所比對的值的型別相符。例如，模式 `1` 具有整數型別，模式 `MyEnum::Variant(1, true)` 的型別為 `MyEnum`，模式 `MyStruct { x, y }` 的型別為 `MyStruct`，而 `OtherStruct<bool> { x: true, y: 1}` 的型別為 `OtherStruct<bool>`。如果你嘗試比對的運算式型別與 `match` 中模式的型別不同，就會產生型別錯誤。例如：

```move
match (1) {
    // `true` 字面值模式的型別為 `bool`，因此這是型別錯誤。
    true => 1,
    // 型別錯誤：預期型別為 u64，找到 bool
    _ => 2,
}
```

同樣地，以下也會產生型別錯誤，因為 `MyEnum` 與 `MyStruct` 是不同的型別：

```move
match (MyStruct { x: 0, y: 0 }) {
    MyEnum::Variant(..) => 1,
    // 型別錯誤：預期型別為 MyEnum，找到 MyStruct
}
```

## 比對 (Matching) {#matching}

在深入探討模式比對的細節，以及值「比對」模式所代表的意義之前，先檢視幾個範例，以建立對此概念的直覺理解。

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

從這些範例中最重要的一點是：若值等於模式，則該模式會比對該值；而萬用字元／變數模式可比對任何值。這適用於常值、變數及常數。例如，在 `test_lit` 函式中，值 `1` 比對模式 `1`，值 `2` 比對模式 `2`，而值 `3` 比對萬用字元 `_`。同樣地，在 `test_var` 函式中，值 `1` 與值 `2` 都比對模式 `y`。

變數 `x` 可比對（或「等於」）任何值，而萬用字元 `_` 可比對任何值（但僅比對一個值）。或模式類似邏輯 OR：若值比對或模式中的任一模式，便會比對該模式，因此 `p1 | p2 | p3` 應讀為「比對 p1，或 p2，或 p3」。

### 比對建構子 (Matching Constructors) {#matching-constructors}

模式比對包含建構子模式的概念。這些模式可讓你檢查並存取 struct 與 enum 內部的深層內容，也是模式比對中最強大的部分之一。建構子模式搭配變數繫結，可讓你依據值的結構進行比對，並取出你關心、要在比對分支右側使用的值組成部分。

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

這表示：「若 `x` 是欄位值為 `1` 與 `true` 的 `MyEnum::Variant`，則回傳 `1`。若它是第一個欄位可為任意值、第二個欄位為 `3` 的 `MyEnum::OtherVariant`，則回傳 `2`。若它是欄位可為任意值的 `MyEnum::Variant`，則回傳 `3`。最後，若它是欄位可為任意值的 `MyEnum::OtherVariant`，則回傳 `4`。」

你也可以巢狀使用模式。因此，若你想在前述的 `MyEnum::Variant` 中比對 `1`、`2` 或 `10`，而不只是比對 `1`，可以使用 or-pattern：

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

### 能力限制 (Ability Constraints) {#ability-constraints}

此外，match 綁定與 Move 的其他面向一樣，受到相同的能力限制。
特別是，若你嘗試使用萬用字元比對不具備 `drop` 的值（非參考），編譯器將會回報錯誤，因為萬用字元預期會捨棄該值。同樣地，若你使用綁定器綁定不具備 `drop` 的值，則必須在 match 分支的右側使用該值。此外，若你完全解構該值，便已將它解包，這與[非 `drop` 結構解包](./../structs#destroying-structs-via-pattern-matching)的語意一致。如需 `drop` 能力的更多詳細資料，請參閱[能力章節中關於 `drop` 的內容](./../abilities#drop)。

```move
public struct NonDrop(u64)

fun drop_nondrop(x: NonDrop): u64 {
    match (x) {
        NonDrop(1) => 1,
        _ => 2
        // 錯誤：無法對不可捨棄的值使用萬用字元比對
    }
}

fun destructure_nondrop(x: NonDrop): u64 {
    match (x) {
        NonDrop(1) => 1,
        NonDrop(_) => 2
        // 可以！
    }
}

fun use_nondrop(x: NonDrop): NonDrop {
    match (x) {
        NonDrop(1) => NonDrop(8),
        x => x
    }
}
```

## 完整涵蓋 (Exhaustiveness) {#exhaustiveness}

Move 中的 `match` 運算式必須具備 _完整涵蓋性_：所比對型別的每一個可能值，
都必須由其中一個 match 分支中的其中一個模式涵蓋。如果一系列 match 分支
不完整涵蓋，編譯器就會引發錯誤。請注意，任何帶有防護運算式的分支都不會
對 match 的完整涵蓋性有所貢獻，因為它可能在執行階段無法比對成功。

舉例來說，只有在比對從 0 到 255（含）的 _每一個_ 數字時，對 `u8` 的 match
才是完整涵蓋，除非存在萬用字元或變數模式。同樣地，對 `bool` 的 match
必須同時比對 `true` 與 `false`，除非存在萬用字元或變數模式。

對於結構體，由於該型別只有一種建構子型別，因此只需要比對一個建構子，
但結構體內的欄位也必須完整涵蓋地比對。相反地，列舉可以定義多個變體，
而每個變體（包括任何子欄位）都必須被比對，該 match 才會被視為完整涵蓋。

由於底線與變數都是可比對任何內容的萬用字元，因此在該位置上，它們會被視為
比對了所比對型別的所有值。此外，多參數萬用字元模式 `..` 可用於比對結構體或
列舉變體中的多個值。

若要查看一些 _不完整涵蓋_ 的 match 範例，請考慮以下內容：

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
        // 錯誤：不完整涵蓋，因為未比對值 `MyEnum::OtherVariant(_, 4)`。
    }
}

fun match_pair_bool(x: Pair<bool>): u8 {
    match (x) {
        Pair(true, true) => 1,
        Pair(true, false) => 1,
        Pair(false, false) => 1,
        // 錯誤：不完整涵蓋，因為未比對值 `Pair(false, true)`。
    }
}
```

接著可以在 match 分支的結尾加入萬用字元模式，或完整比對其餘值，使這些範例變成完整涵蓋：

```move
fun f(x: MyEnum): u8 {
    match (x) {
        MyEnum::Variant(1, true) => 1,
        MyEnum::Variant(_, _) => 1,
        MyEnum::OtherVariant(_, 3) => 2,
        // 現在是完整涵蓋，因為這會比對 MyEnum::OtherVariant 的所有值
        MyEnum::OtherVariant(..) => 2,

    }
}

fun match_pair_bool(x: Pair<bool>): u8 {
    match (x) {
        Pair(true, true) => 1,
        Pair(true, false) => 1,
        Pair(false, false) => 1,
        // 現在是完整涵蓋，因為這會比對 Pair<bool> 的所有值
        Pair(false, true) => 1,
    }
}
```

## 守衛 (Guards) {#guards}

如先前所述，你可以在模式之後加入 `if` 子句，藉此為 match 分支新增守衛。此守衛會在模式完成比對*之後*、箭頭右側的運算式求值*之前*執行。若守衛運算式求值為 `true`，則會對箭頭右側的運算式求值；若求值為 `false`，則會將其視為比對失敗，並檢查 `match` 運算式中的下一個 match 分支。

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

守衛運算式在求值期間可以參考模式中繫結的變數。然而，請注意，無論要比對的模式為何，_變數在守衛中僅能作為不可變參考使用_——即使變數具有可變性指定詞，或模式是以值進行比對也一樣。

```move
fun incr(x: &mut u64) {
    *x = *x + 1;
}

fun match_with_guard_incr(x: u64): u64 {
    match (x) {
        x if ({ incr(&mut x); x == 1 }) => 1,
        // 錯誤：    ^^^ 對不可變值進行無效借用
        _ => 2,
    }
}

fun match_with_guard_incr2(x: &mut u64): u64 {
    match (x) {
        x if ({ incr(&mut x); x == 1 }) => 1,
        // 錯誤：    ^^^ 對不可變值進行無效借用
        _ => 2,
    }
}
```

此外，請務必注意，任何具有守衛運算式的 match 分支都不會納入窮盡性檢查，因為編譯器無法以靜態方式對守衛運算式求值。

## 特定模式的限制 (Limitations on Specific Patterns) {#limitations-on-specific-patterns}

在模式中使用 `..` 與 `mut` 模式修飾詞時，存在一些限制。

### 可變性使用方式 (Mutability Usage) {#mutability-usage}

可將 `mut` 修飾詞放在變數模式上，以指定在比對分支的右側運算式中要修改該 _變數_。請注意，由於 `mut` 修飾詞僅表示要修改變數，而非底層資料，因此可用於所有比對類型（依值、不可變參考及可變參考）。

請注意，`mut` 修飾詞只能套用於變數，不能套用於其他類型的模式。

```move
public struct MyStruct(u64)

fun top_level_mut(x: MyStruct): u64 {
    match (x) {
        mut MyStruct(y) => 1,
        // 錯誤：無法在非變數模式上使用 mut
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

### `..` 使用方式 (`..` Usage) {#usage}

`..` 模式只能在建構子模式內作為萬用字元使用，以比對任意數量的欄位 -- 編譯器會將 `..` 展開為在建構子模式中任何缺少的欄位插入 `_`（若有）。因此，`MyStruct(_, _, _)` 與 `MyStruct(..)` 相同，`MyStruct(1, _, _)` 與 `MyStruct(1, ..)` 相同。基於此，`..` 模式的使用方式與位置有一些限制：

- 它只能在建構子模式內使用**一次**；
- 在位置引數中，它可用於建構子內模式的開頭、中間或結尾；
- 在具名引數中，它只能用於建構子內模式的結尾；

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
        // 正確！`..` 模式可用於建構子模式的開頭
        MyStruct(1, ..) => 2,
        // 正確！`..` 模式可用於建構子模式的結尾
        MyStruct(1, .., 1) => 3,
        // 正確！`..` 模式可用於建構子模式的中間
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
