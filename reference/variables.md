---
title: 區域變數與作用域 (Local Variables and Scope) | 參考手冊
description:
  Move 區域變數與作用域 (Move Local Variables and Scope)：let 綁定、可變性、型別標註、遮蔽 (shadowing)
  與 move 語義參考手冊
---

# 區域變數與作用域 (Local Variables and Scope) {#local-variables-and-scope}

Move 中的區域變數是按詞法（靜態）定義作用域的。新變數透過關鍵字 `let` 引入，這會遮蔽（shadow）任何同名的先前區域變數。標記為 `mut` 的區域變數是可變的，既可以直接更新，也可以透過可變參考進行更新。

## 宣告區域變數 (Declaring Local Variables) {#declaring-local-variables}

### `let` 綁定 (`let` bindings) {#let-bindings}

Move 程式使用 `let` 將變數名稱綁定到值：

```move
let x = 1;
let y = x + x;
```

`let` 也可以在不將值綁定到區域變數的情況下使用。

```move
let x;
```

隨後可以為該區域變數分配一個值。

```move
let x;
if (cond) {
  x = 1
} else {
  x = 0
}
```

當嘗試在無法提供預設值的情況下從迴圈中提取值時，這非常有用。

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

要在賦值 _之後_ 修改區域變數，或以可變方式借用它（`&mut`），必須將其宣告為 `mut`。

```move
let mut x = 0;
if (cond) x = x + 1;
foo(&mut x);
```

欲了解更多詳情，請參閱下文的[賦值](#assignments)部分。

### 變數在使用前必須先賦值 (Variables must be assigned before use) {#variables-must-be-assigned-before-use}

Move 的型別系統可確保區域變數在賦值之前不會被使用。

```move
let x;
// highlight-error
x + x // 錯誤！x 在賦值前被使用
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

### 有效的變數名稱 (Valid variable names) {#valid-variable-names}

變數名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z` 以及數字 `0` 到 `9`。變數名稱必須以底線 `_` 或字母 `a` 到 `z` 開頭。它們 _不能_ 以大寫字母開頭。

```move
// 全部有效
let x = e;
let _x = e;
let _A = e;
let x0 = e;
let xA = e;
let foobar_123 = e;

// 全部無效
// highlight-error-start
let X = e; // 錯誤！
let Foo = e; // 錯誤！
// highlight-error-end
```

### 型別標註 (Type annotations) {#type-annotations}

區域變數的型別幾乎總能由 Move 的型別系統推論出來。然而，Move 允許顯式的型別標註，這有助於提高可讀性、清晰度或除錯。新增型別標註的語法為：

```move
let x: T = e; // 「型別為 T 的變數 x 被初始化為運算式 e」
```

顯式型別標註的一些範例：

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

請注意，型別標註必須始終位於模式的右側：

```move
// highlight-error-start
// 錯誤！應為 let (x, y): (&u64, &mut u64) = ...
let (x: &u64, y: &mut u64) = (&0, &mut 1);
// highlight-error-end
```

### 何時需要標註 (When annotations are necessary) {#when-annotations-are-necessary}

在某些情況下，如果型別系統無法推論型別，則需要局部型別標註。這常見於無法推論泛型型別的型別參數時。例如：

```move
// highlight-error-start
let _v1 = vector[]; // 錯誤！
//        ^^^^^^^^ 無法推論此型別。請嘗試新增標註
// highlight-error-end
let v2: vector<u64> = vector[]; // 無錯誤
```

在極少數情況下，型別系統可能無法為發散（divergent）程式碼（後續程式碼均無法到達的情況）推論型別。[`return`](./functions#return-expression) 和 [`abort`](./abort-and-assert) 都是運算式，可以具有任何型別。[`loop`](./control-flow/loops) 如果有 `break` 則具有型別 `()`（如果有 `break e` 且 `e: T` 則具有型別 `T`），但如果沒有跳出 `loop` 的 break，則它可能具有任何型別。如果無法推論這些型別，則需要提供型別標註。例如，以下程式碼：

```move
let a: u8 = return ();
let b: bool = abort 0;
let c: signer = loop ();

// highlight-error-start
let x = return (); // 錯誤！
//  ^ 無法推論此型別。請嘗試新增標註
let y = abort 0; // 錯誤！
//  ^ 無法推論此型別。請嘗試新增標註
let z = loop (); // 錯誤！
//  ^ 無法推論此型別。請嘗試新增標註
// highlight-error-end
```

為這些程式碼新增型別標註會暴露有關無作用程式碼 (dead code) 或未使用區域變數的其他錯誤，但該範例對於理解此問題仍然很有幫助。

### 透過元組進行多重宣告 (Multiple declarations with tuples) {#multiple-declarations-with-tuples}

`let` 可以使用元組一次性引入多個區域變數。圓括號內宣告的區域變數會被初始化為元組中對應的值。

```move
let () = ();
let (x0, x1) = (0, 1);
let (y0, y1, y2) = (0, 1, 2);
let (z0, z1, z2, z3) = (0, 1, 2, 3);
```

運算式的型別必須與元組模式的基數（arity）完全匹配。

```move
// highlight-error
let (x, y) = (0, 1, 2); // 錯誤！
// highlight-error
let (x, y, z, q) = (0, 1, 2); // 錯誤！
```

不能在單個 `let` 中宣告多個同名的區域變數。

```move
// highlight-error
let (x, x) = 0; // 錯誤！
```

宣告的區域變數的可變性可以混用。

```move
let (mut x, y) = (0, 1);
x = 1;
```

### 透過結構體進行多重宣告 (Multiple declarations with structs) {#multiple-declarations-with-structs}

在對結構體進行解構（或與之匹配）時，`let` 也可以一次性引入多個區域變數。在這種形式中，`let` 建立一組區域變數，並依照結構體中欄位的值進行初始化。語法如下：

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

對於位置結構體（positional structs）也是如此：

```move
public struct P(u64, u64)
```

以及：

```move
let P (local1, local2) = P ( 1, 2 );
// local1: u64
// local2: u64
```

這是一個更複雜的範例：

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

結構體的欄位可以兼任兩職：標識要綁定的欄位 _以及_ 變數名稱。這有時被稱為「雙關（punning）」。

```move
let Y { x1, x2 } = e;
```

等同於：

```move
let Y { x1: x1, x2: x2 } = e;
```

如元組所示，不能在單個 `let` 中宣告多個同名的區域變數。

```move
// highlight-error
let Y { x1: x, x2: x } = e; // 錯誤！
```

與元組一樣，宣告的區域變數的可變性可以混用。

```move
let Y { x1: mut x1, x2 } = e;
```

此外，可變性標註也可以應用於雙關欄位。給出等效的範例：

```move
let Y { mut x1, x2 } = e;
```

### 對參考進行解構 (Destructuring against references) {#destructuring-against-references}

在上述結構體的範例中，`let` 中綁定的值被移動，銷毀了結構體值並綁定了其欄位。

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

在這種情況下，結構體值 `T { f1: 1, f2: 2 }` 在 `let` 之後不再存在。

如果你希望不移動且不銷毀結構體值，則可以借用其每個欄位。例如：

```move
let t = T { f1: 1, f2: 2 };
let T { f1: local1, f2: local2 } = &t;
// local1: &u64
// local2: &u64
```

對於可變參考也是如此：

```move
let mut t = T { f1: 1, f2: 2 };
let T { f1: local1, f2: local2 } = &mut t;
// local1: &mut u64
// local2: &mut u64
```

此行為也適用於巢狀結構體。

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

    // `struct X 和 struct Y` 沒有 `drop` 能力，需要手動銷毀
    let Y { x1: X(_), x2: X(_) } = y;
}
```

### 忽略值 (Ignoring Values) {#ignoring-values}

在 `let` 綁定中，忽略某些值通常很有幫助。以 `_` 開頭的區域變數將被忽略，且不會引入新變數。

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

有時這是必要的，因為編譯器會針對未使用的區域變數發出警告。

```move
let (x1, y, z1) = three(); // 警告！
//       ^ 未使用的區域變數 'y'
```

### 通用的 `let` 語法 (General `let` grammar) {#general-let-grammar}

`let` 中的所有不同結構都可以組合使用！因此，我們可以得出 `let` 陳述式的通用語法：

> _let-binding_ → **let** _pattern-or-list_ _type-annotation_<sub>_opt_</sub> >
> _initializer_<sub>_opt_</sub> > _pattern-or-list_ → _pattern_ | **(** _pattern-list_ **)** >
> _pattern-list_ → _pattern_ **,**<sub>_opt_</sub> | _pattern_ **,** _pattern-list_ >
> _type-annotation_ → **:** _type_ _initializer_ → **=** _expression_

引入綁定的項目的通稱是 _模式（pattern）_。模式既用於解構資料（可能是遞迴的），也用於引入綁定。模式語法如下：

> _pattern_ -> _local-variable_ | _struct-type_ **\{** _field-binding-list_ **\}** >
> _field-binding-list_ → _field-binding_ **,**<sub>_opt_</sub> | _field-binding_ **,** >
> _field-binding-list_ > _field-binding_ → _field_ | _field_ **:** _pattern_

應用此語法的一些具體範例：

```move
    let (x, y): (u64, u64) = (0, 1);
//       ^                           區域變數
//       ^                           模式
//          ^                        區域變數
//          ^                        模式
//          ^                        模式清單
//       ^^^^                        模式清單
//      ^^^^^^                       模式或清單
//            ^^^^^^^^^^^^           型別標註
//                         ^^^^^^^^  初始化程序
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let-綁定

    let Foo { f, g: x } = Foo { f: 0, g: 1 };
//      ^^^                                    結構體型別
//            ^                                欄位
//            ^                                欄位綁定
//               ^                             欄位
//                  ^                          區域變數
//                  ^                          模式
//               ^^^^                          欄位綁定
//            ^^^^^^^                          欄位綁定清單
//      ^^^^^^^^^^^^^^^                        模式
//      ^^^^^^^^^^^^^^^                        模式或清單
//                      ^^^^^^^^^^^^^^^^^^^^   初始化程序
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let-綁定
```

## 修改 (Mutations) {#mutations}

### 賦值 (Assignments) {#assignments}

在引入區域變數後（無論是透過 `let` 還是作為函式參數），可以透過賦值修改 `mut` 區域變數：

```move
x = e
```

與 `let` 綁定不同，賦值是運算式。在某些語言中，賦值會傳回被分配的值，但在 Move 中，任何賦值的型別始終為 `()`。

```move
(x = e: ())
```

實際上，賦值作為運算式意味著可以在不使用大括號（`{`...`}`）增加新運算式區塊的情況下使用它們。

```move
let x;
if (cond) x = 1 else x = 2;
```

賦值使用與 `let` 綁定類似的模式語法方案，但缺少 `mut`：

```move
module 0::example;

public struct X { f: u64 }

fun new_x(): X {
    X { f: 1 }
}

// 注意：此範例將會針對未使用的變數和賦值發出警告。
fun example() {
    let (mut x, mut y, mut f, mut g) = (0, 0, 0, 0);

    (X { f }, X { f: x }) = (new_x(), new_x());
    assert!(f + x == 2, 42);

    (x, y, f, _, g) = (0, 0, 0, 0, 0);
}
```

請注意，區域變數只能有一種型別，因此區域變數的型別在賦值之間不能改變。

```move
let mut x;
x = 0;
// highlight-error
x = false; // 錯誤！
```

### 透過參考進行修改 (Mutating through a reference) {#mutating-through-a-reference}

除了使用賦值直接修改區域變數外，還可以透過可變參考 `&mut` 修改 `mut` 區域變數。

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

這類修改也是修改結構體和向量的方法！

```move
let mut v = vector[];
vector::push_back(&mut v, 100);
assert!(*vector::borrow(&v, 0) == 100, 42);
```

欲了解更多詳情，請參閱 [Move 參考](./primitive-types/references)。

## 作用域 (Scopes) {#scopes}

任何使用 `let` 宣告的區域變數都可以在該 _作用域（scope）_ 內的所有後續運算式中使用。作用域使用運算式區塊 `{`...`}` 宣告。

區域變數不能在宣告的作用域之外使用。

```move
let x = 0;
{
    let y = 1;
};
// highlight-error-start
x + y // 錯誤！
//  ^ 未繫結的區域變數 'y'
// highlight-error-end
```

但是，外部作用域的區域變數 _可以_ 在巢狀作用域中使用。

```move
{
    let x = 0;
    {
        let y = x + 1; // 有效
    }
}
```

區域變數可以在任何可存取的作用域中被修改。該修改將隨區域變數一起保留，無論執行修改的作用域為何。

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

### 運算式區塊 (Expression Blocks) {#expression-blocks}

運算式區塊是由分號（`;`）分隔的一系列陳述式。運算式區塊的結果值是區塊中最後一個運算式的值。

```move
{ let x = 1; let y = 1; x + y }
```

在此範例中，區塊的結果是 `x + y`。

陳述式可以是 `let` 宣告，也可以是運算式。請記住，賦值（`x = e`）是型別為 `()` 的運算式。

```move
{ let x; let y = 1; x = 1; x + y }
```

函式呼叫是另一種常見的型別為 `()` 的運算式。修改資料的函式呼叫通常用作陳述式。

```move
{ let v = vector[]; vector::push_back(&mut v, 1); v }
```

這不僅限於 `()` 型別——任何運算式都可以在序列中用作陳述式！

```move
{
    let x = 0;
    x + 1; // 值被捨棄
    x + 2; // 值被捨棄
    b"hello"; // 值被捨棄
}
```

但是！如果運算式包含資源（不具備 `drop` [能力](./abilities)的值），則會報錯。這是因為 Move 的型別系統保證任何被捨棄的值都具備 `drop` [能力](./abilities)。（所有權必須被轉移，或者該值必須在宣告它的模組內部被顯式銷毀。）

```move
{
    let x = 0;
// highlight-error-start
    Coin { value: x }; // 錯誤！
//  ^^^^^^^^^^^^^^^^^ 未使用的值，不具備 `drop` 能力
// highlight-error-end
    x
}
```

如果區塊中不存在最終運算式——即如果存在末尾分號 `;`，則存在隱式的 [單元 `()` 值](https://en.wikipedia.org/wiki/Unit_type)。同樣地，如果運算式區塊為空，則存在隱式的單元 `()` 值。

兩者是等效的

```move
{ x = x + 1; 1 / x; }
```

```move
{ x = x + 1; 1 / x; () }
```

同樣地，兩者也是等效的

```move
{ }
```

```move
{ () }
```

運算式區塊本身就是一個運算式，可以在任何使用運算式的地方使用。（注意：函式體也是一個運算式區塊，但函式體不能被另一個運算式替換。）

```move
let my_vector: vector<vector<u8>> = {
    let mut v = vector[];
    vector::push_back(&mut v, b"hello");
    vector::push_back(&mut v, b"goodbye");
    v
};
```

（在此範例中不需要型別標註，新增僅是為了清晰考量。）

### 遮蔽 (Shadowing) {#shadowing}

如果 `let` 引入了一個名稱已在作用域中的區域變數，則在該作用域的剩餘部分將無法再存取之前的變數。這被稱為 _遮蔽（shadowing）_。

```move
let x = 0;
assert!(x == 0, 42);

let x = 1; // x 被遮蔽
assert!(x == 1, 42);
```

當區域變數被遮蔽時，不需要保留與之前相同的型別。

```move
let x = 0;
assert!(x == 0, 42);

let x = b"hello"; // x 被遮蔽
assert!(x == b"hello", 42);
```

區域變數被遮蔽後，儲存在區域變數中的值仍然存在，但將不再可被存取。對於不具備 [`drop` 能力](./abilities)型別的值，必須牢記這一點，因為值的所有權必須在函式結束前轉移。

```move
module 0::example;

public struct Coin has store { value: u64 }

fun unused_coin(): Coin {
// highlight-error-start
    let x = Coin { value: 0 }; // 錯誤！
//      ^ 此區域變數仍包含一個不具備 `drop` 能力的值
    x.value = 1;
    let x = Coin { value: 10 };
    x
//  ^ 無效的傳回
// highlight-error-end
}
```

當區域變數在一個作用域內被遮蔽時，遮蔽僅對該作用域有效。一旦該作用域結束，遮蔽就會消失。

```move
let x = 0;
{
    let x = 1;
    assert!(x == 1, 42);
};
assert!(x == 0, 42);
```

請記住，當區域變數被遮蔽時，它們可以改變型別。

```move
let x = 0;
{
    let x = b"hello";
    assert!(x == b"hello", 42);
};
assert!(x == 0, 42);
```

## 移動與複製 (Move and Copy) {#move-and-copy}

Move 中的所有區域變數都可以透過兩種方式使用：`move` 或 `copy`。如果未指定其中之一，Move 編譯器能夠推論應使用 `copy` 還是 `move`。這意味著在上述所有範例中，編譯器都會插入 `move` 或 `copy`。區域變數在不使用 `move` 或 `copy` 的情況下無法使用。

對於從其他程式語言轉向 Move 的開發者來說，`copy` 可能感覺最熟悉，因為它會在運算式中使用該變數時，建立變數值的全新副本。使用 `copy` 之後，區域變數可以多次使用。

```move
let x = 0;
let y = copy x + 1;
let z = copy x + 2;
```

任何具備 `copy` [能力](./abilities)的值都可以以此方式複製，除非指定 `move`，否則將隱式複製。

`move` 將值從區域變數中取出 _而不_ 複製資料。在執行 `move` 後，即使該值的型別具備 `copy` [能力](./abilities)，該區域變數也將不再可用。

```move
let x = 1;
// highlight-error-start
let y = move x + 1;
//      ------ 區域變數在此處已移動
let z = move x + 2; // 錯誤！
//      ^^^^^^ 區域變數 'x' 的用法無效
// highlight-error-end
y + z
```

### 安全性 (Safety) {#safety}

Move 的型別系統將阻止值在被移動後再次使用。這與 [`let` 宣告](#let-bindings) 中描述的安全檢查相同，用於防止區域變數在賦值之前被使用。

<!-- 欲瞭解更多資訊，請參見 TODO 未來關於所有權和移動語義的章節。 -->

### 推論 (Inference) {#inference}

如上所述，如果未指明，Move 編譯器將推論 `copy` 或 `move`。其演算法非常簡單：

- 任何具備 `copy` [能力](./abilities)的值都被賦予 `copy`。
- 任何參考（包括可變 `&mut` 和不可變 `&`）都被賦予 `copy`。
  - 除特殊情況外，為了產生可預測的借用檢查器錯誤，參考會被設為 `move`。這發生在參考不再被使用後。
- 其他任何值都被賦予 `move`。

給定結構體：

```move
public struct Foo has copy, drop, store { f: u64 }
public struct Coin has store { value: u64 }
```

我們有以下範例：

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
