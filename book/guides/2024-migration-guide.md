---
description: 將 Move 程式碼遷移至 2024 版 (2024 edition)：模組標籤 (module labels)、let mut、公開結構 (public structs)、方法語法 (method syntax)、列舉 (enums) 與 match、巨集 (macros)、聰明錯誤 (clever errors)，以及逐步操作說明。
---

# Move 2024 遷移指南 (Move 2024 Migration Guide) {#move-2024-migration-guide}

Move 2024 是 Mysten Labs 維護的 Move 語言目前版本，也是本書所教授的版本。本指南是為了將程式碼——或知識——從原始版本（以下稱為 _Move 2020_）遷移過來的讀者所寫：本指南逐一列出每個功能的變更，並針對每項變更提供修改前後的範例對照。

> 本指南為高階概覽。這裡列出的每個功能在本書中都有專屬章節，可從標題連結進去——完整內容請參閱各章節。

## 使用 2024 版本 (Using the 2024 Edition) {#using-the-2024-edition}

版本是在 [Package Manifest](./../concepts/manifest) 的 `[package]` 區段中指定的。
穩定的 `2024` 版本是預設選擇，也是建議使用的版本；`2024.beta` 和
`2024.alpha` 版本則提供仍在開發中、可能會變動的功能的搶先體驗：

```toml
[package]
name = "my_package"
edition = "2024"
```

## 遷移工具 (Migration Tool) {#migration-tool}

Move CLI 有一個遷移工具，可以將舊版程式碼更新到新版本。要使用遷移
工具，請在套件目錄中執行以下指令：

```bash
$ sui move migrate
```

遷移工具會處理機械式的變更：`let mut` 語法、struct 上的 `public`
修飾詞，以及用 `public(package)` 可見性取代 `friend` 宣告。

## 模組標籤 (Module Label) {#module-label}

_參閱 [Module](./../move-basics/module#module-block)。_

模組不再需要將其主體包裝在區塊中：*模組標籤*語法宣告模組一次，之後的所有內容都屬於該模組——為整個檔案節省了一層縮排。區塊語法仍受支援，但僅在同一檔案中宣告多個模組時才有用，而這並非建議的做法：

```move
// Move 2020：模組區塊
module book::my_module {
    public struct Book {}
}

// Move 2024：模組標籤
module book::my_module;

public struct Book {}
```

## 使用 `let mut` 進行可變綁定 (Mutable Bindings with `let mut`) {#mutable-bindings-with-let-mut}

_參見 [基本型別](./../move-basics/primitive-types#variables-and-assignment)。_

Move 2024 要求使用 `mut` 關鍵字來宣告可以被重新賦值或可變借用的變數。編譯器在嘗試修改未宣告 `mut` 的變數時會發出錯誤：

```move
// Move 2020
let x: u64 = 10;
x = 20;

// Move 2024
let mut x: u64 = 10;
x = 20;
```

此外，`mut` 關鍵字也用於元組解構與函式引數中，放置在變數名稱之前：

```move
// 依值傳遞並修改
fun takes_by_value_and_mutates(mut v: Value): Value {
    v.field = 10;
    v
}

// 用於元組解構
fun destruct() {
    let (mut x, y) = point::get_point();
}

// 用於結構體解包
fun unpack() {
    let Point { x, mut y } = point::get_point();
}
```

## Struct 可見性 (Struct Visibility) {#struct-visibility}

_請參考[使用 Struct 的自訂型別](./../move-basics/struct#defining-a-struct)。_

在 Move 2024 中，struct 宣告需要可見性修飾詞。目前唯一可用的可見性是 `public`：

```move
// Move 2020
struct Book {}

// Move 2024
public struct Book {}
```

請注意 `public` 套用於 struct 的 _型別_ ——欄位仍維持模組內部可見，且只有定義該 struct 的模組才能封裝與解封裝該 struct，與先前完全相同。

## Friends 已棄用 (Friends Are Deprecated) {#friends-are-deprecated}

_參見[可見性修飾符](./../move-basics/visibility#package-visibility)。_

`friend` 宣告與 `public(friend)` 可見性已棄用。取而代之，`public(package)` 可見性讓函式可以被同一 package 內的任何模組呼叫——不需要任何宣告。`friend book::module_name;` 陳述式已完全移除：

```move
// Move 2020
friend book::friend_module;
public(friend) fun protected_function() {}

// Move 2024：不需要 friend 宣告
public(package) fun protected_function() {}
```

## 方法語法 (Method Syntax) {#method-syntax}

_參見 [Struct Methods](./../move-basics/struct-methods)。_

第一個參數是同一模組中定義型別的函式會成為該型別的*方法*，可在該型別出現的任何地方以點語法呼叫：

```move
public fun count(c: &Counter): u64 { /* ... */ }

fun use_counter(c: &Counter) {
    // Move 2020
    let count = counter::count(c);

    // Move 2024
    let count = c.count();
}
```

標準函式庫與 Sui Framework 充分運用了這一點：原生型別與標準型別都內建了相關聯的方法：

```move
// vector 轉為 string 與 ascii string
let str: String = b"Hello, World!".to_string();
let ascii: ascii::String = b"Hello, World!".to_ascii_string();

// address 轉為 bytes
let bytes = @0xa11ce.to_bytes();
```

## `use fun` 與方法別名 (`use fun` and Method Aliases) {#use-fun-and-method-aliases}

_參見 [Struct Methods](./../move-basics/struct-methods#method-aliases)。_

`use fun` 宣告會將一個函式在指定的方法名稱下與某個型別建立關聯。若該型別是模組本地的，可以為它宣告一個別名；若該型別是在同一個模組中定義的，則可以使用 `public use fun` 公開宣告：

```move
// 本地：該型別對此模組而言是外部型別
use fun my_custom_function as vector.do_magic;

// 匯出：該型別是在同一個模組中定義的
public use fun kiosk_owner_cap_for as KioskOwnerCap.kiosk;
```

## 借用的索引語法 (Index Syntax for Borrowing) {#index-syntax-for-borrowing}

_參見 Move 參考文件中的 [Vector](./../move-basics/vector#reading-elements) 與
[Index Syntax](./../../reference/index-syntax)。_

方括號取代了集合型別上明確的 `borrow` 與 `borrow_mut` 呼叫：

```move
fun play_vec() {
    let mut v = vector[1, 2, 3, 4];
    let first = &v[0];         // 呼叫 vector::borrow(&v, 0)
    let first_mut = &mut v[0]; // 呼叫 vector::borrow_mut(&mut v, 0)
    let first_copy = v[0];     // 呼叫 *vector::borrow(&v, 0)
}
```

此語法由 `vector` 以及 Sui Framework 的集合型別所支援：`VecMap`、
`Table`、`Bag`、`ObjectTable`、`ObjectBag` 與 `LinkedTable`。自訂型別可以透過將其
borrow 函式標記 `#[syntax(index)]` 屬性來實作此語法：

```move
#[syntax(index)]
public fun borrow<T>(c: &List<T>, key: String): &T { /* ... */ }

#[syntax(index)]
public fun borrow_mut<T>(c: &mut List<T>, key: String): &mut T { /* ... */ }
```

## 字串字面值 (String Literals) {#string-literals}

_參見 [String](./../move-basics/string#string-literals)。_

Move 2020 只提供 byte-string 字面值，建構 `String` 需要明確轉換。新版本新增了字串字面值 `"..."`，其型別會根據上下文**推斷**——會變成 `String`、`ascii::String`，或 `vector<u8>`，依需求而定：

```move
// Move 2020：位元組，於執行期轉換
let str: String = string::utf8(b"Hello");

// Move 2024：此字面值在編譯期會被檢查並賦予型別
let str: String = "Hello";
let ascii: std::ascii::String = "ASCII";
```

內容會在編譯時期進行驗證：若字面值用作 `ascii::String`，則必須只包含 ASCII 字元，否則程式碼將無法編譯。

## 列舉與 `match` (Enums and `match`) {#enums-and-match}

_參見 [Enums and Match](./../move-basics/enum-and-match)。_

Move 2024 引入了*列舉* —— 具有多個變體的使用者定義型別 —— 以及用來處理它們的 `match` 運算式。兩者搭配可以用單一型別表達多種不同的資料結構，這是先前需要用多個結構體與執行期檢查來模擬的：

```move
/// 一種型別 —— 三種不同的資料形狀。
public enum Segment has copy, drop {
    Empty,
    String(String),
    Special { content: vector<u8>, encoding: u8 },
}

public fun is_empty(s: &Segment): bool {
    match (s) {
        Segment::Empty => true,
        _ => false,
    }
}
```

`match` 運算式並不限於列舉：它同樣適用於基本型別與結構體，要求各分支必須窮盡所有情況，並支援用 `_` 萬用字元處理剩餘情況。

## 巨集 (Macros) {#macros}

_請參閱 [巨集函式](./../move-basics/macros)。_

Move 2024 引入了*巨集函式* —— 這是在編譯期於呼叫端展開的函式，可以接受_lambda_作為參數。巨集名稱後面會接 `!` 符號：

```move
// 可以透過 `for!(0, 10, |i| call(i));` 呼叫
macro fun for($start: u64, $stop: u64, $body: |u64|) {
    let mut i = $start;
    let stop = $stop;
    while (i < stop) {
        $body(i);
        i = i + 1
    }
}
```

熟悉的 `assert!` 不再是編譯器特殊處理的魔法 —— 它現在是一個普通的巨集，而且其錯誤碼參數現在是選填的。標準函式庫提供了一組豐富的巨集，這些巨集很快就成為撰寫迭代的慣用方式：

```move
let v = vector[1, 2, 3];

// 取代手寫的 while 迴圈：
let doubled = v.map!(|n| n * 2);
let sum = v.fold!(0, |acc, n| acc + n);
v.do!(|n| std::debug::print(&n));
```

## 不使用中止碼中止 (Abort Without a Code) {#abort-without-a-code}

_參見[中止執行](./../move-basics/assert-and-abort#omitting-the-abort-code)。_

中止碼現在是可選的：單獨的 `abort`(以及不帶第二個參數的 `assert!`)會自動推導出碼，編碼失敗發生的模組與原始碼行號。這很適合用在預期不會被觸及的分支：

```move
// Move 2020: 一定要提供 code
if (!is_valid) abort 0;

// Move 2024
if (!is_valid) abort;
assert!(is_valid);
```

## 巧妙的錯誤 (Clever Errors) {#clever-errors}

_參閱 [中止執行](./../move-basics/assert-and-abort#error-messages)。_

標記 `#[error]` 屬性的錯誤常數可以帶有人類可讀的訊息 — 使用 `vector<u8>` 而非單純的 `u64`。中止時，工具鏈會解碼常數名稱、訊息與原始碼行號，不再需要查找數字代碼：

```move
#[error]
const ENotAuthorized: vector<u8> = "The caller is not authorized to perform this action";

public fun protected_action(/* ... */) {
    assert!(is_authorized, ENotAuthorized);
}
```

## 在測試中擴充模組 (Extending Modules in Tests) {#extending-modules-in-tests}

_請參閱 [擴充外部模組 (Extending Modules)](./../testing/extend-foreign-module)。_

`extend module` 宣告可以為現有模組——包括來自外部套件的模組——新增僅供測試使用的成員，並完整存取其私有型別。這解決了長久以來測試沒有提供測試工具的依賴項時所遇到的問題：

```move
#[test_only]
extend module pyth::price_info;

// 這裡定義的函式可以在測試中
// 封裝與解封裝 `pyth::price_info` 的私有型別
```

> 模組擴充功能仍在開發中，目前需要 `2024.alpha` edition。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui Blog 上的 [Move 2024 遷移指南](https://blog.sui.io/move-2024-migration-guide)。
