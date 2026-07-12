---
title: 巨集函式 (Macro Functions) | 參考手冊
description: Move 巨集函式參考手冊 (Move macro functions reference)：編譯時期展開、Lambda 參數、型別參數與巨集的方法語法。
---

# 巨集函式 (Macro Functions)

巨集 (Macro) 函式是定義函式的一種方式，這些函式在編譯時會在每個呼叫點進行展開。巨集的引數不像普通函式那樣被提早求值 (evaluated eagerly)，而是透過運算式進行替換。此外，呼叫者可以透過 [Lambdas](#lambdas) 向巨集提供程式碼。

這種運算式替換機制使得 `macro` 函式類似於[在其他程式語言中發現的巨集](<https://en.wikipedia.org/wiki/Macro_(computer_science)>)；然而，在 Move 中它們受到的限制比你可能從其他語言預期的更多。`macro` 函式的參數和回傳值仍然是具備型別的 —— 儘管這可以透過 [`_` 型別](./../generics#_-型別) 來部分放寬。不過，這種限制的好處在於 `macro` 函式可以在任何普通函式可以使用的中央使用，這在 [方法語法 (Method Syntax)](./../method-syntax) 中特別有用。

未來可能會推出更廣泛的[語法巨集系統](<https://en.wikipedia.org/wiki/Macro_(computer_science)#Syntactic_macros>)。

## 語法

`macro` 函式的語法與普通函式類似。但是，所有型別參數名稱和所有參數名稱必須以 `$` 開頭。請注意，`_` 仍然可以單獨使用，但不能作為前綴，必須改用 `$_`。

```text
<可見性>? macro fun <識別碼><[$型別參數: 約束],*>([$參數名稱: 型別],*): <回傳型別> <函式主體>
```

例如，以下 `macro` 函式接受一個向量和一個 lambda，並將 lambda 應用於向量的每個元素以建構一個新的向量。

```move
macro fun map<$T, $U>($v: vector<$T>, $f: |$T| -> $U): vector<$U> {
    let mut v = $v;
    v.reverse();
    let mut i = 0;
    let mut result = vector[];
    while (!v.is_empty()) {
        result.push_back($f(v.pop_back()));
        i = i + 1;
    };
    result
}
```

這裡的 `$` 是用來指示參數（包括型別參數和數值參數）的行為不像它們非巨集的對應部分。對於型別參數，它們可以用任何型別實例化（甚至是參考型別 `&` 或 `&mut`），並且它們會滿足任何約束。同樣對於參數，它們不會被提早求值，相反，引數運算式將在每次使用時被替換。

## Lambdas

Lambdas 是一種新型運算式，只能與 `macro` 一起使用。它們用於將程式碼從呼叫者傳遞到 `macro` 的主體中。雖然替換是在編譯時完成的，但它們的使用方式類似於其他語言中的[匿名函式 (Anonymous functions)](https://en.wikipedia.org/wiki/Anonymous_function)、[lambdas](https://en.wikipedia.org/wiki/Lambda_calculus) 或 [閉包 (Closures)](<https://en.wikipedia.org/wiki/Closure_(computer_programming)>)。

如上例所示 (`$f: |$T| -> $U`)，lambda 型別的定義語法為：

```text
|<型別>,*| (-> <型別>)?
```

幾個例子：

```move
|u64, u64| -> u128 // 一個接受兩個 u64 並回傳一個 u128 的 lambda
|&mut vector<u8>| -> &mut u8 // 一個接受 &mut vector<u8> 並回傳一個 &mut u8 的 lambda
```

如果回傳型別未標註，則預設為單元型別 `()`。

```move
// 以下兩者是等價的
|&mut vector<u8>, u64|
|&mut vector<u8>, u64| -> ()
```

Lambda 運算式隨後在 `macro` 的呼叫點使用以下語法定義：

```text
|(<識別碼> (: <型別>)?),*| <運算式>
|(<識別碼> (: <型別>)?),*| -> <型別> { <運算式> }
```

請注意，如果標註了回傳型別，lambda 的主體必須封裝在 `{}` 中。

使用上面定義的 `map` 巨集：

```move
let v = vector[1, 2, 3];
let doubled: vector<u64> = map!(v, |x| 2 * x);
let bytes: vector<vector<u8>> = map!(v, |x| std::bcs::to_bytes(&x));
```

帶有型別標註：

```move
let doubled: vector<u64> = map!(v, |x: u64| 2 * x); // 回傳型別標註可選
let bytes: vector<vector<u8>> = map!(v, |x: u64| -> vector<u8> { std::bcs::to_bytes(&x) });
```

### 捕捉 (Capturing)

Lambda 運算式還可以參考定義 lambda 的範圍內的變數。這有時被稱為「捕捉」。

```move
let res = foo();
let incremented = map!(vector[1, 2, 3], |x| x + res);
```

任何變數都可以被捕捉，包括可變和不可變參考。

有關更複雜的使用方式，請參閱[範例](#iterating-over-a-vector)章節。

### 限制

目前，lambdas 只能直接在 `macro` 函式的呼叫中使用。它們不能綁定到變數。例如，以下程式碼將產生錯誤：

```move
let f = |x| 2 * x;
//      ^^^^^^^^^ 錯誤！Lambdas 必須直接在 'macro' 呼叫中使用
let doubled: vector<u64> = map!(vector[1, 2, 3], f);
```

## 型別系統 (Typing)

與普通函式一樣，`macro` 函式是具備型別的 —— 參數和回傳值的型別必須經過標註。但是，函式的主體在巨集展開之前不會進行型別檢查。這意味著並非給定巨集的所有用法都是有效的。例如：

```move
macro fun add_one<$T>($x: $T): $T {
    $x + 1
}
```

如果 `$T` 不是原始整數型別，上述巨集的型別檢查將不會通過。

這在與 [方法語法 (Method Syntax)](./../method-syntax) 結合使用時特別有用，其中函式直到巨集展開後才會被解析。

```move
macro fun call_foo<$T, $U>($x: $T): &$U {
    $x.foo()
}
```

只有當 `$T` 具備一個回傳參考 `&$U` 的 `foo` 方法時，此巨集才能成功展開。如[衛生 (Hygiene)](#hygiene)章節所述，`foo` 將根據 `call_foo` 被定義的範圍來解析，而不是它被展開的範圍。

### 型別參數

型別參數可以用任何型別實例化，包括參考型別 `&` 和 `&mut`。它們也可以用[元組型別](./../primitive-types/tuples)實例化，儘管目前這類操作的效用有限，因為元組無法綁定到變數。

這種放寬限制迫使型別參數的約束在呼叫點以一種通常不會發生的方式被滿足。然而，通常還是建議為型別參數加上所有必要的約束。例如：

```move
public struct NoAbilities()
public struct CopyBox<T: copy> has copy, drop { value: T }
macro fun make_box<$T>($x: $T): CopyBox<$T> {
    CopyBox { value: $x }
}
```

只有當 `$T` 用具備 `copy` 能力的型別實例化時，此巨集才能展開。

```move
make_box!(1); // 有效！
make_box!(NoAbilities()); // 錯誤！'NoAbilities' 不具備 copy 能力
```

對 `make_box` 的建議宣告是將 `copy` 約束加到型別參數中。這樣就能告知呼叫者該型別必須具備 `copy` 能力。

```move
macro fun make_box<$T: copy>($x: $T): CopyBox<$T> {
    CopyBox { value: $x }
}
```

那麼你可能會問，如果建議是不使用這種放寬，為什麼還要具備這種放寬呢？原因是型別參數上的約束在所有情況下都無法被強制執行，因為主體在展開之前是不會檢查的。在以下範例中，簽名中對 `$T` 的 `copy` 約束不是必需的，但在主體中卻是必需的。

```move
macro fun read_ref<$T>($r: &$T): $T {
    *$r
}
```

然而，如果你想擁有一個極其寬鬆的型別簽名，建議改用 [`_` 型別](#_-型別)。

### `_` 型別

通常，[`_` 佔位符型別](./../generics#_-型別) 用於運算式中，以允許對型別引數進行部分標註。然而，在 `macro` 函式中，`_` 型別可以用來代替型別參數，以便為任何型別放寬簽名。這應該能增加宣告「泛型」`macro` 函式的便利性。

例如，我們可以接受整數的任何組合並將它們相加。

```move
macro fun add($x: _, $y: _, $z: _): u256 {
    ($x as u256) + ($y as u256) + ($z as u256)
}
```

此外，`_` 型別可以用不同型別實例化 _多次_。例如：

```move
public struct Box<T> has copy, drop, store { value: T }
macro fun create_two($f: |_| -> Box<_>): (Box<u8>, Box<u16>) {
    ($f(0u8), $f(0u16))
}
```

如果我們改用型別參數來宣告該函式，則型別必須統一為共同的型別，這在這種情況下是不可能的。

```move
macro fun create_two<$T>($f: |$T| -> Box<$T>): (Box<u8>, Box<u16>) {
    ($f(0u8), $f(0u16))
    //           ^^^^ 錯誤！預期為 `u8` 但找到了 `u16`
}
...
let (a, b) = create_two!(|value| Box { value });
```

在這種情況下，`$T` 必須實例化為單一型別，但推斷發現 `$T` 必須同時綁定到 `u8` 和 `u16`。

不過這其中也存在權衡，因為 `_` 型別對於呼叫者而言傳達的意義和意圖較少。考慮將上面宣告的 `map` 巨集改用 `_` 代替 `$T` 和 `$U`。

```move
macro fun map($v: vector<_>, $f: |_| -> _): vector<_> {
```

在型別層級上不再有任何關於 `$f` 行為的指示。呼叫者必須從註解或巨集主體中獲得理解。

## 展開與替換 (Expansion and Substitution)

`macro` 的主體在編譯時被替換到呼叫點。每個參數都被其引數的「運算式」而非「數值」所替換。對於 lambdas，可以在 `macro` 主體的上下文中綁定額外的本地變數數值。

舉一個非常簡單的例子：

```move
macro fun apply($f: |u64| -> u64, $x: u64): u64 {
    $f($x)
}
```

在呼叫點：

```move
let incremented = apply!(|x| x + 1, 5);
```

這大約會被展開為：

```move
let incremented = {
    let x = { 5 };
    { x + 1 }
};
```

再次強調，替換的不是 `x` 的值，而是運算式 `5`。這可能意味著一個引數會被求值多次，或者根本不求值，具體取決於 `macro` 的主體。

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    $f($x, $x)
}
```

```move
let sum = dup!(|x, y| x + y, foo());
```

會展開為：

```move
let sum = {
    let x = { foo() };
    let y = { foo() };
    { x + y }
};
```

請注意，`foo()` 將被呼叫兩次。如果 `dup` 是普通函式，則不會發生這種情況。

通常建議透過將引數綁定到本地變數來建立可預測的求值行為。

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    let a = $x;
    $f(a, a)
}
```

現在同一個呼叫點將展開為：

```move
let sum = {
    let a = { foo() };
    {
        let x = { a };
        let y = { a };
        { x + y }
    }
};
```

### 衛生 (Hygiene) {#hygiene}

在上面的範例中，`dup` 巨集有一個本地變數 `a`，用於綁定引數 `$x`。你可能會問，如果變數被命名為 `x` 會發生什麼？這會與 lambda 中的 `x` 產生衝突嗎？

簡短的回答是，不會。`macro` 函式是具備[衛生 (Hygienic)](https://en.wikipedia.org/wiki/Hygienic_macro)性的，這意味著 `macro`s 和 lambdas 的展開不會意外捕捉到來自另一個範圍的變數。

編譯器透過為每個範圍關聯一個唯一數字來實現這一點。當 `macro` 展開時，巨集主體會獲得它自己的範圍。此外，引數在每次使用時都會被重新劃分範圍 (re-scoped)。

修改 `dup` 巨集以使用 `x` 代替 `a`：

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    let x = $x;
    $f(x, x)
}
```

呼叫點的展開：

```move
// let sum = dup!(|x, y| x + y, foo());
let sum = {
    let x#1 = { foo() };
    {
        let x#2 = { x#1 };
        let y#2 = { x#1 };
        { x#2 + y#2 }
    }
};
```

這是編譯器內部表示的近似值，為了簡化範例，省略了一些細節。

並且引數的每次使用都會重新劃分範圍，以便不同的用法不會衝突。

```move
macro fun apply_twice($f: |u64| -> u64, $x: u64): u64 {
    $f($x) + $f($x)
}
```

```move
let result = apply_twice!(|x| x + 1, { let x = 5; x });
```

展開為：

```move
let result = {
    {
        let x#1 = { let x#2 = { 5 }; x#2 };
        { x#1 + x#1 }
    }
    +
    {
        let x#3 = { let x#4 = { 5 }; x#4 };
        { x#3 + x#3 }
    }
};
```

與變數衛生類似，[方法解析 (Method Resolution)](./../method-syntax) 的範圍也侷限於巨集定義。例如：

```move
public struct S { f: u64, g: u64 }

fun f(s: &S): u64 {
    s.f
}
fun g(s: &S): u64 {
    s.g
}

use fun f as foo;
macro fun call_foo($s: &S): u64 {
    let s = $s;
    s.foo()
}
```

在這種情況下，方法呼叫 `foo` 始終會解析為函式 `f`，即使 `call_foo` 被用於 `foo` 綁定到不同函式（例如 `g`）的範圍內也一樣。

```move
fun example(s: &S): u64 {
    use fun g as foo;
    call_foo!(s) // 展開為 'f(s)'，而非 'g(s)'
}
```

不過正因為如此，在帶有 `macro` 函式的模組中，未使用的 `use fun` 宣告可能不會收到警告。

### 控制流 (Control Flow)

與變數衛生類似，控制流結構始終侷限於它們被定義的地方，而不是它們被展開的地方。

```move
macro fun maybe_div($x: u64, $y: u64): u64 {
    let x = $x;
    let y = $y;
    if (y == 0) return 0;
    x / y
}
```

在呼叫點，`return` 始終會從 `macro` 主體回傳，而不是從呼叫者回傳。

```move
let result: vector<u64> = vector[maybe_div!(10, 0)];
```

將展開為：

```move
let result: vector<u64> = vector['a: {
    let x = { 10 };
    let y = { 0 };
    if (y == 0) return 'a 0;
    x / y
}];
```

其中 `return 'a 0` 將回傳到區塊 `'a: { ... }`，而不會回傳到呼叫者的主體。詳情請參閱[帶標籤的控制流 (Labeled Control Flow)](./../control-flow/labeled-control-flow)章節。

同樣地，lambda 中的 `return` 將從 lambda 回傳，而不是從 `macro` 主體回傳，也不會從外部函式回傳。

```move
macro fun apply($f: |u64| -> u64, $x: u64): u64 {
    $f($x)
}
```

並且：

```move
let result = apply!(|x| { if (x == 0) return 0; x + 1 }, 100);
```

將展開為：

```move
let result = {
    let x = { 100 };
    'a: {
        if (x == 0) return 'a 0;
        x + 1
    }
};
```

除了從 lambda 回傳外，還可以使用標籤回傳到外部函式。在 `vector::any` 巨集 中，帶有標籤的 `return` 用於提前從整個 `macro` 回傳：

```move
public macro fun any<$T>($v: &vector<$T>, $f: |&$T| -> bool): bool {
    let v = $v;
    'any: {
        v.do_ref!(|e| if ($f(e)) return 'any true);
        false
    }
}
```

當滿足條件時，`return 'any true` 會提前退出「迴圈」。否則，該巨集將「回傳」`false`。

### 方法語法 (Method Syntax)

在適用的情況下，可以使用 [方法語法 (Method Syntax)](./../method-syntax) 呼叫 `macro` 函式。使用方法語法時，引數的求值方式會發生變化，即第一個引數（方法的「接收者」）將在巨集展開之外進行求值。這個範例雖然是刻意構造的，但能簡明地演示這一行為。

```move
public struct S() has copy, drop;
public fun foo(): S { abort 0 }
public macro fun maybe_s($s: S, $cond: bool): S {
    if ($cond) $s
    else S()
}
```

即使 `foo()` 會中止，其回傳型別仍可用於啟動方法呼叫。

如果 `$cond` 為 `false`，則不會對 `$s` 進行求值，在正規的非方法呼叫下，`foo()` 的引數不會被求值，因此也不會中止。以下範例示範了當 `$cond` 為 `false` 時，不對 `foo()` 進行求值。

```move
maybe_s!(foo(), false) // 不會中止
```

查看展開形式就會變得很清晰：

```move
if (false) foo()
else S()
```

但是，當使用方法語法時，第一個引數會在巨集展開之前被求值。因此，同樣作為 `$s` 引數的 `foo()` 現在將被求值並導致中止。

```move
foo().maybe_s!(false) // 會中止
```

查看展開形式可以更清楚地看到：

```move
let tmp = foo(); // 中止
if (false) tmp
else S()
```

從概念上講，方法呼叫的接收者在巨集展開之前會被綁定到一個暫存變數中，這強制執行了求值並進而導致中止。

### 參數限制

`macro` 函式的參數必須始終作為運算式使用。它們不能用於引數可能被重新解釋的情況。例如，以下情況是不允許的：

```move
macro fun no($x: _): _ {
    $x.f
}
```

原因在於，如果引數 `$x` 不是參考，它會被先借用，這可能會重新解釋該引數。要繞過這項限制，你應該將引數綁定到本地變數。

```move
macro fun yes($x: _): _ {
    let x = $x;
    x.f
}
```

## 範例

### 延遲引數 (Lazy arguments)：assert_eq

```move
macro fun assert_eq<$T>($left: $T, $right: $T, $code: u64) {
    let left = $left;
    let right = $right;
    if (left != right) {
        std::debug::print(&b"assertion failed.\n left: ");
        std::debug::print(&left);
        std::debug::print(&b"\n does not equal right: ");
        std::debug::print(&right);
        abort $code;
    }
}
```

在此案例中，除非斷言失敗，否則不會對 `$code` 引數求值。

```move
assert_eq!(vector[true, false], vector[true, false], 1 / 0); // 除以零不會被求值
```

### 任意整數平方根

此巨集計算除 `u256` 以外的任何整數型別的整數平方根。

`$T` 是輸入的型別，`$bitsize` 是該型別中的位元數，例如 `u8` 有 8 位元。`$U` 應設定為下一個較大的整數型別，例如 `u8` 對應 `u16`。

在此 `macro` 中，整數常值 `1` 和 `0` 的型別經過了標註，例如 `(1: $U)`，這允許常值的型別隨每次呼叫而不同。同樣地，`as` 可以與型別參數 `$T` 和 `$U` 一起使用。只有當 `$T` 和 `$U` 使用整數型別實例化時，此巨集才能成功展開。

```move
macro fun num_sqrt<$T, $U>($x: $T, $bitsize: u8): $T {
    let x = $x;
    let mut bit = (1: $U) << $bitsize;
    let mut res = (0: $U);
    let mut x = x as $U;

    while (bit != 0) {
        if (x >= res + bit) {
            x = x - (res + bit);
            res = (res >> 1) + bit;
        } else {
            res = res >> 1;
        };
        bit = bit >> 2;
    };

    res as $T
}
```

### 走訪向量 (Iterating over a vector) {#iterating-over-a-vector}

這兩個 `macro` 分別對向量進行不可變和可變走訪。

```move
macro fun for_imm<$T>($v: &vector<$T>, $f: |&$T|) {
    let v = $v;
    let n = v.length();
    let mut i = 0;
    while (i < n) {
        $f(&v[i]);
        i = i + 1;
    }
}

macro fun for_mut<$T>($v: &mut vector<$T>, $f: |&mut $T|) {
    let v = $v;
    let n = v.length();
    let mut i = 0;
    while (i < n) {
        $f(&mut v[i]);
        i = i + 1;
    }
}
```

幾個使用範例：

```move
fun imm_examples(v: &vector<u64>) {
    // 列印所有元素
    for_imm!(v, |x| std::debug::print(x));

    // 加總所有元素
    let mut sum = 0;
    for_imm!(v, |x| sum = sum + x);

    // 尋找最大元素
    let mut max = 0;
    for_imm!(v, |x| if (x > max) max = x);
}

fun mut_examples(v: &mut vector<u64>) {
    // 遞增每個元素
    for_mut!(v, |x| *x = *x + 1);

    // 將每個元素設定為前一個值，第一個元素設定為最後一個值
    let mut prev = v[v.length() - 1];
    for_mut!(v, |x| {
        let tmp = *x;
        *x = prev;
        prev = tmp;
    });

    // 將最大元素設定為 0
    let mut max = &mut 0;
    for_mut!(v, |x| if (*x > *max) max = x);
    *max = 0;
}
```

### 非迴圈 lambda 用法

Lambda 不一定非得在迴圈中使用，它們在條件式應用程式碼時通常非常有用。

```move
macro fun inspect<$T>($opt: &Option<$T>, $f: |&$T|) {
    let opt = $opt;
    if (opt.is_some()) $f(opt.borrow())
}

macro fun is_some_and<$T>($opt: &Option<$T>, $f: |&$T| -> bool): bool {
    let opt = $opt;
    if (opt.is_some()) $f(opt.borrow())
    else false
}

macro fun map<$T, $U>($opt: Option<$T>, $f: |$T| -> $U): Option<$U> {
    let opt = $opt;
    if (opt.is_some()) {
        option::some($f(opt.destroy_some()))
    } else {
        opt.destroy_none();
        option::none()
    }
}
```

以及一些使用範例：

```move
fun examples(opt: Option<u64>) {
    // 如果數值存在則列印
    inspect!(&opt, |x| std::debug::print(x));

    // 檢查數值是否為 0
    let is_zero = is_some_and!(&opt, |x| *x == 0);

    // 將 u64 向上轉型為 u256
    let str_opt = map!(opt, |x| x as u256);
}
```
