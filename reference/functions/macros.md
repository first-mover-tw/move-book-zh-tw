---
title: 巨集函式 (Macro Functions) | 參考手冊
description: Move 巨集函式 (macro functions) 參考手冊：編譯時期展開 (compile-time expansion)、Lambda 參數 (lambda parameters)、型別參數 (type parameters) 與巨集 (macros) 的方法語法 (method syntax)。
keywords:
  - Move
  - Sui
  - Move reference
  - macro
  - functions
  - reference
questions:
  - How does Macro Functions work in Move?
  - What is the syntax for Macro Functions in Move?
  - What is Lambdas in Move?
  - What is Typing in Move?
answer: 'Move macro functions reference: compile-time expansion, lambda parameters, type parameters, and method syntax for macros.'
goal:
  description: 'Reader understands move macro functions reference: compile-time expansion, lambda parameters, type parameters, and method syntax for macros'
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

# 巨集函式 (Macro Functions) {#macro-functions}

巨集函式是一種定義函式的方法，會在每個呼叫位置於編譯期間展開。巨集的引數不會像一般函式一樣立即求值，而是以運算式取代。此外，呼叫端可以透過
[lambda](#lambdas) 向巨集提供程式碼。

這些運算式取代機制使 `macro` 函式類似於
[其他程式語言中的巨集](<https://en.wikipedia.org/wiki/Macro_(computer_science)>)；
不過，Move 中的限制比你可能從其他語言預期的更多。`macro` 函式的
參數和回傳值仍具有型別——但可透過 [`_` 型別](./../generics#_-type) 部分放寬此限制。然而，這項限制的優點是
`macro` 函式可在一般函式可使用的任何地方使用，這在使用
[方法語法](./../method-syntax) 時特別有幫助。

未來可能會提供更完整的
[語法巨集](<https://en.wikipedia.org/wiki/Macro_(computer_science)#Syntactic_macros>) 系統。

## 語法 (Syntax) {#syntax}

`macro` 函式的語法與一般函式相似。不過，所有型別參數名稱和所有參數名稱都必須以 `$` 開頭。請注意，`_` 仍可單獨使用，但不可作為前綴；必須改用 `$_`。

```text
<visibility>? macro fun <identifier><[$type_parameters: constraint],*>([$identifier: type],*): <return_type> <function_body>
```

例如，下列 `macro` 函式接受一個向量和一個 lambda，並將 lambda 套用至向量中的每個元素，以建立新的向量。

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

`$` 的用途是表示這些參數（包含型別參數和值參數）的行為不同於一般的非巨集對應項目。對於型別參數，它們可使用任何型別（甚至是參考型別 `&` 或 `&mut`）具現化，且會滿足任何約束。參數也是如此：它們不會被及早求值，而是會在每次使用時代入引數運算式。

## Lambda 運算式 (Lambdas) {#lambdas}

Lambda 運算式是一種只能搭配 `macro` 使用的新型運算式。它們用於將程式碼從呼叫端傳入 `macro` 的主體中。雖然替換作業是在編譯時期完成，但其使用方式與其他語言中的[匿名函式](https://en.wikipedia.org/wiki/Anonymous_function)、[lambda 運算式](https://en.wikipedia.org/wiki/Lambda_calculus)或[閉包](<https://en.wikipedia.org/wiki/Closure_(computer_programming)>)類似。

如上例所示（`$f: |$T| -> $U`），lambda 型別以下列語法定義：

```text
|<type>,*| (-> <type>)?
```

幾個範例：

```move
|u64, u64| -> u128 // 接受兩個 u64 並回傳 u128 的 lambda 運算式
|&mut vector<u8>| -> &mut u8 // 接受 &mut vector<u8> 並回傳 &mut u8 的 lambda 運算式
```

若未標註回傳型別，預設為單元 `()`。

```move
// 以下兩者等價
|&mut vector<u8>, u64|
|&mut vector<u8>, u64| -> ()
```

接著，在 `macro` 的呼叫位置以下列語法定義 lambda 運算式：

```text
|(<identifier> (: <type>)?),*| <expression>
|(<identifier> (: <type>)?),*| -> <type> { <expression> }
```

請注意，若標註回傳型別，lambda 運算式的主體必須以 `{}` 包住。

使用上方定義的 `map` macro：

```move
let v = vector[1, 2, 3];
let doubled: vector<u64> = map!(v, |x| 2 * x);
let bytes: vector<vector<u8>> = map!(v, |x| std::bcs::to_bytes(&x));
```

搭配型別標註：

```move
let doubled: vector<u64> = map!(v, |x: u64| 2 * x); // 回傳型別標註為選用
let bytes: vector<vector<u8>> = map!(v, |x: u64| -> vector<u8> { std::bcs::to_bytes(&x) });
```

### 擷取 (Capturing) {#capturing}

Lambda 運算式也可以參考定義該 lambda 運算式之作用域內的變數。這有時稱為「擷取」。

```move
let res = foo();
let incremented = map!(vector[1, 2, 3], |x| x + res);
```

任何變數都可以被擷取，包括可變與不可變參考。

如需更複雜的用法，請參閱[範例](#iterating-over-a-vector)章節。

### 限制 (Limitations) {#limitations}

目前，lambda 運算式只能直接用於 `macro` 函式的呼叫中。它們無法繫結至變數。例如，下列程式碼會產生錯誤：

```move
let f = |x| 2 * x;
//      ^^^^^^^^^ 錯誤！Lambda 運算式必須直接用於 'macro' 呼叫中
let doubled: vector<u64> = map!(vector[1, 2, 3], f);
```

## 型別標註 (Typing) {#typing}

如同一般函式，`macro` 函式具有型別——參數與回傳值的型別
必須加上標註。不過，函式主體要等到巨集展開後才會進行型別檢查。
這表示特定巨集的所有使用方式不一定都有效。例如：

```move
macro fun add_one<$T>($x: $T): $T {
    $x + 1
}
```

若 `$T` 不是基本整數型別，上述巨集將無法通過型別檢查。

這在搭配[方法語法](./../method-syntax)時特別有用，因為該函式要等到巨集展開後才會解析。

```move
macro fun call_foo<$T, $U>($x: $T): &$U {
    $x.foo()
}
```

只有當 `$T` 具有回傳參考 `&$U` 的 `foo` 方法時，此巨集才能成功展開。
如同[衛生性](#hygiene)章節所述，`foo` 會依據定義 `call_foo` 的作用域解析——而非其展開的位置。

### 型別參數 (Type Parameters) {#type-parameters}

型別參數可使用任何型別進行具現化，包括參考型別 `&` 與 `&mut`。它們
也可以使用[元組型別](./../primitive-types/tuples)進行具現化，但目前其用途有限，因為元組無法繫結至變數。

此放寬規則會迫使型別參數的約束條件在呼叫位置以一般不會發生的方式獲得滿足。不過，通常仍建議為型別參數新增所有必要的約束條件。例如：

```move
public struct NoAbilities()
public struct CopyBox<T: copy> has copy, drop { value: T }
macro fun make_box<$T>($x: $T): CopyBox<$T> {
    CopyBox { value: $x }
}
```

只有在以具有 `copy` 能力的型別具現化 `$T` 時，此巨集才會展開。

```move
make_box!(1); // 有效！
make_box!(NoAbilities()); // 錯誤！'NoAbilities' 不具有 copy 能力
```

建議的 `make_box` 宣告方式是將 `copy` 約束新增至型別參數。這會向呼叫端表達該型別必須具有 `copy` 能力。

```move
macro fun make_box<$T: copy>($x: $T): CopyBox<$T> {
    CopyBox { value: $x }
}
```

那麼，如果建議不要使用這項放寬規則，為何還要提供它？由於主體在展開前不會經過檢查，因此在所有情況下都無法強制執行型別參數的約束條件。在下列範例中，簽章不需要 `$T` 的 `copy` 約束，但主體需要。

```move
macro fun read_ref<$T>($r: &$T): $T {
    *$r
}
```

不過，若你想要使用極為寬鬆的型別簽章，建議改用[`_` 型別](#_-type)。

### `_` 型別 (`_` Type) {#_-type}

通常，[`_` 佔位符型別](./../generics#_-type)會在運算式中使用，以允許對型別引數進行
部分註記。不過，對於 `macro` 函式，`_` 型別可取代型別參數使用，以放寬任何型別的簽章。這應能提升宣告「泛型」`macro` 函式的人體工學。

例如，我們可以接受任何整數組合並將其相加。

```move
macro fun add($x: _, $y: _, $z: _): u256 {
    ($x as u256) + ($y as u256) + ($z as u256)
}
```

此外，`_` 型別可使用不同型別具現化 _多次_。例如：

```move
public struct Box<T> has copy, drop, store { value: T }
macro fun create_two($f: |_| -> Box<_>): (Box<u8>, Box<u16>) {
    ($f(0u8), $f(0u16))
}
```

若我們改為使用型別參數宣告函式，這些型別就必須統一為共同型別，
但在此情況下無法做到。

```move
macro fun create_two<$T>($f: |$T| -> Box<$T>): (Box<u8>, Box<u16>) {
    ($f(0u8), $f(0u16))
    //           ^^^^ 錯誤！預期為 `u8`，但找到 `u16`
}
...
let (a, b) = create_two!(|value| Box { value });
```

在此情況下，`$T` 必須以單一型別具現化，但型別推斷發現 `$T` 必須
同時繫結至 `u8` 與 `u16`。

然而，這存在取捨，因為 `_` 型別向呼叫端傳達的意義與意圖較少。
考慮將上方的 `map` macro 重新宣告，以 `_` 取代 `$T` 與 `$U`。

```move
macro fun map($v: vector<_>, $f: |_| -> _): vector<_> {
```

型別層級不再有任何 `$f` 行為的指示。呼叫端必須從註解或 macro 的主體
理解其行為。

## 展開與替換 (Expansion and Substitution) {#expansion-and-substitution}

`macro` 的主體會在建置時期替換至呼叫位置。每個參數都會以其引數的*運算式*取代，而非其值。對於 lambda，可在 `macro` 主體的內容中為額外的區域變數繫結值。

以一個非常簡單的範例來說

```move
macro fun apply($f: |u64| -> u64, $x: u64): u64 {
    $f($x)
}
```

使用以下呼叫位置

```move
let incremented = apply!(|x| x + 1, 5);
```

大致會展開為

```move
let incremented = {
    let x = { 5 };
    { x + 1 }
};
```

再次強調，替換的不是 `x` 的值，而是運算式 `5`。這可能表示某個引數會被評估多次，或完全不被評估，取決於 `macro` 的主體。

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    $f($x, $x)
}
```

```move
let sum = dup!(|x, y| x + y, foo());
```

會展開為

```move
let sum = {
    let x = { foo() };
    let y = { foo() };
    { x + y }
};
```

請注意，`foo()` 會被呼叫兩次。如果 `dup` 是一般函式，便不會發生這種情況。

通常建議藉由將引數繫結至區域變數，建立可預測的評估行為。

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    let a = $x;
    $f(a, a)
}
```

現在相同的呼叫位置會展開為

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

### 衛生性 (Hygiene) {#hygiene}

在上述範例中，`dup` 巨集有一個區域變數 `a`，用來繫結引數
`$x`。你可能會問，如果該變數改名為 `x`，會發生什麼事？它會與 lambda 中的 `x` 衝突嗎？

簡短的答案是：不會。`macro` 函式具有
[衛生性](https://en.wikipedia.org/wiki/Hygienic_macro)，這表示 `macro` 與
lambda 的展開不會意外擷取來自其他範圍的變數。

編譯器會透過為每個範圍關聯一個唯一編號來達成此事。當 `macro` 展開時，
巨集主體會取得自己的範圍。此外，引數會在每次使用時重新設定範圍。

將 `dup` 巨集修改為使用 `x` 而非 `a`

```move
macro fun dup($f: |u64, u64| -> u64, $x: u64): u64 {
    let a = $x;
    $f(a, a)
}
```

呼叫位置的展開結果

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

這是編譯器內部表示法的近似結果；為了讓此範例保持簡潔，省略了一些細節。

而且，每次使用引數時都會重新設定範圍，讓不同的使用方式不會產生衝突。

```move
macro fun apply_twice($f: |u64| -> u64, $x: u64): u64 {
    $f($x) + $f($x)
}
```

```move
let result = apply_twice!(|x| x + 1, { let x = 5; x });
```

展開為

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

與變數衛生性類似，[方法解析](./../method-syntax)也會限定在巨集
定義的範圍內。例如：

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

在此情況下，方法呼叫 `foo` 一律會解析為函式 `f`，即使 `call_foo`
在 `foo` 繫結至不同函式（例如 `g`）的範圍中使用也是如此。

```move
fun example(s: &S): u64 {
    use fun g as foo;
    call_foo!(s) // 展開為 'f(s)'，而非 'g(s)'
}
```

因此，在具有 `macro` 函式的模組中，未使用的 `use fun` 宣告可能不會產生警告。

### 控制流程 (Control Flow) {#control-flow}

與變數衛生性類似，控制流程建構也一律限定於其定義的位置，而不是其展開的位置。

```move
macro fun maybe_div($x: u64, $y: u64): u64 {
    let x = $x;
    let y = $y;
    if (y == 0) return 0;
    x / y
}
```

在呼叫位置，`return` 一律會從 `macro` 主體回傳，而不是從呼叫端回傳。

```move
let result: vector<u64> = vector[maybe_div!(10, 0)];
```

將展開為

```move
let result: vector<u64> = vector['a: {
    let x = { 10 };
    let y = { 0 };
    if (y == 0) return 'a 0;
    x / y
}];
```

其中，`return 'a 0` 會回傳至區塊 `'a: { ... }`，而不是呼叫端的主體。更多詳細資訊請參閱[帶標籤的控制流程](./../control-flow/labeled-control-flow)章節。

同樣地，lambda 中的 `return` 會從 lambda 回傳，而不是從 `macro` 主體或外層函式回傳。

```move
macro fun apply($f: |u64| -> u64, $x: u64): u64 {
    $f($x)
}
```

以及

```move
let result = apply!(|x| { if (x == 0) return 0; x + 1 }, 100);
```

將展開為

```move
let result = {
    let x = { 100 };
    'a: {
        if (x == 0) return 'a 0;
        x + 1
    }
};
```

除了從 lambda 回傳之外，也可以使用標籤回傳至外層函式。在 `vector::any` 巨集中，會使用帶有標籤的 `return` 提早從整個 `macro` 回傳。

```move
public macro fun any<$T>($v: &vector<$T>, $f: |&$T| -> bool): bool {
    let v = $v;
    'any: {
        v.do_ref!(|e| if ($f(e)) return 'any true);
        false
    }
}
```

當條件成立時，`return 'any true` 會提早離開「迴圈」。否則，巨集會「回傳」`false`。

### 方法語法 (Method Syntax) {#method-syntax}

在適用的情況下，可以使用[方法語法](./../method-syntax)呼叫 `macro` 函式。使用方法語法時，引數的求值方式會改變：第一個引數（方法的「接收者」）會在巨集展開之外進行求值。這個範例雖然是刻意設計的，但能簡潔地展示此行為。

```move
public struct S() has copy, drop;
public fun foo(): S { abort 0 }
public macro fun maybe_s($s: S, $cond: bool): S {
    if ($cond) $s
    else S()
}
```

即使 `foo()` 會中止，其回傳型別仍可用於開始方法呼叫。

若 `$cond` 為 `false`，則不會對 `$s` 求值；在一般的非方法呼叫下，`foo()` 的引數也不會被求值，因此不會中止。以下範例展示了使用 `foo()` 作為引數時，`$s` 不會被求值。

```move
maybe_s!(foo(), false) // 不會中止
```

查看展開後的形式，即可更清楚了解它為何不會中止：

```move
if (false) foo()
else S()
```

然而，使用方法語法時，第一個引數會在巨集展開前求值。因此，作為 `$s` 的同一個 `foo()` 引數現在會被求值，並且會中止。

```move
foo().maybe_s!(false) // 會中止
```

查看展開後的形式，可以更清楚地看到這一點：

```move
let tmp = foo(); // 會中止
if (false) tmp
else S()
```

從概念上來說，方法呼叫的接收者會在巨集展開前繫結至暫存變數，這會強制進行求值，因而導致中止。

### 參數限制 (Parameter Limitations) {#parameter-limitations}

`macro` 函式的參數必須一律作為運算式使用。它們不能用於引數可能被重新解讀的
情況。例如，下列寫法不被允許：

```move
macro fun no($x: _): _ {
    $x.f
}
```

原因是若引數 `$x` 不是參考，會先對它進行借用，這可能會重新解讀該引數。若要避開
此限制，你應將引數繫結至區域變數。

```move
macro fun yes($x: _): _ {
    let x = $x;
    x.f
}
```

## 範例 (Examples) {#examples}

### 惰性引數：assert_eq (Lazy arguments: assert_eq) {#lazy-arguments-assert_eq}

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

在此情況下，除非斷言失敗，否則不會評估傳遞給 `$code` 的引數。

```move
assert_eq!(vector[true, false], vector[true, false], 1 / 0); // 不會評估除以零
```

### 任意整數的平方根 (Any integer square root) {#any-integer-square-root}

此巨集會計算除 `u256` 以外任何整數型別的整數平方根。

`$T` 是輸入的型別，而 `$bitsize` 是該型別中的位元數；例如，`u8`
有 8 個位元。`$U` 應設定為下一個較大的整數型別，例如 `u8` 對應的 `u16`。

在此 `macro` 中，整數字面值 `1` 和 `0` 的型別會加上註記，例如 `(1: $U)`，
以便每次呼叫時字面值的型別可以不同。同樣地，`as` 也可以搭配型別參數 `$T` 和 `$U` 使用。此巨集只有在 `$T` 和 `$U`
以整數型別具現化時，才能成功展開。

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

這兩個 `macro` 分別以不可變與可變方式走訪向量。

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

一些使用範例

```move
fun imm_examples(v: &vector<u64>) {
    // 印出所有元素
    for_imm!(v, |x| std::debug::print(x));

    // 將所有元素加總
    let mut sum = 0;
    for_imm!(v, |x| sum = sum + x);

    // 找出最大元素
    let mut max = 0;
    for_imm!(v, |x| if (x > max) max = x);
}

fun mut_examples(v: &mut vector<u64>) {
    // 將每個元素遞增
    for_mut!(v, |x| *x = *x + 1);

    // 將每個元素設為前一個值，並將第一個元素設為最後一個值
    let mut prev = v[v.length() - 1];
    for_mut!(v, |x| {
        let tmp = *x;
        *x = prev;
        prev = tmp;
    });

    // 將最大元素設為 0
    let mut max = &mut 0;
    for_mut!(v, |x| if (*x > *max) max = x);
    *max = 0;
}
```

### 非迴圈 lambda 用法 (Non-loop lambda usage) {#non-loop-lambda-usage}

Lambda 不需要在迴圈中使用，且通常適合用來有條件地套用程式碼。

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

以下是一些使用範例

```move
fun examples(opt: Option<u64>) {
    // 若值存在，則印出該值
    inspect!(&opt, |x| std::debug::print(x));

    // 檢查值是否為 0
    let is_zero = is_some_and!(&opt, |x| *x == 0);

    // 將 u64 向上轉型為 u256
    let str_opt = map!(opt, |x| x as u256);
}
```
