---
title: 泛型 (Generics) | 參考手冊
description: Move 泛型 (Move generics) 參考手冊：函式和結構的型別參數、限制、虛擬型別與參數化多型 (parametric polymorphism)。
keywords:
  - Move
  - Sui
  - Move reference
  - generics
  - reference
questions:
  - How does Generics work in Move?
  - What is the syntax for Generics in Move?
  - What is Declaring Type Parameters in Move?
  - What is Type Arguments in Move?
answer: 'Move generics reference: type parameters, constraints, phantom types, and parametric polymorphism for functions and structs.'
goal:
  description: 'Reader understands move generics reference: type parameters, constraints, phantom types, and parametric polymorphism for functions and structs'
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

# 泛型 (Generics) {#generics}

泛型可用於針對不同的輸入資料型別定義函式與結構體。這項語言功能有時稱為參數化多型。在 Move 中，我們經常將泛型與 *型別參數*及 *型別引數*交替使用。

泛型常用於函式庫原始碼中，例如 [vector](./primitive-types/vector)，用來宣告可適用於任何可能型別（且符合指定限制）的原始碼。這類參數化讓你能在多種型別與情境中重複使用相同的實作。

## 宣告型別參數 (Declaring Type Parameters) {#declaring-type-parameters}

函式與結構都可以在其簽章中接受一串以角括號 `<...>` 包住的型別參數。

### 泛型函式 (Generic Functions) {#generic-functions}

函式的型別參數會放在函式名稱之後、（值）參數清單之前。以下程式碼定義了一個泛型識別函式，該函式接受任意型別的值，並原樣回傳該值。

```move
fun id<T>(x: T): T {
    // 此型別註解並非必要，但有效
    (x: T)
}
```

定義後，型別參數 `T` 可用於參數型別、回傳型別，以及函式主體內部。

### 泛型結構 (Generic Structs) {#generic-structs}

結構的型別參數會放在結構名稱之後，並可用來命名欄位的型別。

```move
public struct Foo<T> has copy, drop { x: T }

public struct Bar<T1, T2> has copy, drop {
    x: T1,
    y: vector<T2>,
}
```

請注意，[不一定要使用型別參數](#unused-type-parameters)

## 型別引數 (Type Arguments) {#type-arguments}

### 呼叫泛型函式 (Calling Generic Functions) {#calling-generic-functions}

呼叫泛型函式時，可以在一對角括號所包圍的清單中，指定函式型別參數的型別引數。

```move
fun foo() {
    let x = id<bool>(true);
}
```

如果你未指定型別引數，Move 的[型別推斷](#type-inference)會為你提供它們。

### 使用泛型結構 (Using Generic Structs) {#using-generic-structs}

同樣地，建構或解構泛型型別的值時，可以附加結構型別參數的型別引數清單。

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

無論如何，如果你未指定型別引數，Move 的[型別推斷](#type-inference)都會為你提供它們。

### 型別引數不相符 (Type Argument Mismatch) {#type-argument-mismatch}

如果你指定的型別引數與實際提供的值衝突，將會產生錯誤：

```move
fun foo() {
    let x = id<u64>(true); // 錯誤！true 不是 u64
}
```

同樣地：

```move
fun foo() {
    let foo = Foo<bool> { x: 0 }; // 錯誤！0 不是 bool
    let Foo<address> { x } = foo; // 錯誤！bool 與 address 不相容
}
```

## 型別推斷 (Type Inference) {#type-inference}

在大多數情況下，Move 編譯器能夠推斷型別引數，因此你不必明確寫下它們。若省略型別引數，上述範例會如下所示：

```move
fun foo() {
    let x = id(true);
    //        ^ 已推斷 <bool>

    let foo = Foo { x: true };
    //           ^ 已推斷 <bool>

    let Foo { x } = foo;
    //     ^ 已推斷 <bool>
}
```

請注意：當編譯器無法推斷型別時，你必須手動加上型別註記。常見情境是呼叫型別參數只出現在回傳位置的函式。

```move
module a::m;

fun foo() {
    let v = vector[]; // 錯誤！
    //            ^ 編譯器無法判斷元素型別，因為它從未被使用

    let v = vector<u64>[];
    //            ^~~~~ 此情況必須手動加上型別註記。
}
```

請注意，這些情況有些刻意，因為 `vector[]` 從未被使用，因此 Move 的型別推斷無法推斷其型別。

不過，若該值稍後在函式中被使用，編譯器便能推斷其型別：

```move
module a::m;

fun foo() {
    let v = vector[];
    //            ^ 已推斷 <u64>
    vector::push_back(&mut v, 42);
    //               ^ 已推斷 <u64>
}
```

### 「_」型別 (`_` Type) {#_-type}

在某些情況下，你可能想明確註記部分型別引數，但讓編譯器推斷其他引數。`_` 型別可作為這類預留位置，讓編譯器推斷型別。

```move
let bar = Bar<u64, _> { x: 0, y: vector[b"hello"] };
//                 ^ 已推斷 vector<u8>
```

預留位置 `_` 僅可出現在運算式與巨集函式定義中，不能出現在簽章中。這表示你無法將 `_` 用於函式參數的定義、函式回傳型別、常數定義型別及資料型別欄位。

## 整數 (Integers) {#integers}

在 Move 中，整數型別 `u8`、`u16`、`u32`、`u64`、`u128` 與 `u256` 全都是相異的型別。
不過，這些型別都可以使用相同的數值語法建立。換句話說，若未提供型別後綴，編譯器會根據數值的使用方式推斷整數型別。

```move
let x8: u8 = 0;
let x16: u16 = 0;
let x32: u32 = 0;
let x64: u64 = 0;
let x128: u128 = 0;
let x256: u256 = 0;
```

若數值並未用於需要特定整數型別的內容中，預設會採用 `u64`。

```move
let x = 0;
//      ^ 預設使用 u64
```

不過，若數值對推斷出的型別而言過大，將會產生錯誤。

```move
let i: u8 = 256; // 錯誤！
//          ^^^ 對 u8 而言過大
let x = 340282366920938463463374607431768211454;
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 對 u64 而言過大
```

若數字過大，你可能需要明確標註其型別。

```move
let x = 340282366920938463463374607431768211454u128;
//                                             ^^^^ 有效！
```

## 未使用的型別參數 (Unused Type Parameters) {#unused-type-parameters}

對於結構定義，未使用的型別參數是指未出現在該結構中任何已定義欄位內，但會在編譯時進行靜態檢查的型別參數。Move 允許未使用的型別參數，因此以下結構定義有效：

```move
public struct Foo<T> {
    foo: u64
}
```

這在為某些概念建立模型時可能很方便。以下是一個範例：

```move
module a::m;

// 貨幣指定子
public struct A {}
public struct B {}

// 可使用貨幣指定子型別具現化的泛型 coin 型別。
//   例如：Coin<A>、Coin<B> 等。
public struct Coin<Currency> has store {
    value: u64
}

// 以泛型方式撰寫關於所有貨幣的程式碼
public fun mint_generic<Currency>(value: u64): Coin<Currency> {
    Coin { value }
}

// 以具體方式撰寫關於單一貨幣的程式碼
public fun mint_a(value: u64): Coin<A> {
    mint_generic(value)
}
public fun mint_b(value: u64): Coin<B> {
    mint_generic(value)
}
```

在此範例中，`Coin<Currency>` 會以 `Currency` 型別參數作為泛型，該參數指定 coin 的貨幣，並讓程式碼能以泛型方式處理任何貨幣，或以具體方式處理特定貨幣。即使 `Currency` 型別參數未出現在 `Coin` 中任何已定義的欄位內，這種通用性仍然適用。

### 幽靈型別參數 (Phantom Type Parameters) {#phantom-type-parameters}

在上述範例中，雖然 `struct Coin` 要求 `store` 能力，但 `Coin<A>` 與 `Coin<B>` 都不會具有 `store` 能力。這是因為[條件式能力與泛型型別](./abilities#conditional-abilities-and-generic-types)的規則，以及 `A` 和 `B` 沒有 `store` 能力；儘管它們甚至未在 `struct Coin` 的主體中使用。這可能造成一些不理想的後果。例如，我們無法將 `Coin<A>` 放入儲存空間中的錢包。

其中一個可行的解決方案是為 `A` 和 `B` 新增多餘的能力註記（亦即 `public struct Currency1 has store {}`）。但這可能導致錯誤或安全性弱點，因為它會透過不必要的能力宣告弱化型別。例如，我們絕不會預期儲存空間中的值具有型別為 `A` 的欄位，但多餘的 `store` 能力會使此情況成為可能。此外，這些多餘註記會具有擴散性，要求許多對未使用型別參數泛型化的函式也納入必要的約束。

幽靈型別參數可解決此問題。未使用的型別參數可標記為 _幽靈_ 型別參數，且不會參與結構體的能力推導。如此一來，在推導泛型型別的能力時，不會考量幽靈型別參數的引數，從而避免需要多餘的能力註記。為使這項寬鬆規則保持健全，Move 的型別系統保證宣告為 `phantom` 的參數，不是在結構體定義中完全未使用，就是僅作為同樣宣告為 `phantom` 的型別參數引數使用。

#### 宣告 (Declaration) {#declaration}

在結構體定義中，可在型別參數宣告之前新增 `phantom` 關鍵字，將其宣告為幽靈型別參數。

```move
public struct Coin<phantom Currency> has store {
    value: u64
}
```

若型別參數宣告為 phantom，我們稱其為幽靈型別參數。定義結構體時，Move 的型別檢查器會確保每個幽靈型別參數不是未在結構體定義內使用，就是僅作為幽靈型別參數的引數使用。

```move
public struct S1<phantom T1, T2> { f: u64 }
//               ^^^^^^^ 有效，T1 未出現在結構體定義內

public struct S2<phantom T1, T2> { f: S1<T1, T2> }
//               ^^^^^^^ 有效，T1 出現在幽靈位置
```

下列程式碼展示違反此規則的範例：

```move
public struct S1<phantom T> { f: T }
//               ^^^^^^^ 錯誤！  ^ 並非幽靈位置

public struct S2<T> { f: T }
public struct S3<phantom T> { f: S2<T> }
//               ^^^^^^^ 錯誤！     ^ 並非幽靈位置
```

更正式地說，若型別作為幽靈型別參數的引數使用，我們稱該型別出現在 _幽靈位置_。有了此定義後，幽靈參數正確使用方式的規則可指定如下：**幽靈型別參數只能出現在幽靈位置**。

請注意，無須指定 `phantom`，但如果型別參數可以是 `phantom` 卻未如此標記，編譯器將發出警告。

#### 具現化 (Instantiation) {#instantiation}

具現化結構體時，推導結構體能力會排除幽靈參數的引數。例如，請考量下列程式碼：

```move
public struct S<T1, phantom T2> has copy { f: T1 }
public struct NoCopy {}
public struct HasCopy has copy {}
```

現在考量型別 `S<HasCopy, NoCopy>`。由於 `S` 定義了 `copy`，且所有非幽靈引數都具有 `copy`，因此 `S<HasCopy, NoCopy>` 也具有 `copy`。

#### 具有能力約束的幽靈型別參數 (Phantom Type Parameters with Ability Constraints) {#phantom-type-parameters-with-ability-constraints}

能力約束與幽靈型別參數是正交功能，意即幽靈參數可透過能力約束宣告。

```move
public struct S<phantom T: copy> {}
```

以具有能力約束的幽靈型別參數進行具現化時，型別引數仍必須滿足該約束，即使該參數是幽靈參數亦然。一般限制仍然適用，且 `T` 只能以具有 `copy` 的引數具現化。

## 約束條件 (Constraints) {#constraints}

在上述範例中，我們展示了如何使用型別參數來定義可由呼叫端在稍後代入的「未知」型別。然而，這表示型別系統掌握的型別資訊很少，必須以非常保守的方式執行檢查。從某種意義上來說，型別系統必須針對未受約束的泛型假設最糟情境——也就是沒有任何 [能力](./abilities) 的型別。

約束條件可用來指定這些未知型別具備哪些特性，讓型別系統可以允許原本不安全的操作。

### 宣告約束條件 (Declaring Constraints) {#declaring-constraints}

可以使用下列語法對型別參數施加約束條件。

```move
// T 是型別參數的名稱
T: <ability> (+ <ability>)*
```

`<ability>` 可以是四種[能力](./abilities)中的任一種，且型別參數可以同時受多種能力約束。因此，下列所有型別參數宣告都有效：

```move
T: copy
T: copy + drop
T: copy + drop + store + key
```

### 驗證約束條件 (Verifying Constraints) {#verifying-constraints}

約束條件會在具現化位置檢查。

```move
public struct Foo<T: copy> { x: T }

public struct Bar { x: Foo<u8> }
//                         ^^ 有效，u8 具有 `copy`

public struct Baz<T> { x: Foo<T> }
//                            ^ 錯誤！T 沒有 'copy'
```

函式也是同樣的情況。

```move
fun unsafe_consume<T>(x: T) {
    // 錯誤！x 沒有 'drop'
}

fun consume<T: drop>(x: T) {
    // 有效，x 會自動被丟棄
}

public struct NoAbilities {}

fun foo() {
    let r = NoAbilities {};
    consume<NoAbilities>(NoAbilities);
    //      ^^^^^^^^^^^ 錯誤！NoAbilities 沒有 'drop'
}
```

還有一些類似的範例，但使用的是 `copy`。

```move
fun unsafe_double<T>(x: T) {
    (copy x, x)
    // 錯誤！T 沒有 'copy'
}

fun double<T: copy>(x: T) {
    (copy x, x) // 有效，T 具有 'copy'
}

public struct NoAbilities {}

fun foo(): (NoAbilities, NoAbilities) {
    let r = NoAbilities {};
    double<NoAbilities>(r)
    //     ^ 錯誤！NoAbilities 沒有 'copy'
}
```

如需更多資訊，請參閱能力章節中的
[條件式能力與泛型型別](./abilities#conditional-abilities-and-generic-types)。

## 遞迴的限制 (Limitations on Recursions) {#limitations-on-recursions}

### 遞迴結構 (Recursive Structs) {#recursive-structs}

泛型結構不能直接或間接包含相同型別的欄位，即使使用不同的型別引數也不行。以下所有結構宣告皆無效：

```move
public struct Foo<T> {
    x: Foo<u64> // 錯誤！'Foo' 包含 'Foo'
}

public struct Bar<T> {
    x: Bar<T> // 錯誤！'Bar' 包含 'Bar'
}

// 錯誤！'A' 與 'B' 形成迴圈，同樣不被允許。
public struct A<T> {
    x: B<T, u64>
}

public struct B<T1, T2> {
    x: A<T1>
    y: A<T2>
}
```

### 進階主題：型別層級遞迴 (Advanced Topic: Type-level Recursions) {#advanced-topic-type-level-recursions}

Move 允許遞迴呼叫泛型函式。不過，與泛型結構結合使用時，這在某些情況下可能建立無限多種型別；允許這麼做會為編譯器、VM 與其他語言元件增加不必要的複雜性。因此，禁止此類遞迴。

未來可能會放寬這項限制，但目前以下範例應能讓你了解哪些做法被允許、哪些不被允許。

```move
module a::m;

public struct A<T> {}

// 有限種型別 -- 允許。
// foo<T> -> foo<T> -> foo<T> -> ... 有效
fun foo<T>() {
    foo<T>();
}

// 有限種型別 -- 允許。
// foo<T> -> foo<A<u64>> -> foo<A<u64>> -> ... 有效
fun foo<T>() {
    foo<A<u64>>();
}
```

不被允許：

```move
module a::m;

public struct A<T> {}

// 無限多種型別 -- 不允許。
// 錯誤！
// foo<T> -> foo<A<T>> -> foo<A<A<T>>> -> ...
fun foo<T>() {
    foo<Foo<T>>();
}
```

同樣地，以下做法也不被允許：

```move
module a::n;

public struct A<T> {}

// 無限多種型別 -- 不允許。
// 錯誤！
// foo<T1, T2> -> bar<T2, T1> -> foo<T2, A<T1>>
//   -> bar<A<T1>, T2> -> foo<A<T1>, A<T2>>
//   -> bar<A<T2>, A<T1>> -> foo<A<T2>, A<A<T1>>>
//   -> ...
fun foo<T1, T2>() {
    bar<T2, T1>();
}

fun bar<T1, T2> {
    foo<T1, A<T2>>();
}
```

請注意，型別層級遞迴的檢查是根據對呼叫位置的保守分析，且不會將控制流程或執行階段值納入考量。

```move
module a::m;

public struct A<T> {}

// 無限多種型別 -- 不允許。
// 錯誤！
fun foo<T>(n: u64) {
    if (n > 0) foo<A<T>>(n - 1);
}
```

上述範例中的函式在技術上會針對任何給定輸入中止，因此只會建立有限多種型別；但 Move 的型別系統仍將其視為無效。
