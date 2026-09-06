---
title: 區域變數 (Local Variables) 與範圍 (Scope) | 參考手冊
description: Move 區域變數與範圍：`let` 繫結、可變性、型別註解、遮蔽與移動語意參考。
keywords:
  - Move
  - Sui
  - Move reference
  - local
  - variables
  - scope
  - reference
questions:
  - How does Local Variables and Scope work in Move?
  - What is the syntax for Local Variables and Scope in Move?
  - What is Declaring Local Variables in Move?
  - What is Mutations in Move?
answer: 'Move local variables and scope: let bindings, mutability, type annotations, shadowing, and move semantics reference.'
goal:
  description: 'Reader understands move local variables and scope: let bindings, mutability, type annotations, shadowing, and move semantics reference'
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

# 區域變數與作用域 (Local Variables and Scope) {#local-variables-and-scope}

Move 中的區域變數採用詞彙（靜態）作用域。使用關鍵字 `let` 引入新變數，這會遮蔽任何同名的先前區域變數。標記為 `mut` 的區域變數可變，且可直接或透過可變參考進行更新。

## 宣告區域變數 (Declaring Local Variables) {#declaring-local-variables}

### `let` 繫結 (`let` bindings) {#let-bindings}

Move 程式使用 `let` 將變數名稱繫結至值：

```move
let x = 1;
let y = x + x;
```

`let` 也可以在不將值繫結至區域變數的情況下使用。

```move
let x;
```

之後便可以為該區域變數指派值。

```move
let x;
if (cond) {
  x = 1
} else {
  x = 0
}
```

當無法提供預設值，而需要嘗試從迴圈中擷取值時，這會非常有幫助。

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

若要在區域變數被指派*之後*修改它，或以可變方式借用它（`&mut`），則必須將其宣告為 `mut`。

```move
let mut x = 0;
if (cond) x = x + 1;
foo(&mut x);
```

如需更多詳細資訊，請參閱下方的[指派](#assignments)章節。

### 使用前必須先指派變數 (Variables must be assigned before use) {#variables-must-be-assigned-before-use}

Move 的型別系統可防止在區域變數被指派前使用它。

```move
let x;
// 突顯錯誤
x + x // 錯誤！x 在被指派前就已使用
```

```move
let x;
if (cond) x = 0;
// 突顯錯誤
x + x // 錯誤！x 並非在所有情況下都有值
```

```move
let x;
while (cond) x = 0;
// 突顯錯誤
x + x // 錯誤！x 並非在所有情況下都有值
```

### 有效的變數名稱 (Valid variable names) {#valid-variable-names}

變數名稱可包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z`，以及數字 `0`
到 `9`。變數名稱必須以底線 `_` 或字母 `a` 到 `z` 開頭。它們
_不可_ 以大寫字母開頭。

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

### 型別註解 (Type annotations) {#type-annotations}

區域變數的型別幾乎總是能由 Move 的型別系統推斷出來。不過，Move
允許明確的型別註解，這有助於提升可讀性、清晰度或可除錯性。新增型別註解的
語法如下：

```move
let x: T = e; //「型別為 T 的變數 x 會以運算式 e 初始化」
```

以下是一些明確型別註解的範例：

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

請注意，型別註解必須一律位於模式的右側：

```move
// 突顯錯誤開始
// 錯誤！應為 let (x, y): (&u64, &mut u64) = ...
let (x: &u64, y: &mut u64) = (&0, &mut 1);
// 突顯錯誤結束
```

### 何時需要型別註解 (When annotations are necessary) {#when-annotations-are-necessary}

在某些情況下，如果型別系統無法推斷型別，就必須使用區域型別註解。這種情況常見於無法推斷泛型型別的型別引數時。例如：

```move
// highlight-error-start
let _v1 = vector[]; // 錯誤！
//        ^^^^^^^^ 無法推斷此型別。請嘗試加入註解
// highlight-error-end
let v2: vector<u64> = vector[]; // 沒有錯誤
```

在較罕見的情況下，型別系統可能無法推斷發散程式碼的型別（亦即後續所有程式碼皆無法觸及）。[`return`](./functions#return-expression) 與 [`abort`](./abort-and-assert) 都是運算式，且可以具有任何型別。若 [`loop`](./control-flow/loops) 含有 `break`，其型別為 `()`（若含有 `break e` 且 `e: T`，則型別為 `T`）；但如果沒有跳出 `loop` 的 break，它可以具有任何型別。若無法推斷這些型別，就必須使用型別註解。例如，下列程式碼：

```move
let a: u8 = return ();
let b: bool = abort 0;
let c: signer = loop ();

// highlight-error-start
let x = return (); // 錯誤！
//  ^ 無法推斷此型別。請嘗試加入註解
let y = abort 0; // 錯誤！
//  ^ 無法推斷此型別。請嘗試加入註解
let z = loop (); // 錯誤！
//  ^ 無法推斷此型別。請嘗試加入註解
// highlight-error-end
```

為這段程式碼加入型別註解後，會顯示其他關於無效程式碼或未使用區域變數的錯誤；但這個範例仍有助於理解此問題。

### 使用元組的多重宣告 (Multiple declarations with tuples) {#multiple-declarations-with-tuples}

`let` 可以使用元組一次引入多個區域變數。在括號內宣告的區域變數會以元組中對應的值初始化。

```move
let () = ();
let (x0, x1) = (0, 1);
let (y0, y1, y2) = (0, 1, 2);
let (z0, z1, z2, z3) = (0, 1, 2, 3);
```

運算式的型別必須與元組模式的元素數量完全相符。

```move
// 突顯錯誤
let (x, y) = (0, 1, 2); // 錯誤！
// 突顯錯誤
let (x, y, z, q) = (0, 1, 2); // 錯誤！
```

你無法在單一 `let` 中宣告多個名稱相同的區域變數。

```move
// 突顯錯誤
let (x, x) = 0; // 錯誤！
```

已宣告區域變數的可變性可以混用。

```move
let (mut x, y) = (0, 1);
x = 1;
```

### 使用結構的多重宣告 (Multiple declarations with structs) {#multiple-declarations-with-structs}

在解構（或比對）結構時，`let` 也可以一次引入多個區域變數。以這種形式，`let` 會建立一組區域變數，並以結構欄位的值將其初始化。語法如下：

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

位置結構也是同樣的情況：

```move
public struct P(u64, u64)
```

以及：

```move
let P (local1, local2) = P ( 1, 2 );
// local1: u64
// local2: u64
```

以下是一個較複雜的範例：

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

    // 沒有 `drop` ability 的 `struct X`，需要手動銷毀
    let X(_) = x2;
}
```

結構的欄位可以一體兩用：識別要繫結的欄位 _以及_ 變數名稱。這有時稱為雙關（punning）。

```move
let Y { x1, x2 } = e;
```

等同於：

```move
let Y { x1: x1, x2: x2 } = e;
```

如同元組所示，你無法在單一 `let` 中宣告多個同名區域變數。

```move
// highlight-error
let Y { x1: x, x2: x } = e; // 錯誤！
```

而且如同元組，所宣告區域變數的可變性可以混用。

```move
let Y { x1: mut x1, x2 } = e;
```

此外，可變性標註可以套用至雙關欄位。因此可得到等價的範例：

```move
let Y { mut x1, x2 } = e;
```

### 對參考進行解構 (Destructuring against references) {#destructuring-against-references}

在上述的結構體範例中，`let` 中繫結的值會被移動，因而銷毀結構體值並繫結其欄位。

```move
public struct T { f1: u64, f2: u64 }
```

```move
let T { f1: local1, f2: local2 } = T { f1: 1, f2: 2 };
// local1: u64
// local2: u64
```

在此情境中，結構體值 `T { f1: 1, f2: 2 }` 在 `let` 之後便不再存在。

如果你希望不移動及銷毀結構體值，則可以借用它的每個欄位。例如：

```move
let t = T { f1: 1, f2: 2 };
let T { f1: local1, f2: local2 } = &t;
// local1: &u64
// local2: &u64
```

可變參考也是同樣的情況：

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

    // 不具備 `drop` 能力的 `struct X and struct Y`，需要手動銷毀
    let Y { x1: X(_), x2: X(_) } = y;
}
```

### 忽略值 (Ignoring Values) {#ignoring-values}

在 `let` 綁定中，忽略某些值通常很有幫助。名稱以 `_` 開頭的區域變數
會被忽略，且不會引入新的變數。

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

這有時是必要的，因為編譯器會對未使用的區域變數發出警告。

```move
let (x1, y, z1) = three(); // 警告！
//       ^ 未使用的區域變數 'y'
```

### 通用 `let` 文法 (General `let` grammar) {#general-let-grammar}

`let` 中所有不同的結構都可以組合！如此一來，我們便得到 `let` 陳述式的一般
文法：

> _let 繫結_ → **let** _模式或清單_ _型別註記_<sub>_可選_</sub> >
> _初始值設定_<sub>_可選_</sub> > _模式或清單_ → _模式_ | **(** _模式清單_ **)** >
> _模式清單_ → _模式_ **,**<sub>_可選_</sub> | _模式_ **,** _模式清單_ >
> _型別註記_ → **:** _型別_ _初始值設定_ → **=** _運算式_

用來引入繫結項目的通用術語是 _模式_。模式可同時用於
解構資料（可能以遞迴方式）以及引入繫結。模式文法如下：

> _模式_ -> _區域變數_ | _結構體型別_ **\{** _欄位繫結清單_ **\}** >
> _欄位繫結清單_ → _欄位繫結_ **,**<sub>_可選_</sub> | _欄位繫結_ **,** >
> _欄位繫結清單_ > _欄位繫結_ → _欄位_ | _欄位_ **:** _模式_

以下是套用此文法的幾個具體範例：

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
//                         ^^^^^^^^  初始值設定
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let 繫結

    let Foo { f, g: x } = Foo { f: 0, g: 1 };
//      ^^^                                    結構體型別
//            ^                                欄位
//            ^                                欄位繫結
//               ^                             欄位
//                  ^                          區域變數
//                  ^                          模式
//               ^^^^                          欄位繫結
//            ^^^^^^^                          欄位繫結清單
//      ^^^^^^^^^^^^^^^                        模式
//      ^^^^^^^^^^^^^^^                        模式或清單
//                      ^^^^^^^^^^^^^^^^^^^^   初始值設定
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ let 繫結
```

## 變更 (Mutations) {#mutations}

### 指派 (Assignments) {#assignments}

在引入區域變數後（透過 `let` 或作為函式參數），可以透過指派來修改 `mut` 區域變數：

```move
x = e
```

與 `let` 綁定不同，指派是運算式。在某些語言中，指派會回傳被指派的值，但在 Move 中，任何指派的型別一律為 `()`。

```move
(x = e: ())
```

實務上，指派為運算式表示可以直接使用它們，而不必新增含有大括號（`{`...`}`）的運算式區塊。

```move
let x;
if (cond) x = 1 else x = 2;
```

指派採用與 `let` 綁定相似的模式語法配置，但不使用 `mut`：

```move
module 0::example;

public struct X { f: u64 }

fun new_x(): X {
    X { f: 1 }
}

// 注意：此範例會針對未使用的變數和指派提出警告。
fun example() {
    let (mut x, mut y, mut f, mut g) = (0, 0, 0, 0);

    (X { f }, X { f: x }) = (new_x(), new_x());
    assert!(f + x == 2, 42);

    (x, y, f, _, g) = (0, 0, 0, 0, 0);
}
```

請注意，區域變數只能有一種型別，因此區域變數的型別不能在指派之間變更。

```move
let mut x;
x = 0;
// 突顯錯誤
x = false; // 錯誤！
```

### 透過參考修改 (Mutating through a reference) {#mutating-through-a-reference}

除了直接透過指派修改區域變數外，也可以透過可變參考 `&mut` 修改 `mut` 區域變數。

```move
let mut x = 0;
let r = &mut x;
*r = 1;
assert!(x == 1, 42);
```

在以下任一情況中，這特別實用：

(1) 你想根據某些條件修改不同的變數。

```move
let mut x = 0;
let mut y = 1;
let r = if (cond) &mut x else &mut y;
*r = *r + 1;
```

(2) 你想讓另一個函式修改你的區域值。

```move
let mut x = 0;
modify_ref(&mut x);
```

這類修改方式就是你修改結構與向量的方法！

```move
let mut v = vector[];
vector::push_back(&mut v, 100);
assert!(*vector::borrow(&v, 0) == 100, 42);
```

如需更多詳細資料，請參閱 [Move 參考](./primitive-types/references)。

## 作用域 (Scopes) {#scopes}

任何以 `let` 宣告的區域變數，都可供該作用域內後續的任何運算式使用，_僅限於該作用域內_。
作用域是以運算式區塊 `{`...`}` 宣告。

區域變數無法在已宣告的作用域之外使用。

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

但是，外層作用域中的區域變數*可以*在巢狀作用域中使用。

```move
{
    let x = 0;
    {
        let y = x + 1; // 有效
    }
}
```

區域變數可在任何能夠存取它們的作用域中被修改。該修改會隨著區域變數保留，
不論是由哪個作用域執行修改。

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

運算式區塊是一系列以分號（`;`）分隔的陳述式。運算式區塊的結果值是區塊中最後一個運算式的值。

```move
{ let x = 1; let y = 1; x + y }
```

在此範例中，區塊的結果為 `x + y`。

陳述式可以是 `let` 宣告或運算式。請記住，指派（`x = e`）是型別為 `()` 的運算式。

```move
{ let x; let y = 1; x = 1; x + y }
```

函式呼叫也是另一種常見的型別 `()` 運算式。修改資料的函式呼叫通常會作為陳述式使用。

```move
{ let v = vector[]; vector::push_back(&mut v, 1); v }
```

這不僅限於 `()` 型別---任何運算式都可以作為序列中的陳述式使用！

```move
{
    let x = 0;
    x + 1; // 值會被捨棄
    x + 2; // 值會被捨棄
    b"hello"; // 值會被捨棄
}
```

但是！如果運算式包含資源（沒有 `drop` [能力](./abilities)的值），你會收到錯誤。這是因為 Move 的型別系統保證，任何被捨棄的值都具有 `drop` [能力](./abilities)。（所有權必須被轉移，或該值必須在其宣告模組內明確銷毀。）

```move
{
    let x = 0;
// highlight-error-start
    Coin { value: x }; // 錯誤！
//  ^^^^^^^^^^^^^^^^^ 未使用且沒有 `drop` 能力的值
// highlight-error-end
    x
}
```

若區塊中沒有最後一個運算式---也就是存在結尾分號 `;`，則會有隱含的 [單位 `()` 值](https://en.wikipedia.org/wiki/Unit_type)。同樣地，若運算式區塊為空，則會有隱含的單位 `()` 值。

兩者等價

```move
{ x = x + 1; 1 / x; }
```

```move
{ x = x + 1; 1 / x; () }
```

同樣地，兩者等價

```move
{ }
```

```move
{ () }
```

運算式區塊本身也是運算式，可在任何可使用運算式的位置使用。（注意：函式主體也是運算式區塊，但函式主體不能替換為另一個運算式。）

```move
let my_vector: vector<vector<u8>> = {
    let mut v = vector[];
    vector::push_back(&mut v, b"hello");
    vector::push_back(&mut v, b"goodbye");
    v
};
```

（此範例不需要型別註記，僅為清楚起見而加入。）

### 遮蔽 (Shadowing) {#shadowing}

如果 `let` 引入的區域變數名稱已在目前範圍內，則在此範圍的其餘部分將無法再存取先前的變數。這稱為*遮蔽*。

```move
let x = 0;
assert!(x == 0, 42);

let x = 1; // x 已被遮蔽
assert!(x == 1, 42);
```

區域變數遭到遮蔽時，不需要保留與先前相同的型別。

```move
let x = 0;
assert!(x == 0, 42);

let x = b"hello"; // x 已被遮蔽
assert!(x == b"hello", 42);
```

區域變數遭到遮蔽後，儲存在該區域變數中的值仍然存在，但將無法再存取。對於不具備 [`drop` ability](./abilities) 的型別值，請務必留意這點，因為值的所有權必須在函式結束前轉移。

```move
module 0::example;

public struct Coin has store { value: u64 }

fun unused_coin(): Coin {
// highlight-error-start
    let x = Coin { value: 0 }; // 錯誤！
//      ^ 此區域變數仍包含不具備 `drop` ability 的值
    x.value = 1;
    let x = Coin { value: 10 };
    x
//  ^ 無效的回傳
// highlight-error-end
}
```

當區域變數在範圍內遭到遮蔽時，遮蔽效果只會維持在該範圍內。該範圍結束後，遮蔽效果便會消失。

```move
let x = 0;
{
    let x = 1;
    assert!(x == 1, 42);
};
assert!(x == 0, 42);
```

請記得，區域變數遭到遮蔽時可以變更型別。

```move
let x = 0;
{
    let x = b"hello";
    assert!(x == b"hello", 42);
};
assert!(x == 0, 42);
```

## 移動與複製 (Move and Copy) {#move-and-copy}

Move 中的所有區域變數都可以透過兩種方式使用：`move` 或 `copy`。如果未指定其中之一，
Move 編譯器能夠推論應使用 `copy` 還是 `move`。這表示在上述所有範例中，編譯器都會插入
`move` 或 `copy`。區域變數無法在不使用 `move` 或 `copy` 的情況下使用。

對於來自其他程式語言的人而言，`copy` 很可能是最熟悉的方式，因為它會建立變數內值的新副本，
以供該運算式使用。使用 `copy` 時，區域變數可以使用多次。

```move
let x = 0;
let y = copy x + 1;
let z = copy x + 2;
```

任何具有 `copy` [能力](./abilities) 的值都可以透過這種方式複製，除非指定 `move`，
否則會隱含地複製。

`move` 會從區域變數取出值，_不複製資料_。發生 `move` 後，該區域變數便無法再使用，
即使值的型別具有 `copy` [能力](./abilities) 也是如此。

```move
let x = 1;
// highlight-error-start
let y = move x + 1;
//      ------ 區域變數在此被移動
let z = move x + 2; // 錯誤！
//      ^^^^^^ 無效地使用區域變數 'x'
// highlight-error-end
y + z
```

### 安全性 (Safety) {#safety}

Move 的型別系統會防止值在被移動後再次使用。這與 [`let` 宣告](#let-bindings)中所述的安全性
檢查相同，該檢查可防止區域變數在被指派值之前使用。

<!-- 如需更多資訊，請參閱未來關於所有權與移動語意的 TODO 章節。 -->

### 推論 (Inference) {#inference}

如上所述，如果未指出 `copy` 或 `move`，Move 編譯器會進行推論。執行此作業的演算法
相當簡單：

- 任何具有 `copy` [能力](./abilities) 的值都會使用 `copy`。
- 任何參考（可變 `&mut` 與不可變 `&`）都會使用 `copy`。
  - 除了在特殊情況下，為了讓借用檢查器錯誤更具可預測性，會改為使用 `move`。
    當該參考不再被使用時，就會發生這種情況。
- 任何其他值都會使用 `move`。

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

let s2 = s; // 複製
let foo2 = foo; // 複製
let coin2 = coin; // 移動
let coins2 = coins; // 移動

let x = 0;
let b = false;
let addr = @0x42;
let x_ref = &x;
let coin_ref = &mut coin2;

let x2 = x; // 複製
let b2 = b; // 複製
let addr2 = @0x42; // 複製
let x_ref2 = x_ref; // 複製
let coin_ref2 = coin_ref; // 複製
```
