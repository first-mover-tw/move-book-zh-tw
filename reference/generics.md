---
title: 泛型 (Generics) | 參考手冊
description:
  Move 泛型參考手冊 (Move generics reference)：函式與結構的型別參數 (type parameters)、約束
  (constraints)、幻影型別 (phantom types) 與參數多型 (parametric polymorphism)。
---

# 泛型 (Generics)

泛型可用於在不同的輸入資料型別上定義函式和結構體。這項語言特性有時被稱為參數化多型 (parametric polymorphism)。在 Move 中，我們通常會將「泛型」與 _型別參數 (type parameters)_ 及 _型別引數 (type arguments)_ 這幾個術語互換使用。

泛型常見於程式庫程式碼（例如 [向量 (vector)](./primitive-types/vector)），用於宣告適用於任何可能型別（只要滿足指定約束）的程式碼。這種參數化允許你在多種型別和情境中重複使用相同的實作。

## 宣告型別參數

函式和結構體都可以在其簽名中接受一組型別參數清單，並用一對角括號 `<...>` 括起來。

### 泛型函式

函式的型別參數放在函式名稱之後、(數值) 參數清單之前。以下程式碼定義了一個泛型恆等函式 (identity function)，它接受任何型別的數值並原樣傳回該值。

```move
fun id<T>(x: T): T {
    // 雖然這裡的型別標記是不必要的，但仍然有效
    (x: T)
}
```

一旦定義完成，型別參數 `T` 就可以用於參數型別、回傳型別以及函式主體內部。

### 泛型結構體

結構體的型別參數放在結構體名稱之後，可用於命名欄位的型別。

```move
public struct Foo<T> has copy, drop { x: T }

public struct Bar<T1, T2> has copy, drop {
    x: T1,
    y: vector<T2>,
}
```

請注意，[型別參數不一定要被使用](#unused-type-parameters)。

## 型別引數 (Type Arguments)

### 呼叫泛型函式

呼叫泛型函式時，可以在一對角括號括起來的清單中為函式的型別參數指定型別引數。

```move
fun foo() {
    let x = id<bool>(true);
}
```

如果你沒有指定型別引數，Move 的[型別推導 (type inference)](#type-inference) 將會為你自動填入。

### 使用泛型結構體

同樣地，在建構或解構泛型型別的數值時，可以為結構體的型別參數附加型別引數清單。

```move
fun foo() {
    // 建構時的型別引數
    let foo = Foo<bool> { x: true };
    let bar = Bar<u64, u8> { x: 0, y: vector<u8>[] };

    // 解構時的型別引數
    let Foo<bool> { x } = foo;
    let Bar<u64, u8> { x, y } = bar;
}
```

在任何情況下，如果你沒有指定型別引數，Move 的[型別推導 (type inference)](#type-inference) 將會為你自動填入。

### 型別引數不匹配

如果你指定了型別引數，但它們與實際提供的數值發生衝突，將會出現錯誤：

```move
fun foo() {
    let x = id<u64>(true); // 錯誤！true 不是 u64 型別
}
```

同樣地：

```move
fun foo() {
    let foo = Foo<bool> { x: 0 }; // 錯誤！0 不是 bool 型別
    let Foo<address> { x } = foo; // 錯誤！bool 與 address 型別不相容
}
```

## 型別推導 (Type Inference) {#type-inference}

在大多數情況下，Move 編譯器能夠推導出型別引數，因此你不需要顯式寫下它們。以下是省略型別引數時上述範例的樣子：

```move
fun foo() {
    let x = id(true);
    //        ^ 推導出 <bool>

    let foo = Foo { x: true };
    //           ^ 推導出 <bool>

    let Foo { x } = foo;
    //     ^ 推導出 <bool>
}
```

注意：當編譯器無法推導型別時，你需要手動標記它們。常見的情境是呼叫一個型別參數僅出現在回傳位置的函式。

```move
module a::m;

fun foo() {
    let v = vector[]; // 錯誤！
    //            ^ 編譯器無法得知元素型別，因為它從未被使用

    let v = vector<u64>[];
    //            ^~~~~ 這種情況下必須手動標記。
}
```

請注意，這些案例有點像刻意製造的，因為 `vector[]` 從未被使用，因此 Move 的型別推導無法推導其型別。

然而，如果該數值在函式後面被使用，編譯器就能推導出型別：

```move
module a::m;

fun foo() {
    let v = vector[];
    //            ^ 推導出 <u64>
    vector::push_back(&mut v, 42);
    //               ^ 推導出 <u64>
}
```

### `_` 型別

在某些情況下，你可能想要顯式標記部分型別引數，但讓編譯器推導其他引數。`_` 型別充當編譯器推導型別的佔位符 (placeholder)。

```move
let bar = Bar<u64, _> { x: 0, y: vector[b"hello"] };
//                 ^ 推導出 vector<u8>
```

佔位符 `_` 僅能出現在運算式和巨集函式定義中，不能出現在簽名中。這意味著你不能將 `_` 作為函式參數、函式回傳型別、常數定義型別或資料型別欄位定義的一部分。

## 整數 (Integers)

在 Move 中，整數型別 `u8`, `u16`, `u32`, `u64`, `u128` 和 `u256` 都是不同的型別。然而，每一種這類型別都可以用相同的數值語法來建立。換句話說，如果沒有提供型別後綴，編譯器將根據數值的使用情況來推導整數型別。

```move
let x8: u8 = 0;
let x16: u16 = 0;
let x32: u32 = 0;
let x64: u64 = 0;
let x128: u128 = 0;
let x256: u256 = 0;
```

如果該值未在需要特定整數型別的上下文中使用，則預設採用 `u64`。

```move
let x = 0;
//      ^ 預設使用 u64
```

然而，如果該值對於推導出的型別而言太大，將會報錯。

```move
let i: u8 = 256; // 錯誤！
//          ^^^ 對於 u8 而言太大
let x = 340282366920938463463374607431768211454;
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 對於 u64 而言太大
```

在數值太大的情況下，你可能需要顯式標記它：

```move
let x = 340282366920938463463374607431768211454u128;
//                                             ^^^^ 有效！
```

## 未使用的型別參數 (Unused Type Parameters) {#unused-type-parameters}

對於結構體定義，未使用的型別參數是指未出現在結構體定義的任何欄位中，但在編譯時會進行靜態檢查的參數。Move 允許未使用的型別參數，因此以下結構體定義是有效的：

```move
public struct Foo<T> {
    foo: u64
}
```

這在建模某些概念時會非常方便。以下是一個例子：

```move
module a::m;

// 貨幣識別符 (Currency Specifiers)
public struct A {}
public struct B {}

// 一個泛型代幣 (coin) 型別，可以使用貨幣識別符型別來實例化。
//   例如：Coin<A>, Coin<B> 等。
public struct Coin<Currency> has store {
    value: u64
}

// 針對所有貨幣撰寫泛型程式碼
public fun mint_generic<Currency>(value: u64): Coin<Currency> {
    Coin { value }
}

// 針對特定貨幣撰寫具體程式碼
public fun mint_a(value: u64): Coin<A> {
    mint_generic(value)
}
public fun mint_b(value: u64): Coin<B> {
    mint_generic(value)
}
```

在這個範例中，`Coin<Currency>` 對於 `Currency` 型別參數是泛型的，它指定了代幣的貨幣，並允許程式碼既可以針對任何貨幣以泛型方式撰寫，也可以針對特定貨幣以具體方式撰寫。即便 `Currency` 型別參數並未出現在 `Coin` 定義的任何欄位中，這種泛用性依然適用。

### 虛像型別參數 (Phantom Type Parameters)

在上述範例中，雖然 `struct Coin` 要求具備 `store` 能力，但 `Coin<A>` 和 `Coin<B>` 都不會具備 `store` 能力。這是因為[條件能力與泛型型別](./abilities#conditional-abilities-and-generic-types)的規則，以及 `A` 和 `B` 本身不具備 `store` 能力的事實 —— 儘管它們甚至沒有在 `struct Coin` 的主體中使用。這可能會導致一些令人不快的後果。例如，我們無法將 `Coin<A>` 放入儲存中的錢包。

一種可能的解決方案是為 `A` 和 `B` 加上多餘的能力標記（例如 `public struct Currency1 has store {}`）。但是，這可能會導致錯誤或安全漏洞，因為它透過不必要的能力宣告弱化了型別。例如，我們永遠不指望儲存中的數值具有型別 `A` 的欄位，但有了多餘的 `store` 能力這就變成了可能。此外，這些多餘標記具有傳染性，導致許多針對該未使用型別參數的泛型函式也必須包含必要的約束。

「虛像型別參數 (Phantom type parameters)」解決了這個問題。未使用的型別參數可以被標記為 _虛像 (phantom)_ 型別參數，它們不參與結構體的能力推導。透過這種方式，在衍生泛型型別的能力時，不會考慮針對虛像型別參數的引數，從而避免了對多餘能力標記的需求。為了使這條放寬的規則健全，Move 的型別系統保證宣告為 `phantom` 的參數要麼在結構體定義中完全不被使用，要麼僅作為引數傳遞給同樣被宣告為 `phantom` 的型別參數。

#### 宣告

在結構體定義中，可以透過在宣告前加上 `phantom` 關鍵字將型別參數宣告為虛像型別。

```move
public struct Coin<phantom Currency> has store {
    value: u64
}
```

如果一個型別參數被宣告為虛像，我們稱其為虛像型別參數。在定義結構體時，Move 的型別檢查器會確保每個虛像型別參數要麼不在結構體內部使用，要麼僅作為虛像型別參數的引數。

```move
public struct S1<phantom T1, T2> { f: u64 }
//               ^^^^^^^ 有效，T1 未出現在結構體定義中

public struct S2<phantom T1, T2> { f: S1<T1, T2> }
//               ^^^^^^^ 有效，T1 出現在虛像位置 (phantom position)
```

以下程式碼顯示了違反此規則的範例：

```move
public struct S1<phantom T> { f: T }
//               ^^^^^^^ 錯誤！  ^ 不是虛像位置

public struct S2<T> { f: T }
public struct S3<phantom T> { f: S2<T> }
//               ^^^^^^^ 錯誤！     ^ 不是虛像位置
```

更正式地說，如果一個型別被用作虛像型別參數的引數，我們稱該型別出現在 _虛像位置 (phantom position)_ 。有了這個定義，正確使用虛像參數的規則可以描述為：**虛像型別參數僅能出現在虛像位置**。

請注意，指定 `phantom` 並非強制要求，但如果一個型別參數本可以成為 `phantom` 卻未被標記，編譯器會發出警告。

#### 實例化 (Instantiation)

當實例化一個結構體時，在衍生結構體能力時會排除針對虛像參數的引數。例如，考慮以下程式碼：

```move
public struct S<T1, phantom T2> has copy { f: T1 }
public struct NoCopy {}
public struct HasCopy has copy {}
```

現在考慮型別 `S<HasCopy, NoCopy>`。因為 `S` 定義了 `copy`，且所有非虛像 (non-phantom) 引數都具備 `copy`，那麼 `S<HasCopy, NoCopy>` 也具備 `copy` 能力。

#### 具備能力約束的虛像型別參數

能力約束與虛像型別參數是正交的功能，意即虛像參數也可以帶有能力約束宣告。

```move
public struct S<phantom T: copy> {}
```

當用帶有能力約束的型別引數來實例化虛像型別參數時，型別引數必須滿足該約束，即便該參數是虛像參數也一樣。通常的限制依然適用，`T` 僅能用具備 `copy` 的引數來實例化。

## 約束 (Constraints)

在上述範例中，我們示範了如何使用型別參數來定義可由呼叫者稍後填入的「未知」型別。然而，這意味著型別系統關於該型別的資訊很少，必須以非常保守的方式進行檢查。從某種意義上說，型別系統必須為無約束的泛型（即沒有[能力 (abilities)](./abilities) 的型別）假設最壞的情況。

「約束 (Constraints)」提供了一種方式來指定這些未知型別具備哪些屬性，以便型別系統允許執行原本不安全的操作。

### 宣告約束

可以使用以下語法在型別參數上強加約束。

```move
// T 是型別參數的名稱
T: <ability> (+ <ability>)*
```

`<ability>` 可以是四種[能力 (abilities)](./abilities) 中的任何一種，且一個型別參數可以同時受多種能力的約束。因此，以下所有的型別參數宣告都是有效的：

```move
T: copy
T: copy + drop
T: copy + drop + store + key
```

### 驗證約束

約束是在實例化位置進行檢查的。

```move
public struct Foo<T: copy> { x: T }

public struct Bar { x: Foo<u8> }
//                         ^^ 有效，u8 具備 `copy`

public struct Baz<T> { x: Foo<T> }
//                            ^ 錯誤！T 不具備 'copy'
```

對於函式也是如此：

```move
fun unsafe_consume<T>(x: T) {
    // 錯誤！x 不具備 'drop'
}

fun consume<T: drop>(x: T) {
    // 有效，x 將會被自動丟棄
}

public struct NoAbilities {}

fun foo() {
    let r = NoAbilities {};
    consume<NoAbilities>(NoAbilities);
    //      ^^^^^^^^^^^ 錯誤！NoAbilities 不具備 'drop'
}
```

以及一些類似的關於 `copy` 的範例：

```move
fun unsafe_double<T>(x: T) {
    (copy x, x)
    // 錯誤！T 不具備 'copy'
}

fun double<T: copy>(x: T) {
    (copy x, x) // 有效，T 具備 'copy'
}

public struct NoAbilities {}

fun foo(): (NoAbilities, NoAbilities) {
    let r = NoAbilities {};
    double<NoAbilities>(r)
    //     ^ 錯誤！NoAbilities 不具備 'copy'
}
```

欲瞭解更多資訊，請參閱能力章節中有關[條件能力與泛型型別](./abilities#conditional-abilities-and-generic-types)的部分。

## 遞迴限制 (Limitations on Recursions)

### 遞迴結構體 (Recursive Structs)

泛型結構體不能直接或間接地包含相同型別的欄位，即便使用了不同的型別引數也一樣。以下所有的結構體定義都是無效的：

```move
public struct Foo<T> {
    x: Foo<u64> // 錯誤！'Foo' 包含 'Foo'
}

public struct Bar<T> {
    x: Bar<T> // 錯誤！'Bar' 包含 'Bar'
}

// 錯誤！'A' 和 'B' 形成迴圈，這也是不允許的。
public struct A<T> {
    x: B<T, u64>
}

public struct B<T1, T2> {
    x: A<T1>
    y: A<T2>
}
```

### 進階話題：型別層級遞迴 (Type-level Recursions)

Move 允許泛型函式進行遞迴呼叫。但是，當這與泛型結構體結合使用時，在某些情況下可能會產生無限數量的型別，而允許這種行為意味著會為編譯器、虛擬機 (VM) 和其他語言組件增加不必要的複雜性。因此，這種遞迴是被禁止的。

這項限制在未來可能會放寬，但目前以下範例應該能讓你了解哪些是允許的，哪些是不允許的。

```move
module a::m;

public struct A<T> {}

// 有限多個型別 —— 允許。
// foo<T> -> foo<T> -> foo<T> -> ... 是有效的
fun foo<T>() {
    foo<T>();
}

// 有限多個型別 —— 允許。
// foo<T> -> foo<A<u64>> -> foo<A<u64>> -> ... 是有效的
fun foo<T>() {
    foo<A<u64>>();
}
```

不允許的情況：

```move
module a::m;

public struct A<T> {}

// 無限多個型別 —— 不允許。
// 錯誤！
// foo<T> -> foo<A<T>> -> foo<A<A<T>>> -> ...
fun foo<T>() {
    foo<A<T>>();
}
```

同樣地，這也是不允許的：

```move
module a::n;

public struct A<T> {}

// 無限多個型別 —— 不允許。
// 錯誤！
// foo<T1, T2> -> bar<T2, T1> -> foo<T2, A<T1>>
//   -> bar<A<T1>, T2> -> foo<A<T1>, A<T2>>
//   -> bar<A<T2>, A<T1>> -> foo<A<T2>, A<A<T1>>>
//   -> ...
fun foo<T1, T2>() {
    bar<T2, T1>();
}

fun bar<T1, T2>() {
    foo<T1, A<T2>>();
}
```

請注意，型別層級遞迴的檢查是基於對呼叫點的保守分析，**不**考慮控制流或執行階段的數值。

```move
module a::m;

public struct A<T> {}

// 無限多個型別 —— 不允許。
// 錯誤！
fun foo<T>(n: u64) {
    if (n > 0) foo<A<T>>(n - 1);
}
```

上述範例中的函式在技術上會針對任何給定輸入而終止，因此僅會產生有限數量的型別，但它仍然被 Move 的型別系統視為無效。
