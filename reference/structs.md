---
title: 結構 (Structs) | 參考手冊
description: Move 結構參考：定義自訂型別、位置與具名欄位、能力、可見性及資源語意。
keywords:
  - Move
  - Sui
  - Move reference
  - structs
  - reference
  - struct
questions:
  - How does Structs work in Move?
  - What is the syntax for Structs in Move?
  - What is Defining Structs in Move?
  - What is Using Structs in Move?
answer: 'Move structs reference: define custom types, positional and named fields, abilities, visibility, and resource semantics.'
goal:
  description: 'Reader understands move structs reference: define custom types, positional and named fields, abilities, visibility, and resource semantics'
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

# 結構與資源 (Structs and Resources) {#structs-and-resources}

*結構*是一種使用者定義的資料結構，包含具型別的欄位。結構可以儲存任何非參考、非元組型別，包括其他結構。

結構可用來定義所有「資產」值或不受限制的值，並可控制對這些值執行的操作，這是透過結構的[能力](./abilities)達成。預設情況下，結構是線性且暫時性的。這表示它們無法被複製、無法被丟棄，也無法儲存於儲存空間中。這意味著所有值都必須轉移其所有權（線性），且必須在程式執行結束前處理這些值（暫時性）。我們可以藉由賦予結構[能力](./abilities)來放寬此行為，讓值能夠被複製或丟棄，也能儲存於儲存空間中或定義儲存架構。

## 定義結構 (Defining Structs) {#defining-structs}

結構必須在模組內定義，且結構的欄位可以是具名或位置式：

```move
module a::m;

public struct Foo { x: u64, y: bool }
public struct Bar {}
public struct Baz { foo: Foo, }
//                          ^ 註解：結尾可以有逗號

public struct PosFoo(u64, bool)
public struct PosBar()
public struct PosBaz(Foo)
```

結構不可遞迴，因此下列定義無效：

```move
public struct Foo { x: Foo }
//                     ^ 錯誤！遞迴定義

public struct A { b: B }
public struct B { a: A }
//                   ^ 錯誤！遞迴定義

public struct D(D)
//              ^ 錯誤！遞迴定義
```

### 可見性 (Visibility) {#visibility}

如你可能已注意到，所有結構都宣告為 `public`。這表示結構的型別可以從任何其他模組參考。不過，結構的欄位，以及建立或銷毀結構的能力，仍限於定義該結構的模組內部。

未來，我們預計會新增將結構宣告為 `public(package)` 或內部結構的功能，類似於[函式](./functions#visibility)。

### 能力 (Abilities) {#abilities}

如上所述：預設情況下，結構宣告是線性且暫時的。因此，若要允許值以這些方式使用（例如複製、丟棄、儲存於[物件](./abilities/object)，或用於定義可儲存的[物件](./abilities/object)），可以透過以 `has <ability>` 加上註記，為結構授予[能力](./abilities)：

```move
module a::m {
    public struct Foo has copy, drop { x: u64, y: bool }
}
```

能力宣告可以位於結構欄位之前或之後。不過，兩者只能擇一使用，不可同時使用。若在結構欄位之後宣告，能力宣告必須以分號結尾：

```move
module a::m;

public struct PreNamedAbilities has copy, drop { x: u64, y: bool }
public struct PostNamedAbilities { x: u64, y: bool } has copy, drop;
public struct PostNamedAbilitiesInvalid { x: u64, y: bool } has copy, drop
//                                                                        ^ 錯誤！缺少分號

public struct NamedInvalidAbilities has copy { x: u64, y: bool } has drop;
//                                                               ^ 錯誤！重複的能力宣告

public struct PrePositionalAbilities has copy, drop (u64, bool)
public struct PostPositionalAbilities (u64, bool) has copy, drop;
public struct PostPositionalAbilitiesInvalid (u64, bool) has copy, drop
//                                                                     ^ 錯誤！缺少分號
public struct InvalidAbilities has copy (u64, bool) has drop;
//                                                  ^ 錯誤！重複的能力宣告
```

如需更多詳細資料，請參閱[為結構與列舉加上能力註記](./abilities#annotating-structs-and-enums)章節。

### 命名 (Naming) {#naming}

結構必須以大寫字母 `A` 至 `Z` 開頭。第一個字母之後，結構名稱可以包含底線 `_`、字母 `a` 至 `z`、字母 `A` 至 `Z`，或數字 `0` 至 `9`。

```move
public struct Foo {}
public struct BAR {}
public struct B_a_z_4_2 {}
public struct P_o_s_Foo()
```

要求以 `A` 至 `Z` 開頭的命名限制，是為了替未來的語言功能保留空間。之後可能會移除，也可能不會。

## 使用結構 (Using Structs) {#using-structs}

### 建立結構 (Creating Structs) {#creating-structs}

可以透過指定結構名稱，接著為每個欄位提供值，來建立（或「封裝」）結構型別的值。

對於具有具名欄位的結構，欄位順序並不重要，但必須提供欄位名稱。對於具有位置欄位的結構，欄位順序必須符合結構定義中的欄位順序，而且必須使用 `()` 而非 `{}` 來包住參數。

```move
module a::m;

public struct Foo has drop { x: u64, y: bool }
public struct Baz has drop { foo: Foo }
public struct Positional(u64, bool) has drop;

fun example() {
    let foo = Foo { x: 0, y: false };
    let baz = Baz { foo: foo };
    // 注意：位置結構值使用圓括號建立，並且
    // 依據位置而非名稱。
    let pos = Positional(0, false);
    let pos_invalid = Positional(false, 0);
    //                           ^ 錯誤！欄位順序錯誤，且型別不相符。
}
```

對於具有具名欄位的結構，如果你有與欄位同名的區域變數，可以使用下列簡寫：

```move
let baz = Baz { foo: foo };
// 等同於
let baz = Baz { foo };
```

這有時稱為「欄位名稱雙關」。

### 透過模式比對銷毀結構 (Destroying Structs via Pattern Matching) {#destroying-structs-via-pattern-matching}

結構值可以使用與建立它們相似的語法，透過在模式中繫結或指派來銷毀。

```move
module a::m;

public struct Foo { x: u64, y: bool }
public struct Bar(Foo)
public struct Baz {}
public struct Qux()

fun example_destroy_foo() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y: foo_y } = foo;
    //        ^ `x: x` 的簡寫

    // 兩個新的繫結
    //   x: u64 = 3
    //   foo_y: bool = false
}

fun example_destroy_foo_wildcard() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y: _ } = foo;

    // 因為 y 已繫結至萬用字元，所以只有一個新的繫結
    //   x: u64 = 3
}

fun example_destroy_foo_assignment() {
    let x: u64;
    let y: bool;
    Foo { x, y } = Foo { x: 3, y: false };

    // 變更既有變數 x 和 y
    //   x = 3, y = false
}

fun example_foo_ref() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &foo;

    // 兩個新的繫結
    //   x: &u64
    //   y: &bool
}

fun example_foo_ref_mut() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &mut foo;

    // 兩個新的繫結
    //   x: &mut u64
    //   y: &mut bool
}

fun example_destroy_bar() {
    let bar = Bar(Foo { x: 3, y: false });
    let Bar(Foo { x, y }) = bar;
    //            ^ 巢狀模式

    // 兩個新的繫結
    //   x: u64 = 3
    //   y: bool = false
}

fun example_destroy_baz() {
    let baz = Baz {};
    let Baz {} = baz;
}

fun example_destroy_qux() {
    let qux = Qux();
    let Qux() = qux;
}
```

### 存取結構欄位 (Accessing Struct Fields) {#accessing-struct-fields}

可以使用點運算子 `.` 存取結構的欄位。

對於具有具名欄位的結構，可以透過欄位名稱來存取欄位：

```move
public struct Foo { x: u64, y: bool }
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

對於位置結構，可以透過欄位在結構定義中的位置來存取欄位：

```move
public struct PosFoo(u64, bool)
let pos_foo = PosFoo(3, true);
let x = pos_foo.0;  // x == 3
let y = pos_foo.1;  // y == true
```

在未借用或複製結構欄位的情況下存取欄位，必須遵守該欄位的能力限制。如需更多詳細資料，請參閱
[借用結構與欄位](#borrowing-structs-and-fields)及
[讀取與寫入欄位](#reading-and-writing-fields)章節。

### 借用結構與欄位 (Borrowing Structs and Fields) {#borrowing-structs-and-fields}

`&` 與 `&mut` 運算子可用來建立結構或欄位的參考。以下範例
包含一些選用的型別註記（例如 `: &Foo`），以示範運算的型別。

```move
let foo = Foo { x: 3, y: true };
let foo_ref: &Foo = &foo;
let y: bool = foo_ref.y;         // 透過結構的參考讀取欄位
let x_ref: &u64 = &foo.x;        // 透過擴展結構的參考來借用欄位

let x_ref_mut: &mut u64 = &mut foo.x;
*x_ref_mut = 42;            // 透過可變參考修改欄位
```

可以借用巢狀結構的內部欄位：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);

let x_ref = &bar.0.x;
```

你也可以透過結構的參考借用欄位：

```move
let foo = Foo { x: 3, y: true };
let foo_ref = &foo;
let x_ref = &foo_ref.x;
// 此效果與 let x_ref = &foo.x 相同
```

### 讀取與寫入欄位 (Reading and Writing Fields) {#reading-and-writing-fields}

如果你需要讀取並複製欄位的值，接著可以對借用的欄位進行解參考：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(copy foo);
let x: u64 = *&foo.x;
let y: bool = *&foo.y;
let foo2: Foo = *&bar.0;
```

更標準的做法是，可以使用點運算子讀取結構的欄位，而不需要任何借用。如同
[解參考](./primitive-types/references#reading-and-writing-through-references)的情況，欄位
型別必須具有 `copy` [能力](./abilities)。

```move
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

點運算子可以串接以存取巢狀欄位：

```move
let bar = Bar(Foo { x: 3, y: true });
let x = baz.0.x; // x = 3;
```

不過，對於包含非基本型別的欄位，例如 vector 或另一個結構，則不允許這麼做：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);
let foo2: Foo = *&bar.0;
let foo3: Foo = bar.0; // 錯誤！必須使用 *& 明確加入 copy
```

我們可以可變地借用結構的欄位，為其指派新值：

```move
let mut foo = Foo { x: 3, y: true };
*&mut foo.x = 42;     // foo = Foo { x: 42, y: true }
*&mut foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);               // bar = Bar(Foo { x: 42, y: false })
*&mut bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
*&mut bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

與解參考類似，我們也可以直接使用點運算子修改欄位。在這兩種情況下，欄位型別都必須具有 `drop` [能力](./abilities)。

```move
let mut foo = Foo { x: 3, y: true };
foo.x = 42;     // foo = Foo { x: 42, y: true }
foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);         // bar = Bar(Foo { x: 42, y: false })
bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

用於指派的點語法也可透過結構的參考運作：

```move
let mut foo = Foo { x: 3, y: true };
let foo_ref = &mut foo;
foo_ref.x = foo_ref.x + 1;
```

## 受限的結構操作 (Privileged Struct Operations) {#privileged-struct-operations}

結構型別 `T` 上的大多數結構操作只能在宣告 `T` 的模組內執行：

- 結構型別只能在定義該結構的模組內建立（「封裝」）及銷毀（「解構」）。
- 結構的欄位只能在定義該結構的模組內存取。

依循這些規則，若你想在模組外修改你的結構，就必須為它們提供公開 API。本章末尾包含一些相關範例。

不過，如同[上方可見性章節](#visibility)所述，結構*型別*對其他模組一律可見。

```move
module a::m {
    public struct Foo has drop { x: u64 }

    public fun new_foo(): Foo {
        Foo { x: 42 }
    }
}

module a::n {
    use a::m::Foo;

    public struct Wrapper has drop {
        foo: Foo
        //   ^ 有效，型別為公開

    }

    fun f1(foo: Foo) {
        let x = foo.x;
        //      ^ 錯誤！無法在 `a::m` 外存取 `Foo` 的欄位
    }

    fun f2() {
        let foo_wrapper = Wrapper { foo: a::m::new_foo() };
        //                               ^ 有效，函式為公開
    }
}

```

## 所有權 (Ownership) {#ownership}

如同在 [定義結構 (Defining Structs)](#defining-structs) 中所述，結構預設為線性且
暫時性的。這表示它們無法被複製或丟棄。當對真實世界的資產（例如金錢）建模時，此特性非常實用，因為你不希望金錢在流通中被重複或遺失。

```move
module a::m;

public struct Foo { x: u64 }

public fun copying() {
    let foo = Foo { x: 100 };
    let foo_copy = copy foo; // 錯誤！複製需要 `copy` 能力
    let foo_ref = &foo;
    let another_copy = *foo_ref // 錯誤！解參考需要 `copy` 能力
}

public fun destroying_1() {
    let foo = Foo { x: 100 };

    // 錯誤！當函式回傳時，foo 仍包含一個值。
    // 此銷毀作業需要 `drop` 能力
}

public fun destroying_2(f: &mut Foo) {
    *f = Foo { x: 100 } // 錯誤！
                        // 透過寫入銷毀舊值需要 `drop` 能力
}
```

若要修正範例 `fun destroying_1`，你需要手動「解構」該值：

```move
module a::m;

public struct Foo { x: u64 }

public fun destroying_1_fixed() {
    let foo = Foo { x: 100 };
    let Foo { x: _ } = foo;
}
```

請記住，你只能在結構定義所在的模組內解構結構。此限制可用來在系統中強制維持特定的不變條件，例如金錢守恆。

另一方面，如果你的結構並不代表有價值的事物，你可以加入
`copy` 與 `drop` 能力，以取得在其他程式語言中可能更為熟悉的結構值：

```move
module a::m;

public struct Foo has copy, drop { x: u64 }

public fun run() {
    let foo = Foo { x: 100 };
    let foo_copy = foo;
    //             ^ 此程式碼會複製 foo，
    //             而 `let x = move foo` 則會移動 foo

    let x = foo.x;            // x = 100
    let x_copy = foo_copy.x;  // x = 100

    // 當函式回傳時，foo 與 foo_copy 都會被隱式丟棄
}
```

## 儲存 (Storage) {#storage}

結構可用於定義儲存結構描述，但細節會因 Move 的部署方式而異。
如需更多詳細資訊，請參閱 [`key` ability](./abilities#key) 與
[Sui 物件](./abilities/object) 的文件。
