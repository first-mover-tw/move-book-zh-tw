---
title: '結構體 (Structs) | 參考手冊'
description: "Move 結構體參考手冊：定義自定義類型、位置欄位與命名欄位、能力 (abilities)、可見性 (visibility) 以及資源語義 (resource semantics)。"
---

# 結構體與資源 (Structs and Resources)

「結構體 (struct)」是使用者定義的資料結構，包含具類型的欄位。結構體可以存儲任何非引用、非元組 (non-tuple) 類型，包括其他結構體。

結構體可用於定義所有的「資產 (asset)」數值或不受限的數值，其中對這些數值執行的操作可以受結構體的 [能力 (abilities)](./abilities) 控制。預設情況下，結構體是線性 (linear) 且短暫 (ephemeral) 的。我們的意思是，它們：不能被複製，不能被丟棄，也不能存儲在存儲中。這意味著所有數值都必須進行所有權轉移（線性），且數值必須在程式執行結束前處理完畢（短暫）。我們可以透過賦予結構體 [能力 (abilities)](./abilities) 來放寬這種行為，這允許數值被複製或丟棄，並允許存儲在存儲中或定義存儲架構 (storage schemas)。

## 定義結構體 {#defining-structs}

結構體必須定義在模組內部，其欄位可以是命名欄位 (named fields) 或位置欄位 (positional fields)：

```move
module a::m;

public struct Foo { x: u64, y: bool }
public struct Bar {}
public struct Baz { foo: Foo, }
//                          ^ 注意：可以使用尾隨逗號

public struct PosFoo(u64, bool)
public struct PosBar()
public struct PosBaz(Foo)
```

結構體不能是遞歸的，因此以下定義是無效的：

```move
public struct Foo { x: Foo }
//                     ^ 錯誤！遞歸定義

public struct A { b: B }
public struct B { a: A }
//                   ^ 錯誤！遞歸定義

public struct D(D)
//              ^ 錯誤！遞歸定義
```

### 可見性 (Visibility) {#visibility}

你可能已經注意到，所有結構體都被宣告為 `public`。這意味著該結構體的類型可以從任何其他模組引用。然而，結構體的欄位，以及建立或銷毀結構體的能力，仍然是定義該結構體的模組所私有的。

在未來，我們計畫增加宣告結構體為 `public(package)` 或內部 (internal) 的功能，就像 [函式 (functions)](./functions#visibility) 一樣。

### 能力 (Abilities)

如上所述：預設情況下，結構體宣告是線性且短暫的。為了允許數值以這些方式使用（例如，複製、丟棄、存儲在 [物件 (object)](./abilities/object) 中，或用於定義可存儲的 [物件 (object)](./abilities/object)），可以透過使用 `has <ability>` 標記結構體來賦予其 [能力 (abilities)](./abilities)：

```move
module a::m {
    public struct Foo has copy, drop { x: u64, y: bool }
}
```

能力宣告可以出現在結構體欄位之前或之後。但是，兩者只能擇其一，不能同時使用。如果宣告在欄位之後，能力宣告必須以分號結尾：

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

更多細節請參閱[標記結構體的能力](./abilities#annotating-structs-and-enums)章節。

### 命名 (Naming)

結構體名稱必須以大寫字母 `A` 到 `Z` 開頭。第一個字母之後，結構體名稱可以包含底線 `_`、小寫字母 `a` 到 `z`、大寫字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
public struct Foo {}
public struct BAR {}
public struct B_a_z_4_2 {}
public struct P_o_s_Foo()
```

这种以 `A` 到 `Z` 開頭的命名限制是為了給未來的語言特性留出空間。以後可能會也可能不會移除此限制。

## 使用結構體

### 建立結構體

可以透過指定結構體名稱，後跟每個欄位的數值來建立（或稱為「打包 pack」）結構體類型的數值。

對於具有命名欄位的結構體，欄位的順序並不重要，但需要提供欄位名稱。對於具有位置欄位的結構體，欄位的順序必須與結構體定義中的欄位順序匹配，且必須使用 `()` 而非 `{}` 來括住參數。

```move
module a::m;

public struct Foo has drop { x: u64, y: bool }
public struct Baz has drop { foo: Foo }
public struct Positional(u64, bool) has drop;

fun example() {
    let foo = Foo { x: 0, y: false };
    let baz = Baz { foo: foo };
    // 注意：位置結構體數值使用圓括號建立，
    // 並且是基於位置而非名稱。
    let pos = Positional(0, false);
    let pos_invalid = Positional(false, 0);
    //                           ^ 錯誤！欄位順序錯誤且類型不匹配。
}
```

對於具有命名欄位的結構體，如果本地變數的名稱與欄位名稱相同，可以使用以下簡寫：

```move
let baz = Baz { foo: foo };
// 等同於
let baz = Baz { foo };
```

這有時被稱為「欄位名稱雙關 (field name punning)」。

### 透過模式匹配銷毀結構體

結構體數值可以透過使用與構造它們類似的語法在模式 (patterns) 中綁定或賦值來銷毀。

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

    // 兩個新的綁定
    //   x: u64 = 3
    //   foo_y: bool = false
}

fun example_destroy_foo_wildcard() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y: _ } = foo;

    // 由於 y 綁定到萬用字元 (wildcard)，因此只有一個新的綁定
    //   x: u64 = 3
}

fun example_destroy_foo_assignment() {
    let x: u64;
    let y: bool;
    Foo { x, y } = Foo { x: 3, y: false };

    // 修改現有的變數 x 和 y
    //   x = 3, y = false
}

fun example_foo_ref() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &foo;

    // 兩個新的綁定
    //   x: &u64
    //   y: &bool
}

fun example_foo_ref_mut() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &mut foo;

    // 兩個新的綁定
    //   x: &mut u64
    //   y: &mut bool
}

fun example_destroy_bar() {
    let bar = Bar(Foo { x: 3, y: false });
    let Bar(Foo { x, y }) = bar;
    //            ^ 巢狀模式 (nested pattern)

    // 兩個新的綁定
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

### 存取結構體欄位

可以使用點運算子 `.` 來存取結構體的欄位。

對於具有命名欄位的結構體，可以透過欄位名稱存取欄位：

```move
public struct Foo { x: u64, y: bool }
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

對於位置結構體，可以透過欄位在結構體定義中的位置來存取欄位：

```move
public struct PosFoo(u64, bool)
let pos_foo = PosFoo(3, true);
let x = pos_foo.0;  // x == 3
let y = pos_foo.1;  // y == true
```

在不借用或複製的情況下存取結構體欄位會受到欄位能力約束的限制。更多細節請參閱[借用結構體與欄位](#borrowing-structs-and-fields)以及[讀取與寫入欄位](#reading-and-writing-fields)章節。

### 借用結構體與欄位 {#borrowing-structs-and-fields}

`&` 和 `&mut` 運算子可用於建立對結構體或欄位的引用。這些範例包含了一些可選的類型標籤（例如 `: &Foo`）來演示操作類型。

```move
let foo = Foo { x: 3, y: true };
let foo_ref: &Foo = &foo;
let y: bool = foo_ref.y;         // 透過對結構體的引用讀取欄位
let x_ref: &u64 = &foo.x;        // 透過擴展對結構體的引用來借用欄位

let x_ref_mut: &mut u64 = &mut foo.x;
*x_ref_mut = 42;            // 透過可變引用修改欄位
```

可以借用巢狀結構體的內部欄位：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);

let x_ref = &bar.0.x;
```

你也可以透過對結構體的引用來借用欄位：

```move
let foo = Foo { x: 3, y: true };
let foo_ref = &foo;
let x_ref = &foo_ref.x;
// 這與 let x_ref = &foo.x 效果相同
```

### 讀取與寫入欄位 {#reading-and-writing-fields}

如果你需要讀取並複製欄位的值，可以對借用的欄位進行解引用 (dereference)：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(copy foo);
let x: u64 = *&foo.x;
let y: bool = *&foo.y;
let foo2: Foo = *&bar.0;
```

更規範的做法是，點運算子可用於在不進行任何借用的情況下讀取結構體的欄位。與[解引用](./primitive-types/references#reading-and-writing-through-references)一樣，欄位類型必須具備 `copy` [能力 (ability)](./abilities)。

```move
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

點運算子可以鏈式使用以存取巢狀欄位：

```move
let bar = Bar(Foo { x: 3, y: true });
let x = baz.0.x; // x = 3;
```

但是，對於包含非原始類型（例如向量或其他結構體）的欄位，這是不允許的：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);
let foo2: Foo = *&bar.0;
let foo3: Foo = bar.0; // 錯誤！必須使用 *& 進行顯式複製
```

我們可以透過可變借用結構體的欄位來為其分配新值：

```move
let mut foo = Foo { x: 3, y: true };
*&mut foo.x = 42;     // foo = Foo { x: 42, y: true }
*&mut foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);               // bar = Bar(Foo { x: 42, y: false })
*&mut bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
*&mut bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

與解引用類似，我們可以改為直接使用點運算子來修改欄位。在這種情況下，欄位類型必須具備 `drop` [能力 (ability)](./abilities)。

```move
let mut foo = Foo { x: 3, y: true };
foo.x = 42;     // foo = Foo { x: 42, y: true }
foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);         // bar = Bar(Foo { x: 42, y: false })
bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

點語法用於賦值也適用於透過結構體的引用：

```move
let mut foo = Foo { x: 3, y: true };
let foo_ref = &mut foo;
foo_ref.x = foo_ref.x + 1;
```

## 特權結構體操作 (Privileged Struct Operations)

對結構體類型 `T` 的大多數操作只能在宣告 `T` 的模組內部執行：

- 結構體類型只能在定義結構體的模組內部建立（「打包 pack」）和銷毀（「拆解 unpack」）。
- 結構體的欄位僅在定義該結構體的模組內部可存取。

遵循這些規則，如果你想在模組外部修改你的結構體，你需要為它們提供公共 API。本章末尾包含一些相關範例。

然而，正如[上述可見性部分](#visibility)所述，結構體「類型」始終對其他模組可見。

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
        //   ^ 有效，該類型是公開的
    }

    fun f1(foo: Foo) {
        let x = foo.x;
        //      ^ 錯誤！不能在 `a::m` 之外存取 `Foo` 的欄位
    }

    fun f2() {
        let foo_wrapper = Wrapper { foo: a::m::new_foo() };
        //                               ^ 有效，該函式是公開的
    }
}
```

## 所有權 (Ownership)

如[定義結構體](#defining-structs)中所述，結構體預設是線性且短暫的。這意味著它們不能被複製或丟棄。當建模像金錢這樣的現實世界資產時，這個屬性非常有用，因為你不希望金錢被複製或是莫名消失。

```move
module a::m;

public struct Foo { x: u64 }

public fun copying() {
    let foo = Foo { x: 100 };
    let foo_copy = copy foo; // 錯誤！使用 'copy' 需要具備 'copy' 能力
    let foo_ref = &foo;
    let another_copy = *foo_ref // 錯誤！解引用需要具備 'copy' 能力
}

public fun destroying_1() {
    let foo = Foo { x: 100 };

    // 錯誤！當函式回傳時，foo 仍包含一個值。
    // 這類銷毀需要具備 'drop' 能力
}

public fun destroying_2(f: &mut Foo) {
    *f = Foo { x: 100 } // 錯誤！透過寫入銷毀舊值需要具備 'drop' 能力
}
```

要修正 `fun destroying_1` 範例，你需要手動「拆解」該數值：

```move
module a::m;

public struct Foo { x: u64 }

public fun destroying_1_fixed() {
    let foo = Foo { x: 100 };
    let Foo { x: _ } = foo;
}
```

回想一下，你只能在定義結構體的模組內解構結構體。這可以用來強制執行系統中的某些不變量，例如金錢守恆。

另一方面，如果你的結構體不代表具有價值的東西，你可以添加 `copy` 和 `drop` 能力，以獲得與其他程式語言更相似的結構體數值：

```move
module a::m;

public struct Foo has copy, drop { x: u64 }

public fun run() {
    let foo = Foo { x: 100 };
    let foo_copy = foo;
    //             ^ 此程式碼複製了 foo，
    //             而 `let x = move foo` 則會移動 foo

    let x = foo.x;            // x = 100
    let x_copy = foo_copy.x;  // x = 100

    // 當函式回傳時，foo 和 foo_copy 都會被隱式丟棄
}
```

## 存儲 (Storage)

結構體可以用來定義存儲架構，但具體細節因 Move 的部署而異。詳情請參閱 [`key` 能力](./abilities#key) 與 [Sui 物件](./abilities/object) 的文件。
