---
title: '方法語法 (Method Syntax) | 參考手冊'
description: "Move 方法語法參考：使用點號標記法呼叫函式、接收者型別、自動借用、以及方法解析。"
---

# 方法 (Methods)

作為一種語法便利性，Move 中的某些函式可以作為值上的「方法」呼叫。這是通過使用 `.` 運算子來呼叫函式，其中 `.` 左側的值是該函式的第一個引數（有時稱為接收者）。該值的類型靜態決定了呼叫哪個函式。這與某些其他語言的重要區別在於，在那些語言中，此語法可能指示動態呼叫，其中待呼叫的函式在執行時期確定。在 Move 中，所有函式呼叫都是靜態確定的。

簡單來說，這種語法的存在是為了使呼叫函式變得更容易，無需用 `use` 建立別名，也無需顯式借用函式的第一個引數。此外，這可以使程式碼更具可讀性，因為它減少了呼叫函式所需的樣板程式碼，並使鏈式呼叫函式變得更容易。

## 語法

呼叫方法的語法如下：

```text
<expression> . <identifier> <[type_arguments],*> ( <arguments> )
```

例如

```move
coin.value();
*nums.borrow_mut(i) = 5;
```

## 方法解析

當呼叫方法時，編譯器將根據接收者（`.` 左側的引數）的類型靜態確定呼叫哪個函式。編譯器維護一個從類型和方法名稱到應呼叫的模組和函式名稱的映射。此映射是從目前範圍內的 `use fun` 別名以及接收者類型定義模組中的適當函式建立的。在所有情況下，接收者類型都是函式的第一個引數，無論是按值傳遞還是按參考傳遞。

在本節中，當我們說方法「解析」為函式時，我們指的是編譯器將靜態地將該方法替換為普通[函式](./functions)呼叫。例如，如果我們有 `x.foo(e)` 且 `foo` 解析為 `a::m::foo`，編譯器將把 `x.foo(e)` 替換為 `a::m::foo(x, e)`，可能會[自動借用](#自動借用) `x`。

### 定義模組中的函式

在類型的定義模組中，當類型是函式的第一個引數時，編譯器將自動為其類型的任何函式宣告建立方法別名。例如，

```move
module a::m;

public struct X() has copy, drop, store;
public fun foo(x: &X) { ... }
public fun bar(flag: bool, x: &X) { ... }
```

函式 `foo` 可以作為 `X` 類型值上的方法呼叫。然而，並非第一個引數（也不會為 `bool` 建立，因為 `bool` 未在該模組中定義）。例如，

```move
fun example(x: a::m::X) {
    x.foo(); // 有效
    // x.bar(true); 錯誤！
}
```

### `use fun` 別名

與傳統的 [`use`](uses) 類似，`use fun` 陳述式建立一個別名，該別名的作用域限於其目前的範圍。這可能是當前模組或當前表達式區塊。但是，該別名與類型相關聯。

`use fun` 陳述式的語法如下：

```move
use fun <function> as <type>.<method alias>;
```

這為 `<function>` 建立一個別名，`<type>` 可以以 `<method alias>` 的形式接收該別名。

例如

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

我們現在可以為這些函式建立 `use fun` 別名

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

請注意，`use fun` 中的 `<function>` 不必是完全解析的路徑，可以改用別名，因此上面範例中的宣告可以等價地寫成

```move
use a::cup::{Self, cup_swap};

use fun cup::cup_borrow as Cup.borrow;
use fun cup::cup_value as Cup.value;
use fun cup_swap as Cup.set;
```

雖然這些範例對於在當前模組中重新命名函式很巧妙，但該功能對於宣告來自其他模組的類型上的方法可能更有用。例如，如果我們想為 `Cup` 新增實用程式，我們可以使用 `use fun` 別名並仍然使用方法語法

```move
module b::example;

fun double(c: &Cup<u64>): Cup<u64> {
    let v = c.value();
    Cup::new(v * 2)
}
```

通常，我們會被困在必須將其呼叫為 `double(&c)`，因為 `b::example` 未定義 `Cup`，但相反我們可以使用 `use fun` 別名

```move
fun double_double(c: Cup<u64>): (Cup<u64>, Cup<u64>) {
    use fun b::example::double as Cup.dub;
    (c.dub(), c.dub()) // 在兩次呼叫中都解析為 b::example::double
}
```

雖然 `use fun` 可以在任何範圍內建立，但 `use fun` 的目標 `<function>` 必須具有與 `<type>` 相同的第一個引數。

```move
public struct X() has copy, drop, store;

fun new(): X { X() }
fun flag(flag: bool): u8 { if (flag) 1 else 0 }

use fun new as X.new; // 錯誤！
use fun flag as X.flag; // 錯誤！
// `new` 和 `flag` 都沒有類型為 `X` 的第一個引數
```

但 `<type>` 的任何第一個引數都可以使用，包括參考和可變參考

```move
public struct X() has copy, drop, store;

public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

// 這 3 個都有效，在任何範圍內
use fun by_val as X.v;
use fun by_ref as X.r;
use fun by_mut as X.m;
```

請注意，對於泛型，方法與通用類型的 _所有_ 實例相關聯。您無法多載方法以根據具體化解析為不同的函式。

```move
public struct Cup<T>(T) has copy, drop, store;

public fun value<T: copy>(c: &Cup<T>): T {
    c.0
}

use fun value as Cup<bool>.flag; // 錯誤！
use fun value as Cup<u64>.num; // 錯誤！
// 在兩種情況下，`use fun` 別名都不能是泛型，它們必須適用於類型的所有實例
```

### `public use fun` 別名

與傳統的 [`use`](uses) 不同，`use fun` 陳述式可以是 `public` 的，這允許它在其宣告的範圍之外使用。`use fun` 可以是 `public` 的條件是它在定義接收者類型的模組中宣告，就像為定義模組中的函式自動建立的方法別名一樣。或者，反過來，可以認為對於定義模組中的每個函式，如果其第一個引數是接收者類型（如果它在該模組中定義），則隱式建立 `public use fun`。這兩種觀點是等價的。

```move
module a::cup;

public struct Cup<T>(T) has copy, drop, store;

public use fun cup_borrow as Cup.borrow;
public fun cup_borrow<T>(c: &Cup<T>): &T {
    &c.0
}
```

在此範例中，為 `a::cup::Cup.borrow` 和 `a::cup::Cup.cup_borrow` 建立了公開方法別名。兩者都解析為 `a::cup::cup_borrow`。並且兩者在「公開」的意義上都是可用的，即它們可以在 `a::cup` 之外使用，無需額外的 `use` 或 `use fun`。

```move
module b::example;

fun example<T: drop>(c: a::cup::Cup<u64>) {
    c.borrow(); // 解析為 a::cup::cup_borrow
    c.cup_borrow(); // 解析為 a::cup::cup_borrow
}
```

`public use fun` 宣告因此可用作重新命名函式的方式，如果您想為方法語法使用更簡潔的名稱。這在您有一個模組包含多個類型以及每個類型的類似命名函式時特別有幫助。

```move
module a::shapes;

public struct Rectangle { base: u64, height: u64 }
public struct Box { base: u64, height: u64, depth: u64 }

// Rectangle 和 Box 可以擁有具有相同名稱的方法

public use fun rectangle_base as Rectangle.base;
public fun rectangle_base(rectangle: &Rectangle): u64 {
    rectangle.base
}

public use fun box_base as Box.base;
public fun box_base(box: &Box): u64 {
    box.base
}
```

`public use fun` 的另一個用途是為來自其他模組的類型新增方法。這在與散佈在單個套件中的函式結合使用時非常有幫助。

```move
module a::cup {
    public struct Cup<T>(T) has copy, drop, store;

    public fun new<T>(t: T): Cup<T> { Cup(t) }
    public fun borrow<T>(c: &Cup<T>): &T {
        &c.0
    }
    // 指向定義在另一個模組中的函式的 `public use fun`
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

並請注意，此 `public use fun` 不會建立循環依賴，因為 `use fun` 在模組編譯後不存在——所有方法都是靜態解析的。

### 與 `use` 別名的互動

需要注意的一個細節是方法別名尊重普通 `use` 別名。

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

一個有幫助的想法是 `use` 在它能做到時為函式建立隱式 `use fun` 別名。在此情況下，`use a::cup::cup_borrow as borrow` 建立了隱含的 `use fun a::cup::cup_borrow as Cup.borrow`，因為它將成為有效的 `use fun` 別名。兩種觀點是等價的。這條推理線可以告知使用遮蔽時特定方法將如何解析。有關更多詳情，請參閱[範圍](#範圍)中的情況。

### 範圍 (Scoping)

如果不是 `public`，`use fun` 別名在其範圍內是本地的，很像普通的 [`use`](uses)。例如

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

## 自動借用

解析方法時，如果函式期望參考，編譯器會自動借用接收者。例如

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

在這些範例中，`x` 分別自動借用到 `&x` 和 `&mut x`。這也可以通過欄位存取運作

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

請注意，在這兩個範例中，本地變數都必須標記為 [`mut`](./variables) 以允許 `&mut` 借用。如果沒有這個，會出現一個錯誤，說 `x`（或第二個範例中的 `y`）不可變。

請記住，沒有參考的情況下，變數和欄位存取的普通規則適用。意味著如果不借用值，值可能會被移動或複製。

```move
module a::m;

public struct X() has copy, drop;
public fun by_val(_: X) {}
public fun by_ref(_: &X) {}
public fun by_mut(_: &mut X) {}

public struct Y has drop { x: X }
public fun drop_y(y: Y) { y }

fun example(y: Y) {
    y.x.by_val(); // 複製 `y.x`，因為 `by_val` 是按值傳遞且 `X` 有 `copy`
    y.drop_y(); // 移動 `y`，因為 `drop_y` 是按值傳遞且 `Y` 沒有 `copy`
}
```

## 鏈式呼叫 (Chaining)

方法呼叫可以鏈式呼叫，因為任何表達式都可以是方法的接收者。

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

在此範例中，對於 `l.start().x()`，編譯器首先將 `l.start()` 解析為 `a::shapes::start(&l)`。然後 `.x()` 解析為 `a::shapes::x(a::shapes::start(&l))`。對 `l.end().x()` 類似。請記住，此功能不是「特殊的」——`.` 左側可以是任何表達式，編譯器將如常解析方法呼叫。我們簡單地重點指出這種「鏈式」呼叫，因為它是提高可讀性的常見做法。
