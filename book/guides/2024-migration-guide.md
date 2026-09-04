---
description: 將你的 Move 原始碼遷移至 2024 版本：模組標籤 (module labels)、let mut、公開結構 (public structs)、方法語法 (method syntax)、列舉 (enums) 與 match、巨集 (macros)、巧妙錯誤 (clever errors)，以及逐步操作說明。
title: Move 2024 遷移指南
keywords:
  - Move
  - Sui
  - Move tutorial
  - move
  - '2024'
  - migration
  - guide
questions:
  - What is Move 2024 Migration Guide in Move?
  - How do I use Move 2024 Migration Guide in Move?
  - What is Using the 2024 Edition in Move?
  - What is Migration Tool in Move?
answer: 'Migrate your Move code to the 2024 edition: module labels, let mut, public structs, method syntax, enums and match, macros, clever errors, and step-by-step instructions.'
goal:
  description: 'Reader understands migrate your Move code to the 2024 edition: module labels, let mut, public structs, method syntax, enums and match, macros, clever errors, and step-by-step instructions'
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

# Move 2024 遷移指南 (Move 2024 Migration Guide) {#move-2024-migration-guide}

Move 2024 是由 Mysten Labs 維護的 Move 語言目前版本，也是本書所教授的版本。本指南是為了將原始版本（下文稱為 _Move 2020_）的原始碼或知識遷移過來的讀者所撰寫：它會逐項列出變更內容，並為每項功能提供變更前後的範例。

> 本指南提供高層次的概觀。此處列出的每項功能在本書中都有專屬章節，並已從其標題連結至該章節——如需完整說明，請參考這些章節。

## 使用 2024 版 (Using the 2024 Edition) {#using-the-2024-edition}

版本會在 [套件清單](./../concepts/manifest) 的 `[package]` 區段中指定。
穩定版 `2024` 是預設且建議優先選用的版本；`2024.beta` 與
`2024.alpha` 版可讓你提早使用仍在開發、可能變更的功能：

```toml
[package]
name = "my_package"
edition = "2024"
```

## 遷移工具 (Migration Tool) {#migration-tool}

Move CLI 提供遷移工具，可將舊版原始碼更新至新版。若要使用遷移工具，請在套件目錄中執行下列命令：

```bash
$ sui move migrate
```

遷移工具會處理機械式變更：`let mut` 語法、結構上的 `public` 修飾詞，以及以 `public(package)` 可見性取代 `friend` 宣告。

## 模組標籤 (Module Label) {#module-label}

_請參閱 [模組](./../move-basics/module#module-block)。_

模組不再需要將其主體包在區塊中：*模組標籤*語法只需宣告一次模組，
之後的所有內容都屬於該模組——可節省整個文件的一層縮排。
區塊語法仍受到支援，但僅適合用於在單一文件中宣告多個模組，
而這並非建議的做法：

```move
// Move 2020：模組區塊
module book::my_module {
    public struct Book {}
}

// Move 2024：模組標籤
module book::my_module;

public struct Book {}
```

## 可變繫結與 `let mut` (Mutable Bindings with `let mut`) {#mutable-bindings-with-let-mut}

_請參閱 [基本型別](./../move-basics/primitive-types#variables-and-assignment)。_

Move 2024 要求使用 `mut` 關鍵字來宣告可重新指派或可被可變借用的變數。嘗試變更未以 `mut` 宣告的變數時，編譯器會產生錯誤：

```move
// Move 2020
let x: u64 = 10;
x = 20;

// Move 2024
let mut x: u64 = 10;
x = 20;
```

此外，`mut` 關鍵字也用於元組解構與函式引數，並置於變數名稱之前：

```move
// 以值傳遞並進行變更
fun takes_by_value_and_mutates(mut v: Value): Value {
    v.field = 10;
    v
}

// 在元組解構中
fun destruct() {
    let (mut x, y) = point::get_point();
}

// 在結構解包中
fun unpack() {
    let Point { x, mut y } = point::get_point();
}
```

## 結構可見性 (Struct Visibility) {#struct-visibility}

_請參閱[使用 Struct 的自訂型別](./../move-basics/struct#defining-a-struct)。_

在 Move 2024 中，結構宣告必須使用可見性修飾詞。目前唯一可用的可見性為 `public`：

```move
// Move 2020
struct Book {}

// Move 2024
public struct Book {}
```

請注意，`public` 適用於結構的*型別*——欄位仍維持在模組內部，且只有定義該結構的模組可以打包與解包此結構，與先前完全相同。

## Friend 已淘汰 (Friends Are Deprecated) {#friends-are-deprecated}

_請參閱 [可見性修飾詞](./../move-basics/visibility#package-visibility)。_

`friend` 宣告與 `public(friend)` 可見性已淘汰。取而代之的是，`public(package)` 可見性能讓同一套件中的任何模組呼叫函式，不需要任何宣告。`friend book::module_name;` 陳述式已完全移除：

```move
// Move 2020
friend book::friend_module;
public(friend) fun protected_function() {}

// Move 2024：不需要 friend 宣告
public(package) fun protected_function() {}
```

## 方法語法 (Method Syntax) {#method-syntax}

_請參閱 [結構方法](./../move-basics/struct-methods)。_

第一個引數為同一模組中定義型別的函式，會成為該型別的 _方法_，
可在使用該型別的任何地方以點語法呼叫：

```move
public fun count(c: &Counter): u64 { /* ... */ }

fun use_counter(c: &Counter) {
    // Move 2020
    let count = counter::count(c);

    // Move 2024
    let count = c.count();
}
```

標準函式庫與 Sui Framework 充分運用了這項功能：原生與標準型別
開箱即附帶相關聯的方法：

```move
// vector 轉為 string 與 ascii string
let str: String = b"Hello, World!".to_string();
let ascii: ascii::String = b"Hello, World!".to_ascii_string();

// address 轉為 bytes
let bytes = @0xa11ce.to_bytes();
```

## `use fun` 與方法別名 (`use fun` and Method Aliases) {#use-fun-and-method-aliases}

_請參閱[結構方法](./../move-basics/struct-methods#method-aliases)。_

`use fun` 宣告會以選定的方法名稱，將函式與型別建立關聯。別名
可在模組內為任何型別於本機宣告；若型別定義於同一模組中，則也可以使用 `public use fun` 公開宣告：

```move
// 本機：型別對此模組而言是外部型別
use fun my_custom_function as vector.do_magic;

// 匯出：型別定義於同一模組中
public use fun kiosk_owner_cap_for as KioskOwnerCap.kiosk;
```

## 借用的索引語法 (Index Syntax for Borrowing) {#index-syntax-for-borrowing}

_請參閱 Move 參考資料中的 [Vector](./../move-basics/vector#reading-elements) 與 [Index Syntax](./../../reference/index-syntax)。_

方括號可取代集合型別上明確的 `borrow` 與 `borrow_mut` 呼叫：

```move
fun play_vec() {
    let mut v = vector[1, 2, 3, 4];
    let first = &v[0];         // 呼叫 vector::borrow(&v, 0)
    let first_mut = &mut v[0]; // 呼叫 vector::borrow_mut(&mut v, 0)
    let first_copy = v[0];     // 呼叫 *vector::borrow(&v, 0)
}
```

`vector` 與 Sui Framework 的集合型別皆支援此語法：`VecMap`、
`Table`、`Bag`、`ObjectTable`、`ObjectBag` 及 `LinkedTable`。自訂型別可透過以
`#[syntax(index)]` 屬性標記其借用函式來實作此語法：

```move
#[syntax(index)]
public fun borrow<T>(c: &List<T>, key: String): &T { /* ... */ }

#[syntax(index)]
public fun borrow_mut<T>(c: &mut List<T>, key: String): &mut T { /* ... */ }
```

## 字串常值 (String Literals) {#string-literals}

_請參閱 [String](./../move-basics/string#string-literals)。_

Move 2020 僅提供位元組字串常值，且建立 `String` 需要明確轉換。新版本新增字串常值 `"..."`，其型別會依據上下文進行*推斷*——它會成為預期的 `String`、`ascii::String` 或 `vector<u8>`：

```move
// Move 2020：位元組，於執行階段轉換
let str: String = string::utf8(b"Hello");

// Move 2024：常值會在編譯階段進行檢查與型別判定
let str: String = "Hello";
let ascii: std::ascii::String = "ASCII";
```

內容會在編譯階段驗證：作為 `ascii::String` 使用的常值只能包含 ASCII 字元，否則原始碼將無法編譯。

## 列舉與 `match` (Enums and `match`) {#enums-and-match}

_請參閱 [列舉與 Match](./../move-basics/enum-and-match)。_

Move 2024 引入了 _列舉_（enums）——具有多個變體的使用者自訂型別——以及用於處理它們的 `match`
運算式。兩者結合後，可在單一型別下表示不同的資料結構；先前則是以多個結構和執行階段檢查來模擬：

```move
/// 一個型別——三種不同形態的資料。
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

`match` 運算式不限於列舉：它也適用於基本值和結構、要求各分支涵蓋所有情況，並支援用於其餘情況的 `_` 萬用字元。

## 巨集 (Macros) {#macros}

_請參閱 [巨集函式](./../move-basics/macros)。_

Move 2024 引入了 _巨集函式_——在編譯期間於呼叫位置展開的函式，
可將 _lambda_ 作為引數。巨集名稱後方會接上 `!` 符號：

```move
// 可呼叫為 `for!(0, 10, |i| call(i));`
macro fun for($start: u64, $stop: u64, $body: |u64|) {
    let mut i = $start;
    let stop = $stop;
    while (i < stop) {
        $body(i);
        i = i + 1
    }
}
```

熟悉的 `assert!` 不再是編譯器特別處理的魔法功能——它是一個一般巨集，且其
錯誤碼引數現在為選填。標準函式庫提供了一組豐富的巨集，並迅速成為撰寫迭代作業的慣用方式：

```move
let v = vector[1, 2, 3];

// 取代手動撰寫的 while 迴圈：
let doubled = v.map!(|n| n * 2);
let sum = v.fold!(0, |acc, n| acc + n);
v.do!(|n| std::debug::print(&n));
```

## 不含程式碼的中止 (Abort Without a Code) {#abort-without-a-code}

_請參閱[中止執行](./../move-basics/assert-and-abort#omitting-the-abort-code)。_

中止程式碼現在為選填：單獨使用 `abort`（以及未提供第二個引數的 `assert!`）會自動推導程式碼，並編碼失敗所在的模組與原始碼行號。這很適合用於預期不會走到的分支：

```move
// Move 2020：一律必須提供程式碼
if (!is_valid) abort 0;

// Move 2024
if (!is_valid) abort;
assert!(is_valid);
```

## 智慧錯誤 (Clever Errors) {#clever-errors}

_請參閱 [中止執行](./../move-basics/assert-and-abort#error-messages)。_

標記 `#[error]` 屬性的錯誤常數可攜帶人類可讀的訊息──以 `vector<u8>` 取代單純的 `u64`。發生中止時，工具會解碼常數名稱、訊息與原始碼行數，因此不必再查找數值代碼：

```move
#[error]
const ENotAuthorized: vector<u8> = "The caller is not authorized to perform this action";

public fun protected_action(/* …… */) {
    assert!(is_authorized, ENotAuthorized);
}
```

## 在測試中擴充模組 (Extending Modules in Tests) {#extending-modules-in-tests}

_請參閱[擴充模組](./../testing/extend-foreign-module)。_

`extend module` 宣告會將僅供測試使用的成員新增至既有模組中——包括來自外部套件的模組——並可完整存取其私有型別。它解決了長久以來測試不提供測試工具的依賴項時所面臨的問題：

```move
#[test_only]
extend module pyth::price_info;

// 此處定義的函式僅能在測試中封裝與解封裝
// `pyth::price_info` 的私有型別。
```

> 模組擴充功能仍在開發中，目前需要 `2024.alpha` 版本。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 部落格上的 [Move 2024 遷移指南](https://blog.sui.io/move-2024-migration-guide)。
