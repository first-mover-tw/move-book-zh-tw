---
title: 結構體 (Structs) | 參考手冊
description: Move struct 參考手冊：定義自訂型別 (type)、位置與具名欄位、能力 (ability)、可見性 (visibility) 與資源語意 (resource semantics)。
---

# 結構體與資源 (Structs and Resources)

_結構體 (struct)_ 是包含具型別欄位的使用者定義資料結構。結構體可以儲存任何非參考、非元組型別，包括其他結構體。

結構體可以用於定義所有「資產 (asset)」值或不受限制的值，對這些執行所執行的操作可以由結構體的[能力 (abilities)](./abilities) 來控制。預設情況下，結構體是線性的 (linear) 且短暫的 (ephemeral)。所謂線性且短暫，我們的意思是它們：不能被複製、不能被捨棄 (dropped)，且不能儲存在儲存空間中。這意味著所有值都必須轉移所有權（線性），且必須在程式執行結束前處理完畢（短暫）。我們可以透過給予結構體[能力 (abilities)](./abilities) 來放寬這種行為，這些能力允許值被複製或捨棄，也可以儲存在儲存空間中，或用於定義儲存架構 (storage schemas)。

## 定義結構體 (Defining Structs) {#defining-structs}

結構體必須在模組內定義，結構體的欄位可以是具名的或按位置排列的：

```move
module a::m;

public struct Foo { x: u64, y: bool }
public struct Bar {}
public struct Baz { foo: Foo, }
//                          ^ 注意：允許有結尾逗號
public struct PosFoo(u64, bool)
public struct PosBar()
public struct PosBaz(Foo)
```

結構體不能是遞迴的，因此以下定義是無效的：

```move
public struct Foo { x: Foo }
//                     ^ 錯誤！遞迴定義

public struct A { b: B }
public struct B { a: A }
//                   ^ 錯誤！遞迴定義

public struct D(D)
//              ^ 錯誤！遞迴定義
```

### 能見度 (Visibility) {#visibility}

你可能已經注意到，所有結構體都被宣告為 `public`。這意味著結構體的型別可以在任何其他模組中被參考。然而，結構體的欄位，以及建立或銷毀結構體的能力，仍然在定義該結構體的模組內部。

在未來，我們計畫增加將結構體宣告為 `public(package)` 或內部的功能，就像[函式](./functions#visibility)一樣。

### 能力 (Abilities)

如上所述：預設情況下，結構體宣告是線性的且短暫的。因此，要允許值以這些方式使用（例如，複製、捨棄、儲存在[物件 (object)](./abilities/object) 中，或用於定義可儲存的[物件 (object)](./abilities/object)），可以透過使用 `has <ability>` 標記結構體來賦予其[能力 (abilities)](./abilities)：

```move
module a::m {
    public struct Foo has copy, drop { x: u64, y: bool }
}
```

能力宣告可以出現在結構體欄位之前或之後。但是，只能選擇其中一種，不能同時使用。如果宣告在結構體欄位之後，能力宣告必須以分號結尾：

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

欲了解更多詳情，請參見[標記結構體和列舉的能力](./abilities#annotating-structs-and-enums)章節。

### 命名 (Naming)

結構體名稱必須以大寫字母 `A` 到 `Z` 開頭。第一個字母之後，結構體名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
public struct Foo {}
public struct BAR {}
public struct B_a_z_4_2 {}
public struct P_o_s_Foo()
```

這種以 `A` 到 `Z` 開頭的命名限制是為了給未來的語言特性留出空間。未來可能會、也可能不會移除這項限制。

## 使用結構體 (Using Structs)

### 建立結構體 (Creating Structs)

結構體型別的實例可以透過指定結構體名稱，後跟每個欄位的值來建立（或「封裝 pack」）。

對於具有具名欄位的結構體，欄位的順序並不重要，但需要提供欄位名稱。對於具有位置欄位的結構體，欄位的順序必須與結構體定義中的順序相符，且必須使用 `()` 而非 `{}` 來包圍參數。

```move
module a::m;

public struct Foo has drop { x: u64, y: bool }
public struct Baz has drop { foo: Foo }
public struct Positional(u64, bool) has drop;

fun example() {
    let foo = Foo { x: 0, y: false };
    let baz = Baz { foo: foo };
    // 注意：位置結構體值是使用圓括號建立的，
    // 且基於位置而非名稱。
    let pos = Positional(0, false);
    let pos_invalid = Positional(false, 0);
    //                           ^ 錯誤！欄位順序錯誤且型別不符。
}
```

對於具有具名欄位的結構體，如果你有一個與欄位名稱相同的區域變數，可以使用以下縮寫：

```move
let baz = Baz { foo: foo };
// 等同於
let baz = Baz { foo };
```

這有時被稱為「欄位名稱雙關 (field name punning)」。

### 透過模式匹配銷毀結構體 (Destroying Structs via Pattern Matching)

結構體值可以透過在模式中綁定或賦值來銷毀，語法與構造它們類似。

```move
module a::m;

public struct Foo { x: u64, y: bool }
public struct Bar(Foo)
public struct Baz {}
public struct Qux()

fun example_destroy_foo() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y: foo_y } = foo;
    //        ^ `x: x` 的縮寫

    // 兩個新綁定
    //   x: u64 = 3
    //   foo_y: bool = false
}

fun example_destroy_foo_wildcard() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y: _ } = foo;

    // 只有一個新綁定，因為 y 被綁定到了通配符 (wildcard)
    //   x: u64 = 3
}

fun example_destroy_foo_assignment() {
    let x: u64;
    let y: bool;
    Foo { x, y } = Foo { x: 3, y: false };

    // 修改現有變數 x 和 y
    //   x = 3, y = false
}

fun example_foo_ref() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &foo;

    // 兩個新綁定
    //   x: &u64
    //   y: &bool
}

fun example_foo_ref_mut() {
    let foo = Foo { x: 3, y: false };
    let Foo { x, y } = &mut foo;

    // 兩個新綁定
    //   x: &mut u64
    //   y: &mut bool
}

fun example_destroy_bar() {
    let bar = Bar(Foo { x: 3, y: false });
    let Bar(Foo { x, y }) = bar;
    //            ^ 巢狀模式

    // 兩個新綁定
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

### 存取結構體欄位 (Accessing Struct Fields)

結構體的欄位可以使用點運算子 `.` 來存取。

對於具有具名欄位的結構體，欄位可以透過其名稱存取：

```move
public struct Foo { x: u64, y: bool }
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

對於位置結構體，欄位可以透過其在結構體定義中的位置存取：

```move
public struct PosFoo(u64, bool)
let pos_foo = PosFoo(3, true);
let x = pos_foo.0;  // x == 3
let y = pos_foo.1;  // y == true
```

存取結構體欄位而不借用或複製它們，受制於欄位的能力約束。更多詳情請參見[借用結構體與欄位](#borrowing-structs-and-fields)和[讀取與寫入欄位](#reading-and-writing-fields)部分。

### 借用結構體與欄位 (Borrowing Structs and Fields) {#borrowing-structs-and-fields}

`&` 和 `&mut` 運算子可以用於建立對結構體或欄位的參考。以下範例包含一些選填的型別標注（例如 `: &Foo`）以便展示操作的型別。

```move
let foo = Foo { x: 3, y: true };
let foo_ref: &Foo = &foo;
let y: bool = foo_ref.y;         // 透過結構體參考讀取欄位
let x_ref: &u64 = &foo.x;        // 透過擴展結構體參考來借用欄位

let x_ref_mut: &mut u64 = &mut foo.x;
*x_ref_mut = 42;            // 透過可變參考修改欄位
```

可以借用巢狀結構體內部欄位：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);

let x_ref = &bar.0.x;
```

你也可以透過對結構體的參考來借用欄位：

```move
let foo = Foo { x: 3, y: true };
let foo_ref = &foo;
let x_ref = &foo_ref.x;
// 這與 let x_ref = &foo.x 具有相同的效果
```

### 讀取與寫入欄位 (Reading and Writing Fields) {#reading-and-writing-fields}

如果你需要讀取並複製欄位的值，可以解參考 (dereference) 該借用的欄位：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(copy foo);
let x: u64 = *&foo.x;
let y: bool = *&foo.y;
let foo2: Foo = *&bar.0;
```

更規範的做法是，點運算子可用於讀取結構體欄位而無需任何借用。與[解參考](./primitive-types/references#reading-and-writing-through-references)一樣，欄位型別必須具備 `copy` [能力 (ability)](./abilities)。

```move
let foo = Foo { x: 3, y: true };
let x = foo.x;  // x == 3
let y = foo.y;  // y == true
```

點運算子可以鏈接以存取巢狀欄位：

```move
let bar = Bar(Foo { x: 3, y: true });
let x = baz.0.x; // x = 3;
```

但是，對於包含非原始型別（如向量或其他結構體）的欄位，這是不允許的：

```move
let foo = Foo { x: 3, y: true };
let bar = Bar(foo);
let foo2: Foo = *&bar.0;
let foo3: Foo = bar.0; // 錯誤！必須使用 *& 明確複製
```

我們可以可變地借用結構體的欄位以賦予其新值：

```move
let mut foo = Foo { x: 3, y: true };
*&mut foo.x = 42;     // foo = Foo { x: 42, y: true }
*&mut foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);               // bar = Bar(Foo { x: 42, y: false })
*&mut bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
*&mut bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

與解參考類似，我們可以改為直接使用點運算子來修改欄位。在上述兩種情況下，欄位型別都必須具備 `drop` [能力 (ability)](./abilities)。

```move
let mut foo = Foo { x: 3, y: true };
foo.x = 42;     // foo = Foo { x: 42, y: true }
foo.y = !foo.y; // foo = Foo { x: 42, y: false }
let mut bar = Bar(foo);         // bar = Bar(Foo { x: 42, y: false })
bar.0.x = 52;                   // bar = Bar(Foo { x: 52, y: false })
bar.0 = Foo { x: 62, y: true }; // bar = Bar(Foo { x: 62, y: true })
```

賦值的點語法也可以透過對結構體的參考來完成：

```move
let mut foo = Foo { x: 3, y: true };
let foo_ref = &mut foo;
foo_ref.x = foo_ref.x + 1;
```

## 特權結構體操作 (Privileged Struct Operations)

對結構體型別 `T` 的大多數操作只能在宣告 `T` 的模組內部執行：

- 結構體型別僅能在定義該結構體的模組內建立（「封裝 Pack」）和銷毀（「解裝 Unpack」）。
- 結構體的欄位僅在定義該結構體的模組內部可存取。

根據這些規則，如果你想在模組外部修改你的結構體，你將需要為其提供公開的 API。本章末尾包含了一些範例。

然而，正如[上文能見度部分](#visibility)所述，結構體的「型別 (types)」對其他模組始終可見。

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
        //   ^ 有效，該型別是公開的

    }

    fun f1(foo: Foo) {
        let x = foo.x;
        //      ^ 錯誤！無法在 `a::m` 之外存取 `Foo` 的欄位
    }

    fun f2() {
        let foo_wrapper = Wrapper { foo: a::m::new_foo() };
        //                               ^ 有效，函式是公開的
    }
}
```

## 所有權 (Ownership)

如上文[定義結構體](#defining-structs)中所述，結構體預設是線性的且短暫的。這意味著它們不能被複製或捨棄。當建模像貨幣這樣的現實世界資產時，此屬性非常有用，因為你不希望貨幣被重製或在流通中遺失。

```move
module a::m;

public struct Foo { x: u64 }

public fun copying() {
    let foo = Foo { x: 100 };
    let foo_copy = copy foo; // 錯誤！使用 'copy' 需要具備 'copy' 能力
    let foo_ref = &foo;
    let another_copy = *foo_ref // 錯誤！解參考需要具備 'copy' 能力
}

public fun destroying_1() {
    let foo = Foo { x: 100 };

    // 錯誤！當函式回傳時，foo 仍包含一個值。
    // 這種銷毀行為需要具備 'drop' 能力。
}

public fun destroying_2(f: &mut Foo) {
    *f = Foo { x: 100 } // 錯誤！
                        // 透過寫入來銷毀舊值需要具備 'drop' 能力。
}
```

要修正 `fun destroying_1` 範例，你需要手動「解裝 (unpack)」該值：

```move
module a::m;

public struct Foo { x: u64 }

public fun destroying_1_fixed() {
    let foo = Foo { x: 100 };
    let Foo { x: _ } = foo;
}
```

請記住，你只能在定義結構體的模組內解構結構體。這可以用來強制執行系統中的某些不變數，例如貨幣守恆。

另一方面，如果你的結構體不代表具有價值的東西，你可以加上 `copy` 和 `drop` 能力，以獲得在其他程式語言中更熟悉的結構體行為：

```move
module a::m;

public struct Foo has copy, drop { x: u64 }

public fun run() {
    let foo = Foo { x: 100 };
    let foo_copy = foo;
    //             ^ 此程式碼複製了 foo，
    //             而 `let x = move foo` 則會轉移 foo
    let x = foo.x;            // x = 100
    let x_copy = foo_copy.x;  // x = 100

    // 當函式回傳時，foo 和 foo_copy 都會被隱式捨棄
}
```

## 儲存空間 (Storage)

結構體可以用於定義儲存架構 (storage schemas)，但具體細節因 Move 的部署環境而異。詳見 [`key` 能力](./abilities#key) 與 [Sui 物件 (Sui Objects)](./abilities/object) 章節。
