---
title: 方法語法 (Method Syntax) | 參考手冊
description: Move 方法語法參考手冊：以點號表示法呼叫函式，涵蓋接收者型別、自動借用與方法解析。
---

# 方法 (Methods)

為了語法上的便利，Move 中的某些函式可以作為值的「方法（methods）」來呼叫。這是透過使用 `.` 運算子來呼叫函式實現的，其中 `.` 左側的值是函式的第一個參數（有時稱為接收者，receiver）。該值的型別以靜態方式決定了呼叫哪個函式。這與其他一些語言有重要區別，在某些語言中，這種語法可能表示動態呼叫，即呼叫哪個函式是在執行時決定的。在 Move 中，所有函式呼叫都是靜態決定的。

簡而言之，這種語法的存在是為了讓呼叫函式變得更容易，而無需使用 `use` 建立別名，也無需顯式借用函式的第一個參數。此外，這可以使程式碼更具可讀性，因為它減少了呼叫函式所需的樣板程式碼（boilerplate），並使得鏈式呼叫函式更加容易。

## 語法 (Syntax)

呼叫方法的語法如下：

```text
<expression> . <identifier> <[type_arguments],*> ( <arguments> )
```

例如：

```move
coin.value();
*nums.borrow_mut(i) = 5;
```

## 方法解析 (Method Resolution)

當呼叫一個方法時，編譯器將根據接收者（`.` 左側的參數）的型別靜態地決定呼叫哪個函式。編譯器維護一個從型別和方法名稱到應呼叫的模組及函式名稱的映射。此映射是根據目前作用域內的 `use fun` 別名，以及接收者型別定義模組中的適當函式建立的。在所有情況下，接收者型別都是函式的第一個參數，無論是按值（by-value）還是按參考（by-reference）。

在本節中，當我們說一個方法「解析（resolves）」為一個函式時，是指編譯器將在靜態上把該方法替換為正常的 [函式](./functions) 呼叫。例如，如果我們有 `x.foo(e)`，且 `foo` 解析為 `a::m::foo`，編譯器會將 `x.foo(e)` 替換為 `a::m::foo(x, e)`，並可能 [自動借用](#自動借用-automatic-borrowing) `x`。

### 定義模組中的函式 (Functions in the Defining Module)

在型別的定義模組（defining module）中，當該型別作為函式的第一個參數時，編譯器將自動為其任何函式宣告建立方法別名。例如：

```move
module a::m;

public struct X() has copy, drop, store;
public fun foo(x: &X) { ... }
public fun bar(flag: bool, x: &X) { ... }
```

函式 `foo` 可以作為型別 `X` 的值的方法來呼叫。然而，由於 `bar` 的第一個參數不是 `X`，因此不會為其建立別名（且不會為 `bool` 建立別名，因為 `bool` 不是在該模組中定義的）。例如：

```move
fun example(x: a::m::X) {
    x.foo(); // 有效
    // x.bar(true); 錯誤！
}
```

### `use fun` 別名 (`use fun` Aliases)

與傳統的 [`use`](uses) 類似，`use fun` 陳述式會在其目前作用域建立一個區域別名。這可以是針對目前的模組或目前的運算式區塊。然而，該別名是與某個型別相關聯的。

`use fun` 陳述式的語法如下：

```move
use fun <function> as <type>.<method alias>;
```

這會為 `<function>` 建立一個別名，`<type>` 可以將其作為 `<method alias>` 接收。

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

我們現在可以為這些函式建立 `use fun` 別名：

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

請注意，`use fun` 中的 `<function>` 不需要是完全解析的路徑，也可以使用別名，因此上述範例中的宣告可以等效地寫為：

```move
use a::cup::{Self, cup_swap};

use fun cup::cup_borrow as Cup.borrow;
use fun cup::cup_value as Cup.value;
use fun cup_swap as Cup.set;
```

雖然這些重新命名當前模組函式的範例很簡潔，但該功能對於在其他模組的型別上宣告方法可能更有用。例如，如果我們想給 `Cup` 新增一個新的實用工具，我們可以透過 `use fun` 別名來達成，並且仍然使用方法語法：

```move
module b::example;

fun double(c: &Cup<u64>): Cup<u64> {
    let v = c.value();
    Cup::new(v * 2)
}
```

通常，我們只能將其呼叫為 `double(&c)`，因為 `b::example` 沒有定義 `Cup`，但我們可以改用 `use fun` 別名：

```move
fun double_double(c: Cup<u64>): (Cup<u64>, Cup<u64>) {
    use fun b::example::double as Cup.dub;
    (c.dub(), c.dub()) // 兩次呼叫均解析為 b::example::double
}
```

雖然 `use fun` 可以在任何作用域中建立，但 `use fun` 的目標 `<function>` 的第一個參數必須與 `<type>` 相同。

```move
public struct X() has copy, drop, store;

fun new(): X { X() }
fun flag(flag: bool): u8 { if (flag) 1 else 0 }

use fun new as X.new; // 錯誤！
use fun flag as X.flag; // 錯誤！
// `new` 和 `flag` 的第一個參數型別都不是 `X`
```

但可以使用 `<type>` 的任何形式的第一個參數，包括參考和可變參考：

```move
public struct X() has copy, drop, store;

public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

// 在任何作用域中這 3 個都有效
use fun by_val as X.v;
use fun by_ref as X.r;
use fun by_mut as X.m;
```

注意對於泛型（generics），方法與泛型型別的 _所有_ 實例相關聯。你不能多載方法使其根據實例化而解析為不同的函式。

```move
public struct Cup<T>(T) has copy, drop, store;

public fun value<T: copy>(c: &Cup<T>): T {
    c.0
}

use fun value as Cup<bool>.flag; // 錯誤！
use fun value as Cup<u64>.num; // 錯誤！
// 在這兩種情況下，`use fun` 別名不能是特定的泛型實例，它們必須適用於該型別的所有實例
```

### `public use fun` 別名 (`public use fun` Aliases)

與傳統的 [`use`](uses) 不同，`use fun` 陳述式可以設定為 `public`，這允許它在其宣告的作用域之外使用。如果 `use fun` 是在定義接收者型別的模組中宣告的，則可以將其設定為 `public`，這就像為定義模組中的函式 [自動建立](#定義模組中的函式-functions-in-the-defining-module) 的方法別名一樣。或者相反地，可以認為為定義模組中第一個參數為接收者型別（如果是在該模組中定義的）的每個函式自動建立了一個隱式的 `public use fun`。這兩種觀點是等效的。

```move
module a::cup;

public struct Cup<T>(T) has copy, drop, store;

public use fun cup_borrow as Cup.borrow;
public fun cup_borrow<T>(c: &Cup<T>): &T {
    &c.0
}
```

在這個例子中，為 `a::cup::Cup.borrow` 和 `a::cup::Cup.cup_borrow` 建立了一個公開的方法別名。兩者都解析為 `a::cup::cup_borrow`。兩者在「公開」的意義上是一致的，即它們可以在 `a::cup` 之外使用，而無需額外的 `use` 或 `use fun`。

```move
module b::example;

fun example<T: drop>(c: a::cup::Cup<u64>) {
    c.borrow(); // 解析為 a::cup::cup_borrow
    c.cup_borrow(); // 解析為 a::cup::cup_borrow
}
```

因此，`public use fun` 宣告可以作為一種重命名函式的方法，如果你想給它一個更簡潔的名稱以配合方法語法。如果你有一個包含多個型別的模組，並且每個型別都有類似名稱的函式，這會特別有幫助。

```move
module a::shapes;

public struct Rectangle { base: u64, height: u64 }
public struct Box { base: u64, height: u64, depth: u64 }

// Rectangle 和 Box 可以有相同名稱的方法

public use fun rectangle_base as Rectangle.base;
public fun rectangle_base(rectangle: &Rectangle): u64 {
    rectangle.base
}

public use fun box_base as Box.base;
public fun box_base(box: &Box): u64 {
    box.base
}
```

`public use fun` 的另一個用途是向來自其他模組的型別新增方法。這在與分佈在單個套件中的函式結合使用時非常有幫助。

```move
module a::cup {
    public struct Cup<T>(T) has copy, drop, store;

    public fun new<T>(t: T): Cup<T> { Cup(t) }
    public fun borrow<T>(c: &Cup<T>): &T {
        &c.0
    }
    // `public use fun` 指向定義在另一個模組中的函式
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

請注意，這個 `public use fun` 不會建立環狀依賴，因為在模組編譯後 `use fun` 就不再存在了——所有方法都是靜態解析的。

### 與 `use` 別名的互動 (Interactions with `use` Aliases)

需要注意的一個小細節是，方法別名遵循正常的 `use` 別名規則。

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

理解這一點的一個好方法是，只要可能，`use` 就會為函式建立一個隱式的 `use fun` 別名。在這種情況下，`use a::cup::cup_borrow as borrow` 建立了一個隱式的 `use fun a::cup::cup_borrow as Cup.borrow`，因為它是一個有效的 `use fun` 別名。這兩種觀點是等效的。這種推理方式可以指導特定的方法將如何透過遮蔽（shadowing）來解析。詳細資訊請參見 [作用域](#scoping) 中的案例。

### 作用域 (Scoping) {#scoping}

如果不是 `public`，`use fun` 別名在其作用域內是局部的，就像正常的 [`use`](uses) 一樣。例如：

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
        x.f(); // 仍然解析為 a::m::foo
        {
            use fun a::m::bar as X.f;
            x.f(); // 解析為 a::m::bar
        }
    }
```

## 自動借用 (Automatic Borrowing)

在解析方法時，如果函式預期的是一個參考，編譯器將自動借用接收者。例如：

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

在這些範例中，`x` 分別被自動借用為 `&x` 和 `&mut x`。這同樣適用於欄位存取：

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

請注意，在這兩個範例中，區域變數都必須標記為 [`mut`](./variables) 以允許 `&mut` 借用。如果沒有這個標記，將會出現錯誤，指出 `x`（或第二個範例中的 `y`）不是可變的。

請記住，在沒有參考的情況下，變數和欄位存取的正常規則就會生效。這意味著如果值不被借用，它可能會被移動或複製。

```move
module a::m;

public struct X() has copy, drop;
public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

public struct Y has drop { x: X }
public fun drop_y(y: Y) { y }

fun example(y: Y) {
    y.x.by_val(); // 複製 `y.x`，因為 `by_val` 是按值傳遞且 `X` 具備 `copy`
    y.drop_y(); // 移動 `y`，因為 `drop_y` 是按值傳遞且 `Y` 不具備 `copy`
}
```

## 鏈式呼叫 (Chaining)

方法呼叫可以鏈式進行，因為任何運算式都可以作為方法的接收者。

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

在此範例的 `l.start().x()` 中，編譯器首先將 `l.start()` 解析為 `a::shapes::start(&l)`。然後將 `.x()` 解析為 `a::shapes::x(a::shapes::start(&l))`。`l.end().x()` 同理。請記住，此功能並非「特殊」的——`.` 左側可以是任何運算式，編譯器將照常解析方法呼叫。我們只是特別指出這種「鏈式呼叫」，因為它是提高可讀性的常見做法。
