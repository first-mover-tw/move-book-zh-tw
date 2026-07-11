---
title: 區域變數與作用域 (Local Variables and Scope) | 參考手冊
description:
  Move 區域變數與作用域 (Move Local Variables and Scope)：let 綁定、可變性、型別標註、遮蔽 (shadowing)
  與 move 語義參考手冊
---

# 區域變數與作用域 (Local Variables and Scope) {#local-variables-and-scope}

Move 中的區域變數是詞法（靜態）作用域的。新變數用關鍵字 `let` 引入，這會遮蔽任何先前同名的區域變數。標記為 `mut` 的區域變數是可變的，可以直接更新，也可以透過可變參考來更新。

## 宣告區域變數 (Declaring Local Variables) {#declaring-local-variables}

### `let` 綁定 (`let` bindings) {#let-bindings}

Move 程式使用 `let` 將變數名稱綁定到值：

```move
let x = 1;
let y = x + x;
```

`let` 也可以在不綁定值到區域變數的情況下使用。

```move
let x;
```

之後可以再賦值給該區域變數。

```move
let x;
if (cond) {
  x = 1
} else {
  x = 0
}
```

當試圖從迴圈中取出一個值，而又無法提供預設值時，這會非常有幫助。

```move
let x;
let mut i = 0;
loop {
    let (res, cond) = foo(i);
    if (!cond) {
        x = res;
        break
    };
    i = i + 1;
}
```

若要在賦值*之後*修改區域變數，或以可變參考（`&mut`）借用它，該變數必須宣告為 `mut`。

```move
let mut x = 0;
if (cond) x = x + 1;
foo(&mut x);
```

更多細節請參閱下方[賦值](#assignments)章節。

### 變數必須先賦值才能使用 (Variables must be assigned before use) {#variables-must-be-assigned-before-use}

Move 的型別系統會防止區域變數在賦值之前就被使用。

```move
let x;
// highlight-error
x + x // 錯誤！x 在賦值之前就被使用
```

```move
let x;
if (cond) x = 0;
// highlight-error
x + x // 錯誤！x 並非在所有情況下都有值
```

```move
let x;
while (cond) x = 0;
// highlight-error
x + x // 錯誤！x 並非在所有情況下都有值
```

### 有效變數名稱 (Valid variable names) {#valid-variable-names}

變數名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z`、以及數字 `0`
到 `9`。變數名稱必須以底線 `_` 或字母 `a` 到 `z` 開頭。它們
_不能_ 以大寫字母開頭。

```move
// all valid
let x = e;
let _x = e;
let _A = e;
let x0 = e;
let xA = e;
let foobar_123 = e;

// all invalid
// highlight-error-start
let X = e; // ERROR!
let Foo = e; // ERROR!
// highlight-error-end
```

### 型別標註 (Type annotations) {#type-annotations}

區域變數的型別幾乎都能被 Move 的型別系統推斷出來。不過，Move
允許明確的型別標註，這在可讀性、清晰度或除錯時很有用。新增型別標註的
語法如下：

```move
let x: T = e; // "變數 x 的型別為 T，並初始化為運算式 e"
```

一些明確型別標註的範例：

```move
module 0::example;

public struct S { f: u64, g: u64 }

fun annotated() {
    let u: u8 = 0;
    let b: vector<u8> = b"hello";
    let a: address = @0x0;
    let (x, y): (&u64, &mut u64) = (&0, &mut 1);
    let S { f, g: f2 }: S = S { f: 0, g: 1 };
}
```

請注意，型別標註必須永遠放在模式的右側：

```move
// highlight-error-start
// 錯誤！應為 let (x, y): (&u64, &mut u64) = ...
let (x: &u64, y: &mut u64) = (&0, &mut 1);
// highlight-error-end
```

### 需要標註型別時 (When annotations are necessary) {#when-annotations-are-necessary}

在某些情況下，如果型別系統無法推斷型別，就需要局部型別標註。這種情況常發生在無法推斷泛型型別的型別引數時。例如：

```move
// highlight-error-start
let _v1 = vector[]; // ERROR!
//        ^^^^^^^^ 無法推斷此型別。請嘗試新增型別註解
// highlight-error-end
let v2: vector<u64> = vector[]; // no error
```

在較罕見的情況下，型別系統可能無法為發散程式碼（divergent code，指後續所有程式碼都無法到達）推斷出型別。[`return`](./functions#return-expression) 和 [`abort`](./abort-and-assert) 都是運算式，可以是任意型別。[`loop`](./control-flow/loops) 如果有 `break`，其型別為 `()`（若有 `break e` 且 `e: T`，則型別為 `T`），但如果 `loop` 中沒有 `break`，它可以是任意型別。如果無法推斷這些型別，就需要型別標註。例如，以下程式碼：

```move
let a: u8 = return ();
let b: bool = abort 0;
let c: signer = loop ();

// highlight-error-start
let x = return (); // ERROR!
//  ^ 無法推斷此型別。請嘗試新增型別註解
let y = abort 0; // ERROR!
//  ^ 無法推斷此型別。請嘗試新增型別註解
let z = loop (); // ERROR!
//  ^ 無法推斷此型別。請嘗試新增型別註解
// highlight-error-end
```

為這段程式碼加上型別標註後，會暴露出其他關於死程式碼（dead code）或未使用區域變數的錯誤，但這個範例仍有助於理解這個問題。

### 多重宣告與 tuple (Multiple declarations with tuples) {#multiple-declarations-with-tuples}

`let` 可以用 tuple 一次引入多個區域變數。括號內宣告的區域變數會依序初始化為 tuple 中對應的值。

```move
let () = ();
let (x0, x1) = (0, 1);
let (y0, y1, y2) = (0, 1, 2);
let (z0, z1, z2, z3) = (0, 1, 2, 3);
```

表達式的型別必須與 tuple 樣式的元數（arity）完全相符。

```move
// highlight-error
let (x, y) = (0, 1, 2); // ERROR!
// highlight-error
let (x, y, z, q) = (0, 1, 2); // ERROR!
```

在同一個 `let` 中不能宣告兩個同名的區域變數。

```move
// highlight-error
let (x, x) = 0; // ERROR!
```

宣告的區域變數之可變性可以混合使用。

```move
let (mut x, y) = (0, 1);
x = 1;
```

### 具有結構體的多重宣告 (Multiple declarations with structs) {#multiple-declarations-with-structs}

當解構(或匹配)一個結構體時，`let` 也可以同時引入多個區域變數。在這種形式中，`let` 會建立一組區域變數，並初始化為結構體欄位的值。語法看起來像這樣：

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

具位置的結構體也類似

```move
public struct P(u64, u64)
```

以及

```move
let P (local1, local2) = P ( 1, 2 );
// local1: u64
// local2: u64
```

以下是一個更複雜的範例：

```move
module 0::example;

public struct X(u64)
public struct Y { x1: X, x2: X }

fun new_x(): X {
    X(1)
}

fun example() {
    let Y { x1: X(f), x2 } = Y { x1: new_x(), x2: new_x() };
    assert!(f + x2.0 == 2, 42);

    let Y { x1: X(f1), x2: X(f2) } = Y { x1: new_x(), x2: new_x() };
    assert!(f1 + f2 == 2, 42);

    // `struct X` 沒有 `drop` 能力，需要手動銷毀
    let X(_) = x2;
}
```

結構體的欄位可以身兼二職，同時識別要綁定的欄位*以及*變數的名稱。這有時被稱為雙關(punning)。

```move
let Y { x1, x2 } = e;
```

等同於：

```move
let Y { x1: x1, x2: x2 } = e;
```

如同 tuple 所示，你不能在單一 `let` 中宣告多個同名的區域變數。

```move
// highlight-error
let Y { x1: x, x2: x } = e; // ERROR!
```

同樣地，如同 tuple，所宣告區域變數的可變性可以混合使用。

```move
let Y { x1: mut x1, x2 } = e;
```

此外，可變性標註也可以套用在雙關的欄位上。給出等價的範例

```move
let Y { mut x1, x2 } = e;
```

### 對引用進行解構 (Destructuring against references) {#destructuring-against-references}

在上面針對 struct 的範例中，`let` 中被綁定的值被移動了，銷毀了 struct 值並綁定其欄位。

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

在這個情境中，struct 值 `T { f1: 1, f2: 2 }` 在 `let` 之後就不再存在了。

如果你希望不移動並銷毀 struct 值，你可以借用它的每個欄位。例如：

```move
let t = T { f1: 1, f2: 2 };
let T { f1: local1, f2: local2 } = &t;
// local1: &u64
// local2: &u64
```

可變參照也有類似的行為：

```move
let mut t = T { f1: 1, f2: 2 };
let T { f1: local1, f2: local2 } = &mut t;
// local1: &mut u64
// local2: &mut u64
```

這種行為也適用於巢狀 struct。

```move
module 0::example;

public struct X(u64)
public struct Y { x1: X, x2: X }

fun new_x(): X {
    X(1)
}

fun example() {
    let mut y = Y { x1: new_x(), x2: new_x() };

    let Y { x1: X(f), x2 } = &y;
    assert!(*f + x2.0 == 2, 42);

    let Y { x1: X(f1), x2: X(f2) } = &mut y;
    *f1 = *f1 + 1;
    *f2 = *f2 + 1;
    assert!(*f1 + *f2 == 4, 42);

    // `struct X and struct Y` 沒有 `drop` 能力，需要手動銷毀
    let Y { x1: X(_), x2: X(_) } = y;
}
```

### 忽略值 (Ignoring Values) {#ignoring-values}

在 `let` 綁定中，忽略某些值通常很有幫助。以 `_` 開頭的區域變數會被忽略，不會引入新的變數

```move
fun three(): (u64, u64, u64) {
    (0, 1, 2)
}
```

```move
let (x1, _, z1) = three();
let (x2, _y, z2) = three();
assert!(x1 + z1 == x2 + z2, 42);
```

這在某些時候是必要的，因為編譯器會對未使用的區域變數發出警告

```move
let (x1, y, z1) = three(); // 警告！
//       ^ 未使用的區域變數 'y'
```

### `let` 陳述式的一般文法 (General `let` grammar) {#general-let-grammar}

`let` 裡的各種結構都可以組合使用！這樣我們就得到 `let` 陳述式的一般文法：

> _let-binding_ → **let** _pattern-or-list_ _type-annotation_<sub>_opt_</sub> >
> _initializer_<sub>_opt_</sub> > _pattern-or-list_ → _pattern_ | **(** _pattern-list_ **)** >
> _pattern-list_ → _pattern_ **,**<sub>_opt_</sub> | _pattern_ **,** _pattern-list_ >
> _type-annotation_ → **:** _type_ _initializer_ → **=** _expression_

引入綁定的項目的一般術語是_pattern_（模式）。模式的作用是既可以（可能遞迴地）解構資料，又可以引入綁定。模式的文法如下：

> _pattern_ -> _local-variable_ | _struct-type_ **\{** _field-binding-list_ **\}** >
> _field-binding-list_ → _field-binding_ **,**<sub>_opt_</sub> | _field-binding_ **,** >
> _field-binding-list_ > _field-binding_ → _field_ | _field_ **:** _pattern_

套用此文法的幾個具體範例：

```move
    let (x, y): (u64, u64) = (0, 1);
//       ^                           區域變數
//       ^                           模式
//          ^                        區域變數
//          ^                        模式
//          ^                        模式清單
//       ^^^^                        模式清單
//      ^^^^^^                       模式或清單
//            ^^^^^^^^^^^^           型別註記
//                         ^^^^^^^^  初始化式
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let 綁定

    let Foo { f, g: x } = Foo { f: 0, g: 1 };
//      ^^^                                    struct 型別
//            ^                                欄位
//            ^                                欄位綁定
//               ^                                欄位
//                  ^                          區域變數
//                  ^                          模式
//               ^^^^                          欄位綁定
//            ^^^^^^^                          欄位綁定清單
//      ^^^^^^^^^^^^^^^                        模式
//      ^^^^^^^^^^^^^^^                        模式或清單
//                      ^^^^^^^^^^^^^^^^^^^^   初始化式
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let 綁定
```

## Mutations（賦值） (Mutations) {#mutations}

### 賦值 (Assignments) {#assignments}

在區域變數被引入之後（透過 `let` 或作為函式參數），可變的（`mut`）區域變數可以透過賦值來修改：

```move
x = e
```

與 `let` 綁定不同，賦值是運算式。在某些語言中，賦值會回傳被賦予的值，但在 Move 中，任何賦值的型別永遠是 `()`。

```move
(x = e: ())
```

實務上，賦值作為運算式意味著它們可以在不需要用大括號（`{`...`}`）新增運算式區塊的情況下使用。

```move
let x;
if (cond) x = 1 else x = 2;
```

賦值使用與 `let` 綁定相似的模式語法，但不含 `mut`：

```move
module 0::example;

public struct X { f: u64 }

fun new_x(): X {
    X { f: 1 }
}

// 注意：此範例會針對未使用的變數和賦值出現提示。
fun example() {
    let (mut x, mut y, mut f, mut g) = (0, 0, 0, 0);

    (X { f }, X { f: x }) = (new_x(), new_x());
    assert!(f + x == 2, 42);

    (x, y, f, _, g) = (0, 0, 0, 0, 0);
}
```

請注意，一個區域變數只能有一種型別，因此該區域變數的型別在多次賦值之間不能改變。

```move
let mut x;
x = 0;
// highlight-error
x = false; // ERROR!
```

### 透過參考修改 (Mutating through a reference) {#mutating-through-a-reference}

除了直接透過賦值修改區域變數外，可變的（`mut`）區域變數也可以透過可變參考 `&mut` 來修改。

```move
let mut x = 0;
let r = &mut x;
*r = 1;
assert!(x == 1, 42);
```

這在以下情況特別有用：

(1) 你想根據某個條件修改不同的變數。

```move
let mut x = 0;
let mut y = 1;
let r = if (cond) &mut x else &mut y;
*r = *r + 1;
```

(2) 你想讓另一個函式修改你的區域變數值。

```move
let mut x = 0;
modify_ref(&mut x);
```

這種修改方式正是你修改結構體與向量的方法！

```move
let mut v = vector[];
vector::push_back(&mut v, 100);
assert!(*vector::borrow(&v, 0) == 100, 42);
```

更多細節請參見 [Move 參考](./primitive-types/references)。

## Scopes 作用域 (Scopes) {#scopes}

任何用 `let` 宣告的區域變數，在_該作用域內_都可以在後續的表達式中使用。
作用域由表達式區塊 `{`...`}` 宣告。

區域變數無法在宣告的作用域之外使用。

```move
let x = 0;
{
    let y = 1;
};
// highlight-error-start
x + y // ERROR!
//  ^ 未綁定的區域變數 'y'
// highlight-error-end
```

但是，外層作用域的區域變數_可以_在巢狀作用域中使用。

```move
{
    let x = 0;
    {
        let y = x + 1; // valid
    }
}
```

區域變數可以在任何能存取到它的作用域中被修改。這個修改會跟著該區域變數留存下來，不論是哪個作用域執行了這次修改。

```move
let mut x = 0;
x = x + 1;
assert!(x == 1, 42);
{
    x = x + 1;
    assert!(x == 2, 42);
};
assert!(x == 2, 42);
```

### 表達式區塊 (Expression Blocks) {#expression-blocks}

表達式區塊是一連串以分號（`;`）分隔的敘述。表達式區塊的結果值就是區塊中最後一個表達式的值。

```move
{ let x = 1; let y = 1; x + y }
```

在這個範例中，區塊的結果是 `x + y`。

一個敘述可以是 `let` 宣告，也可以是一個表達式。記住，賦值（`x = e`）是型別為 `()` 的表達式。

```move
{ let x; let y = 1; x = 1; x + y }
```

函式呼叫是另一種常見的型別為 `()` 的表達式。會修改資料的函式呼叫通常被當作敘述使用。

```move
{ let v = vector[]; vector::push_back(&mut v, 1); v }
```

這不僅限於 `()` 型別——任何表達式都可以在一連串敘述中被當作敘述使用！

```move
{
    let x = 0;
    x + 1; // value is discarded
    x + 2; // value is discarded
    b"hello"; // value is discarded
}
```

但是！如果表達式包含一個資源（不具備 `drop` [能力](./abilities) 的值），你會得到一個錯誤。這是因為 Move 的型別系統保證任何被丟棄的值都具備 `drop` [能力](./abilities)。（所有權必須被轉移，或者該值必須在其宣告模組內被明確銷毀。）

```move
{
    let x = 0;
// highlight-error-start
    Coin { value: x }; // ERROR!
//  ^^^^^^^^^^^^^^^^^ 沒有 `drop` 能力的值未被使用
// highlight-error-end
    x
}
```

如果區塊中沒有最後一個表達式——也就是說，如果結尾有一個尾隨分號 `;`，就會有一個隱含的 [unit `()` 值](https://en.wikipedia.org/wiki/Unit_type)。同樣地，如果表達式區塊是空的，也會有一個隱含的 unit `()` 值。

兩者是等價的

```move
{ x = x + 1; 1 / x; }
```

```move
{ x = x + 1; 1 / x; () }
```

同樣地，以下兩者也是等價的

```move
{ }
```

```move
{ () }
```

表達式區塊本身就是一個表達式，可以用在任何使用表達式的地方。（注意：函式的主體也是一個表達式區塊，但函式主體不能被替換成另一個表達式。）

```move
let my_vector: vector<vector<u8>> = {
    let mut v = vector[];
    vector::push_back(&mut v, b"hello");
    vector::push_back(&mut v, b"goodbye");
    v
};
```

（在這個範例中並不需要型別標注，加上它只是為了清楚起見。）

### 遮蔽 (Shadowing) {#shadowing}

如果一個 `let` 引入的區域變數名稱已經存在於作用域中，那個先前的變數在該作用域的其餘部分將無法再被存取。這稱為_遮蔽 (shadowing)_。

```move
let x = 0;
assert!(x == 0, 42);

let x = 1; // x is shadowed
assert!(x == 1, 42);
```

當一個區域變數被遮蔽時，它不需要保留與之前相同的型別。

```move
let x = 0;
assert!(x == 0, 42);

let x = b"hello"; // x is shadowed
assert!(x == b"hello", 42);
```

當一個區域變數被遮蔽後，儲存在該區域變數中的值仍然存在，但將無法再被存取。對於不具備 [`drop` 能力](./abilities) 的型別值來說，這點需要特別留意，因為該值的所有權必須在函式結束前被轉移。

```move
module 0::example;

public struct Coin has store { value: u64 }

fun unused_coin(): Coin {
// highlight-error-start
    let x = Coin { value: 0 }; // ERROR!
//      ^ 這個區域變數仍持有一個沒有 `drop` 能力的值
    x.value = 1;
    let x = Coin { value: 10 };
    x
//  ^ 無效的回傳
// highlight-error-end
}
```

當一個區域變數在某個作用域內被遮蔽時，這個遮蔽只在該作用域內有效。一旦該作用域結束，遮蔽就會消失。

```move
let x = 0;
{
    let x = 1;
    assert!(x == 1, 42);
};
assert!(x == 0, 42);
```

記住，區域變數在被遮蔽時可以改變型別。

```move
let x = 0;
{
    let x = b"hello";
    assert!(x == b"hello", 42);
};
assert!(x == 0, 42);
```

## 移動與複製 (Move and Copy) {#move-and-copy}

Move 中所有的區域變數都可以用兩種方式使用：`move` 或 `copy`。如果沒有指定其中一種，Move 編譯器能夠推斷應該使用 `copy` 還是 `move`。這代表在上述所有範例中，編譯器都會自動插入 `move` 或 `copy`。區域變數如果不使用 `move` 或 `copy` 就無法被使用。

`copy` 對於來自其他程式語言的開發者來說可能感覺最熟悉，因為它會在該運算式中建立變數內值的新副本來使用。使用 `copy`，區域變數可以被使用超過一次。

```move
let x = 0;
let y = copy x + 1;
let z = copy x + 2;
```

任何具有 `copy` [能力 (ability)](./abilities) 的值都可以用這種方式複製，且除非指定了 `move`，否則會隱式地被複製。

`move` 會將值從區域變數中取出，*不*複製資料。在 `move` 發生後，該區域變數就無法使用，即使該值的型別具有 `copy` [能力 (ability)](./abilities)。

```move
let x = 1;
// highlight-error-start
let y = move x + 1;
//      ------ 區域變數在此處被移動
let z = move x + 2; // Error!
//      ^^^^^^ 對區域變數 'x' 的無效使用
// highlight-error-end
y + z
```

### 安全性 (Safety) {#safety}

Move 的型別系統會防止值在被移動後被使用。這與 [`let` 宣告](#let-bindings) 中描述的安全檢查相同，該檢查會防止區域變數在被賦值前被使用。

<!-- For more information, see TODO future section on ownership and move semantics. -->

### 推斷 (Inference) {#inference}

如上所述，如果沒有明確指示，Move 編譯器會推斷出 `copy` 或 `move`。其演算法相當簡單：

- 任何具有 `copy` [能力 (ability)](./abilities) 的值都會被賦予 `copy`。
- 任何參照（不論是可變的 `&mut` 還是不可變的 `&`）都會被賦予 `copy`。
  - 除非在特殊情況下，為了讓借用檢查器 (borrow checker) 的錯誤可預期而被設為 `move`。這會在該參照不再被使用後發生。
- 其他任何值都會被賦予 `move`。

給定以下結構

```move
public struct Foo has copy, drop, store { f: u64 }
public struct Coin has store { value: u64 }
```

我們有以下範例

```move
let s = b"hello";
let foo = Foo { f: 0 };
let coin = Coin { value: 0 };
let coins = vector[Coin { value: 0 }, Coin { value: 0 }];

let s2 = s; // copy
let foo2 = foo; // copy
let coin2 = coin; // move
let coins2 = coins; // move

let x = 0;
let b = false;
let addr = @0x42;
let x_ref = &x;
let coin_ref = &mut coin2;

let x2 = x; // copy
let b2 = b; // copy
let addr2 = @0x42; // copy
let x_ref2 = x_ref; // copy
let coin_ref2 = coin_ref; // copy
```
