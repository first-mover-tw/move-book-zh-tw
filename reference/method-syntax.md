---
title: 方法語法 | 參考手冊
description: Move 方法語法參考：使用點記法呼叫函式、接收者型別、自動借用與方法解析。
keywords:
  - Move
  - Sui
  - Move reference
  - method
  - syntax
  - reference
questions:
  - How does Method Syntax work in Move?
  - What is the syntax for Method Syntax in Move?
  - What is Method Resolution in Move?
  - What is Automatic Borrowing in Move?
answer: 'Move method syntax reference: call functions with dot notation, receiver types, automatic borrowing, and method resolution.'
goal:
  description: 'Reader understands move method syntax reference: call functions with dot notation, receiver types, automatic borrowing, and method resolution'
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

# 方法 (Methods) {#methods}

作為語法上的便利功能，Move 中的某些函式可以在值上以「方法」形式呼叫。這是透過使用 `.` 運算子來呼叫函式；`.` 左側的值會成為函式的第一個引數（有時稱為接收者）。該值的型別會在靜態階段決定要呼叫哪個函式。這與某些其他語言的重要差異在於，其他語言中的此語法可能表示動態呼叫，也就是要呼叫的函式會在執行階段決定。在 Move 中，所有函式呼叫都會在靜態階段決定。

簡而言之，這個語法的存在是為了讓你不必透過 `use` 建立別名，也不必明確借用函式的第一個引數，即可更容易地呼叫函式。此外，這也能讓原始碼更易讀，因為它減少了呼叫函式所需的樣板程式碼，並讓串接函式呼叫更加容易。

## 語法 (Syntax) {#syntax}

呼叫方法的語法如下：

```text
<expression> . <identifier> <[type_arguments],*> ( <arguments> )
```

例如：

```move
coin.value();
*nums.borrow_mut(i) = 5;
```

## 方法解析 (Method Resolution) {#method-resolution}

呼叫方法時，編譯器會根據接收者（`.` 左側的引數）的型別，以靜態方式判定要呼叫哪個函式。編譯器會維護從型別與方法名稱到應呼叫之模組和函式名稱的對應。此對應是由目前位於作用域內的 `use fun` 別名，以及接收者型別定義模組中的適當函式所建立。在所有情況下，無論是按值或按參考傳遞，接收者型別都是函式的第一個引數。

在本節中，當我們說一個方法「解析」為某個函式時，表示編譯器會以靜態方式將該方法替換為一般的[函式](./functions)呼叫。例如，若有 `x.foo(e)`，且 `foo` 解析為 `a::m::foo`，編譯器會將 `x.foo(e)` 替換為 `a::m::foo(x, e)`，並可能對 `x` 進行[自動借用](#automatic-borrowing)。

### 定義模組中的函式 (Functions in the Defining Module) {#functions-in-the-defining-module}

在型別的定義模組中，當型別是函式第一個引數時，編譯器會自動為其型別的任何函式
宣告建立方法別名。例如：

```move
module a::m;

public struct X() has copy, drop, store;
public fun foo(x: &X) { ... }
public fun bar(flag: bool, x: &X) { ... }
```

函式 `foo` 可以作為型別 `X` 值上的方法呼叫。然而，`bar` 的第一個引數不是 `X`
（而且不會為 `bool` 建立別名，因為 `bool` 並未在該模組中定義）。例如：

```move
fun example(x: a::m::X) {
    x.foo(); // 有效
    // x.bar(true); 錯誤！
}
```

### `use fun` 別名 (`use fun` Aliases) {#use-fun-aliases}

如同傳統的 [`use`](uses)，`use fun` 陳述式會建立一個僅限於目前範圍的別名。此範圍可能是目前模組或目前的運算式區塊。不過，該別名會與某個型別關聯。

`use fun` 陳述式的語法如下：

```move
use fun <function> as <type>.<method alias>;
```

這會為 `<function>` 建立別名，而 `<type>` 可以將其作為 `<method alias>` 接收。

例如：

```move
module a::cup;

public struct Cup<T>(T) has copy, drop, store;

public fun cup_borrow<T>(c: &Cup<T>): &T {
    &c.0
}

public fun cup_value<T>(c: Cup<T>): T {
    let Cup(t) = c;
    t
}

public fun cup_swap<T: drop>(c: &mut Cup<T>, t: T) {
    c.0 = t;
}
```

現在可以為這些函式建立 `use fun` 別名：

```move
module b::example;

use fun a::cup::cup_borrow as Cup.borrow;
use fun a::cup::cup_value as Cup.value;
use fun a::cup::cup_swap as Cup.set;

fun example(c: &mut Cup<u64>) {
    let _ = c.borrow(); // 解析為 a::cup::cup_borrow
    let v = c.value(); // 解析為 a::cup::cup_value
    c.set(v * 2); // 解析為 a::cup::cup_swap
}
```

請注意，`use fun` 中的 `<function>` 不必是完全解析的路徑，也可以改用別名。因此，上述範例中的宣告也可以等效地寫成：

```move
use a::cup::{Self, cup_swap};

use fun cup::cup_borrow as Cup.borrow;
use fun cup::cup_value as Cup.value;
use fun cup_swap as Cup.set;
```

雖然這些範例只是為目前模組中的函式重新命名，但此功能對於宣告其他模組型別上的方法可能更實用。例如，如果想為 `Cup` 新增一項實用工具，可以使用 `use fun` 別名，同時仍採用方法語法：

```move
module b::example;

fun double(c: &Cup<u64>): Cup<u64> {
    let v = c.value();
    Cup::new(v * 2)
}
```

一般情況下，由於 `b::example` 並未定義 `Cup`，只能以 `double(&c)` 的方式呼叫它；但可以改用 `use fun` 別名：

```move
fun double_double(c: Cup<u64>): (Cup<u64>, Cup<u64>) {
    use fun b::example::double as Cup.dub;
    (c.dub(), c.dub()) // 兩次呼叫皆解析為 b::example::double
}
```

雖然可以在任何範圍內建立 `use fun`，但 `use fun` 的目標 `<function>` 必須有一個與 `<type>` 相同的第一個引數。

```move
public struct X() has copy, drop, store;

fun new(): X { X() }
fun flag(flag: bool): u8 { if (flag) 1 else 0 }

use fun new as X.new; // 錯誤！
use fun flag as X.flag; // 錯誤！
// `new` 和 `flag` 的第一個引數都不是 `X` 型別
```

但可以使用 `<type>` 的任何第一個引數形式，包括參考與可變參考：

```move
public struct X() has copy, drop, store;

public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

// 三者皆有效，且可在任何範圍內使用
use fun by_val as X.v;
use fun by_ref as X.r;
use fun by_mut as X.m;
```

請注意，對於泛型而言，這些方法會與泛型型別的 _所有_ 實例關聯。你無法多載方法，使其依據具現化而解析為不同函式。

```move
public struct Cup<T>(T) has copy, drop, store;

public fun value<T: copy>(c: &Cup<T>): T {
    c.0
}

use fun value as Cup<bool>.flag; // 錯誤！
use fun value as Cup<u64>.num; // 錯誤！
// 兩種情況中的 `use fun` 別名都不能是泛型；它們必須適用於該型別的所有實例
```

### `public use fun` 別名 (`public use fun` Aliases) {#public-use-fun-aliases}

與傳統的 [`use`](uses) 不同，`use fun` 陳述式可以設為 `public`，使其能在宣告範圍外使用。若 `use fun` 宣告於定義接收者型別的模組中，便可設為 `public`，這與定義模組中函式會[自動建立](#functions-in-the-defining-module)方法別名的方式相似。反過來看，也可以認為：定義模組中每個第一個引數為接收者型別的函式（若該型別定義於該模組中），都會自動建立隱含的 `public use fun`。這兩種觀點是等價的。

```move
module a::cup;

public struct Cup<T>(T) has copy, drop, store;

public use fun cup_borrow as Cup.borrow;
public fun cup_borrow<T>(c: &Cup<T>): &T {
    &c.0
}
```

在此範例中，會為 `a::cup::Cup.borrow` 與 `a::cup::Cup.cup_borrow` 建立公開方法別名。兩者皆會解析為 `a::cup::cup_borrow`。兩者也都具有「公開」性質，意即無須額外的 `use` 或 `use fun`，即可在 `a::cup` 外部使用。

```move
module b::example;

fun example<T: drop>(c: a::cup::Cup<u64>) {
    c.borrow(); // 解析為 a::cup::cup_borrow
    c.cup_borrow(); // 解析為 a::cup::cup_borrow
}
```

因此，若你想為以方法語法使用的函式提供更簡潔的名稱，`public use fun` 宣告可用於重新命名函式。若模組中有多個型別，且每個型別都有名稱相近的函式，這會特別有幫助。

```move
module a::shapes;

public struct Rectangle { base: u64, height: u64 }
public struct Box { base: u64, height: u64, depth: u64 }

// Rectangle 與 Box 可以有同名的方法

public use fun rectangle_base as Rectangle.base;
public fun rectangle_base(rectangle: &Rectangle): u64 {
    rectangle.base
}

public use fun box_base as Box.base;
public fun box_base(box: &Box): u64 {
    box.base
}
```

`public use fun` 的另一個用途是為其他模組中的型別新增方法。這在單一套件中搭配分散於各處的函式時會很有幫助。

```move
module a::cup {
    public struct Cup<T>(T) has copy, drop, store;

    public fun new<T>(t: T): Cup<T> { Cup(t) }
    public fun borrow<T>(c: &Cup<T>): &T {
        &c.0
    }
    // 對另一個模組中定義的函式使用 `public use fun`
    public use fun a::utils::split as Cup.split;
}

module a::utils {
    use a::m::{Self, Cup};

    public fun split<u64>(c: Cup<u64>): (Cup<u64>, Cup<u64>) {
        let Cup(t) = c;
        let half = t / 2;
        let rem = if (t > 0) t - half else 0;
        (cup::new(half), cup::new(rem))
    }

}
```

另請注意，此 `public use fun` 不會建立迴圈依賴，因為模組編譯後不會保留 `use fun`——所有方法都會以靜態方式解析。

### 與 `use` 別名互動 (Interactions with `use` Aliases) {#interactions-with-use-aliases}

需要注意的一個小細節是，方法別名會遵守一般的 `use` 別名。

```move
module a::cup {
    public struct Cup<T>(T) has copy, drop, store;

    public fun cup_borrow<T>(c: &Cup<T>): &T {
        &c.0
    }
}

module b::other {
    use a::cup::{Cup, cup_borrow as borrow};

    fun example(c: &Cup<u64>) {
        c.borrow(); // 解析為 a::cup::cup_borrow
    }
}
```

一種有用的理解方式是：只要可行，`use` 就會為函式建立隱含的 `use fun` 別名。在此情況下，`use a::cup::cup_borrow as borrow` 會建立隱含的 `use fun a::cup::cup_borrow as Cup.borrow`，因為它是有效的 `use fun` 別名。兩種觀點是等價的。這樣的推論可用來理解特定方法在遮蔽情況下將如何解析。如需更多詳細資訊，請參閱 [作用域](#scoping) 中的案例。

### 範圍界定 (Scoping) {#scoping}

若未標示為 `public`，`use fun` 別名僅在其範圍內有效，與一般的 [`use`](uses) 類似。例如：

```move
module a::m {
    public struct X() has copy, drop, store;
    public fun foo(_: &X) {}
    public fun bar(_: &X) {}
}

module b::other {
    use a::m::X;

    use fun a::m::foo as X.f;

    fun example(x: &X) {
        x.f(); // 解析為 a::m::foo
        {
            use a::m::bar as f;
            x.f(); // 解析為 a::m::bar
        };
        x.f(); // 仍解析為 a::m::foo
        {
            use fun a::m::bar as X.f;
            x.f(); // 解析為 a::m::bar
        }
    }
```

## 自動借用 (Automatic Borrowing) {#automatic-borrowing}

在解析方法時，如果函式預期接收參考，編譯器會自動借用接收者。例如：

```move
module a::m;

public struct X() has copy, drop;
public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

fun example(mut x: X) {
    x.by_ref(); // 解析為 a::m::by_ref(&x)
    x.by_mut(); // 解析為 a::m::by_mut(&mut x)
}
```

在這些範例中，`x` 分別自動借用為 `&x` 與 `&mut x`。這也適用於透過欄位存取：

```move
module a::m;

public struct X() has copy, drop;
public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

public struct Y has drop { x: X }

fun example(mut y: Y) {
    y.x.by_ref(); // 解析為 a::m::by_ref(&y.x)
    y.x.by_mut(); // 解析為 a::m::by_mut(&mut y.x)
}
```

請注意，在兩個範例中，區域變數都必須標記為 [`mut`](./variables)，才能允許 `&mut` 借用。否則會發生錯誤，指出 `x`（第二個範例中為 `y`）不可變。

請記住，若沒有參考，則會套用一般的變數與欄位存取規則。這表示若值未被借用，就可能被移動或複製。

```move
module a::m;

public struct X() has copy, drop;
public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

public struct Y has drop { x: X }
public fun drop_y(y: Y) { y }

fun example(y: Y) {
    y.x.by_val(); // 因為 `by_val` 是傳值且 `X` 具有 `copy`，所以複製 `y.x`
    y.drop_y(); // 因為 `drop_y` 是傳值且 `Y` _不_ 具有 `copy`，所以移動 `y`
}
```

## 串接 (Chaining) {#chaining}

方法呼叫可以串接，因為任何運算式都可以作為方法的接收者。

```move
module a::shapes {
    public struct Point has copy, drop, store { x: u64, y: u64 }
    public struct Line has copy, drop, store { start: Point, end: Point }

    public fun x(p: &Point): u64 { p.x }
    public fun y(p: &Point): u64 { p.y }

    public fun start(l: &Line): &Point { &l.start }
    public fun end(l: &Line): &Point { &l.end }

}

module b::example {
    use a::shapes::Line;

    public fun x_values(l: Line): (u64, u64) {
        (l.start().x(), l.end().x())
    }

}
```

在此範例中，對於 `l.start().x()`，編譯器會先將 `l.start()` 解析為
`a::shapes::start(&l)`。接著，`.x()` 會解析為 `a::shapes::x(a::shapes::start(&l))`。`l.end().x()` 的情況也相同。請記住，這項功能並不「特殊」——`.` 左側可以是任何運算式，編譯器會如常解析方法呼叫。我們特別指出這類「串接」，是因為這是提升可讀性的常見作法。
