---
description: Move 程式碼品質檢查清單 (Move code quality checklist)：依據目前的最佳實踐，檢視你的 Sui 智慧合約在安全性、風格與可維護性上的表現。
---

# 程式碼品質檢查清單 (Code Quality Checklist) {#code-quality-checklist}

Move 語言及其生態系統的快速演進，使許多舊有做法變得過時。本指南作為開發者審查自身程式碼的檢查清單，確保其符合當前 Move 開發的最佳實踐。請仔細閱讀並將盡可能多的建議套用到你的程式碼中。

## 程式碼組織 (Code Organization) {#code-organization}

本指南提到的部分問題可以透過使用
[Move Formatter](https://www.npmjs.com/package/@mysten/prettier-plugin-move) 來修正，可作為 CLI 工具、
[CI check](https://github.com/marketplace/actions/move-formatter)，或
[VSCode（Cursor）外掛](https://marketplace.visualstudio.com/items?itemName=mysten.prettier-move)使用。

## Package Manifest 套件清單 (Package Manifest) {#package-manifest}

### 使用正確的版本 (Use Right Edition) {#use-right-edition}

本指南中的所有功能都需要 Move 2024 Edition，且必須在套件清單中指定。

```toml
[package]
name = "my_package"
edition = "2024.beta" # or (just) "2024"
```

### 隱含的 Framework 依賴 (Implicit Framework Dependency) {#implicit-framework-dependency}

從 Sui 1.45 開始，你不再需要在 `Move.toml` 中指定 framework 依賴：

```toml
# 舊版，1.45 之前
[dependencies]
Sui = { ... }

# modern day, Sui、Bridge、MoveStdlib 與 SuiSystem 都是隱式引入的！
[dependencies]
```

### 具前綴的具名位址 (Prefix Named Addresses) {#prefix-named-addresses}

如果你的套件名稱很通用（例如 `token`）——尤其是當你的專案包含多個套件時——請務必為具名位址加上前綴：

```toml
# bad! 沒有指向性，且可能衝突
[addresses]
math = "0x0"

# good! 清楚表明專案，不太可能衝突
[addresses]
my_protocol_math = "0x0"
```

## Imports、模組與常數 (Imports, Module and Constants) {#imports-module-and-constants}

### 使用模組標籤 (Using Module Label) {#using-module-label}

```move
// bad: 增加縮排，舊式風格
module my_package::my_module {
    public struct A {}
}

// 好！
module my_package::my_module;

public struct A {}
```

### `use` 陳述式中不要單獨出現 `Self` (No Single `Self` in `use` Statements) {#no-single-self-in-use-statements}

```move
// 正確，member + self import
use my_package::other::{Self, OtherMember};

// bad! `{Self}` 是多餘的
use my_package::my_module::{Self};

// 好！
use my_package::my_module;
```

### 將 `use` 陳述式與 `Self` 分組 (Group `use` Statements with `Self`) {#group-use-statements-with-self}

```move
// 差！
use my_package::my_module;
use my_package::my_module::OtherMember;

// 好！
use my_package::my_module::{Self, OtherMember};
```

### 錯誤常數使用 `EPascalCase` (Error Constants Are in `EPascalCase`) {#error-constants-are-in-epascalcase}

```move
// bad! 全大寫是用於一般常數
const NOT_AUTHORIZED: u64 = 0;

// good! 清楚表明這是錯誤常數
const ENotAuthorized: u64 = 0;
```

### 一般常數使用 `ALL_CAPS` (Regular Constants Are `ALL_CAPS`) {#regular-constants-are-all_caps}

```move
// bad! PascalCase 是跟錯誤常數關聯的
const MyConstant: vector<u8> = "my const";

// good! 清楚表明這是一個常數值
const MY_CONSTANT: vector<u8> = "my const";
```

## 結構體 (Structs) {#structs}

### 能力型別以 `Cap` 為後綴 (Capabilities are Suffixed with `Cap`) {#capabilities-are-suffixed-with-cap}

```move
// 不好！如果是能力型別，要加上 `Cap` 後綴
public struct Admin has key, store {
    id: UID,
}

// 好！審查者能立即知道這個型別該預期什麼
public struct AdminCap has key, store {
    id: UID,
}
```

### 名稱中不要出現 `Potato` (No `Potato` in Names) {#no-potato-in-names}

```move
// 不好！它沒有任何能力，我們已經知道這是 Hot-Potato 型別
public struct PromisePotato {}

// 好！
public struct Promise {}
```

### 事件應以過去式命名 (Events Should Be Named in Past Tense) {#events-should-be-named-in-past-tense}

```move
// 不好！不清楚這個結構體在做什麼
public struct RegisterUser has copy, drop { user: address }

// 好！清楚明瞭，這是一個事件
public struct UserRegistered has copy, drop { user: address }
```

### 動態欄位鍵使用位置式結構體並加上 `Key` 後綴 (Use Positional Structs for Dynamic Field Keys + `Key` Suffix) {#use-positional-structs-for-dynamic-field-keys-key-suffix}

```move
// 不算太差，但不符合標準風格
public struct DynamicField has copy, drop, store {}

// 好！標準風格，帶有 Key 後綴
public struct DynamicFieldKey() has copy, drop, store;
```

## 函式 (Functions) {#functions}

### 不要用 `public entry`，只用 `public` 或 `entry` (No `public entry`, Only `public` or `entry`) {#no-public-entry-only-public-or-entry}

```move
// 不好！entry 不是讓函式可在交易中被呼叫的必要條件
public entry fun do_something() { /* ... */ }

// 好！public 函式更寬鬆，可以回傳值
public fun do_something_2(): T { /* ... */ }
```

### 為 PTB 寫可組合的函式 (Write Composable Functions for PTBs) {#write-composable-functions-for-ptbs}

```move
// 不好！不可組合，更難測試！
public fun mint_and_transfer(ctx: &mut TxContext) {
    /* ... */
    transfer::transfer(nft, ctx.sender());
}

// 好！可組合！
public fun mint(ctx: &mut TxContext): NFT { /* ... */ }

// 好！刻意設計成不可組合
entry fun mint_and_keep(ctx: &mut TxContext) { /* ... */ }
```

### 物件放最前面（Clock 除外） (Objects Go First (Except for Clock)) {#objects-go-first-except-for-clock}

```move
// 不好！難以閱讀！
public fun call_app(
    value: u8,
    app: &mut App,
    is_smth: bool,
    cap: &AppCap,
    clock: &Clock,
    ctx: &mut TxContext,
) { /* ... */ }

// 好！
public fun call_app(
    app: &mut App,
    cap: &AppCap,
    value: u8,
    is_smth: bool,
    clock: &Clock,
    ctx: &mut TxContext,
) { /* ... */ }
```

### Capability 放第二位 (Capabilities Go Second) {#capabilities-go-second}

```move
// 不好！破壞方法關聯性
public fun authorize_action(cap: &AdminCap, app: &mut App) { /* ... */ }

// 好！讓 Cap 在函式簽章中保持可見，並維持 `.calls()`
public fun authorize_action(app: &mut App, cap: &AdminCap) { /* ... */ }
```

### Getter 以欄位名稱命名 + `_mut` (Getters Named After Field + `_mut`) {#getters-named-after-field-_mut}

```move
// 不好！不必要的 `get_`
public fun get_name(u: &User): String { /* ... */ }

// 好！清楚表明是存取欄位 `name`
public fun name(u: &User): String { /* ... */ }

// 好！可變參考使用 `_mut`
public fun details_mut(u: &mut User): &mut Details { /* ... */ }
```

## 函式主體：結構體方法 (Function Body: Struct Methods) {#function-body-struct-methods}

### 常見的 Coin 操作 (Common Coin Operations) {#common-coin-operations}

```move
// bad! 舊式程式碼，難以閱讀！
let paid = coin::split(&mut payment, amount, ctx);
let balance = coin::into_balance(paid);

// good! struct 方法讓它更容易！
let balance = payment.split(amount, ctx).into_balance();

// even better（在這個範例中——不需要建立臨時 coin）
let balance = payment.balance_mut().split(amount);

// 也可以這樣做！
let coin = balance.into_coin(ctx);
```

### 不要匯入 `std::string::utf8` (Do Not Import `std::string::utf8`) {#do-not-import-stdstringutf8}

```move
// bad! 不幸的是，非常常見！
use std::string::utf8;

let str = utf8(b"hello, world!");

// good! 這個字面值在編譯期就會被檢查
let str: String = "hello, world!";

// 另外，對 ASCII 字串也適用
let ascii: ascii::String = "hello, world!";
```

> `.to_string()` 和 `.to_ascii_string()` 這兩個 `vector<u8>` 上的方法，在轉換編譯期未知的位元組時仍有其用途。
> 對於字面值，則應優先使用字串字面值語法。

### UID 有 `delete` (UID has `delete`) {#uid-has-delete}

```move
// 差！
object::delete(id);

// 好！
id.delete();
```

### `ctx` 有 `sender()` (`ctx` has `sender()`) {#ctx-has-sender}

```move
// 差！
tx_context::sender(ctx);

// 好！
ctx.sender()
```

### Vector 有字面值語法，也有相關函式 (Vector Has a Literal. And Associated Functions) {#vector-has-a-literal-and-associated-functions}

```move
// 差！
let mut my_vec = vector::empty();
vector::push_back(&mut my_vec, 10);
let first_el = vector::borrow(&my_vec);
assert!(vector::length(&my_vec) == 1);

// 好！
let mut my_vec = vector[10];
let first_el = my_vec[0];
assert!(my_vec.length() == 1);
```

### 集合支援索引語法 (Collections Support Index Syntax) {#collections-support-index-syntax}

```move
let x: VecMap<u8, String> = /* ... */;

// 差！
x.get(&10);
x.get_mut(&10);

// 好！
&x[&10];
&mut x[&10];
```

## Option 巨集 (Option -> Macros) {#option---macros}

### 銷毀並呼叫函式 (Destroy And Call Function) {#destroy-and-call-function}

```move
// 差！
if (opt.is_some()) {
    let inner = opt.destroy_some();
    call_function(inner);
};

// good! 有一個 macro 可以用！
opt.do!(|value| call_function(value));
```

### 帶預設值的銷毀 (Destroy Some With Default) {#destroy-some-with-default}

```move
let opt = option::none();

// 差！
let value = if (opt.is_some()) {
    opt.destroy_some()
} else {
    abort EError
};

// good! 有一個 macro！
let value = opt.destroy_or!(default_value);

// 你甚至可以在 `none` 時 abort
let value = opt.destroy_or!(abort ECannotBeEmpty);
```

## Loops -> Macros 迴圈轉巨集 (Loops -> Macros) {#loops---macros}

### 執行 N 次操作 (Do Operation N Times) {#do-operation-n-times}

```move
// bad! 難以閱讀！
let mut i = 0;
while (i < 32) {
    do_action();
    i = i + 1;
};

// good! 任何 uint 都有這個 macro！
32u8.do!(|_| do_action());
```

### 從迭代建立新向量 (New Vector From Iteration) {#new-vector-from-iteration}

```move
// 較難閱讀！
let mut i = 0;
let mut elements = vector[];
while (i < 32) {
    elements.push_back(i);
    i = i + 1;
};

// 易於閱讀！
vector::tabulate!(32, |i| i);
```

### 對向量的每個元素執行操作 (Do Operation on Every Element of a Vector) {#do-operation-on-every-element-of-a-vector}

```move
// 差！
let mut i = 0;
while (i < vec.length()) {
    call_function(&vec[i]);
    i = i + 1;
};

// 好！
vec.do_ref!(|e| call_function(e));
```

### 銷毀向量並對每個元素呼叫函式 (Destroy a Vector and Call a Function on Each Element) {#destroy-a-vector-and-call-a-function-on-each-element}

```move
// 差！
while (!vec.is_empty()) {
    call(vec.pop_back());
};

// 好！
vec.destroy!(|e| call(e));
```

### 將向量摺疊成單一值 (Fold Vector Into a Single Value) {#fold-vector-into-a-single-value}

```move
// 差！
let mut aggregate = 0;
let mut i = 0;

while (i < source.length()) {
    aggregate = aggregate + source[i];
    i = i + 1;
};

// 好！
let aggregate = source.fold!(0, |acc, v| {
    acc + v
});
```

### 過濾向量元素 (Filter Elements of the Vector) {#filter-elements-of-the-vector}

> Note: `T: drop` in the `source` vector

```move
// 差！
let mut filtered = [];
let mut i = 0;
while (i < source.length()) {
    if (source[i] > 10) {
        filtered.push_back(source[i]);
    };
    i = i + 1;
};

// 好！
let filtered = source.filter!(|e| e > 10);
```

## 其他 (Other) {#other}

### 解構賦值中可全部忽略的值 (Ignored Values In Unpack Can Be Ignored Altogether) {#ignored-values-in-unpack-can-be-ignored-altogether}

```move
// bad! 非常稀疏！
let MyStruct { id, field_1: _, field_2: _, field_3: _ } = value;
id.delete();

// good! 2024 語法
let MyStruct { id, .. } = value;
id.delete();
```

## 測試 (Testing) {#testing}

### 合併 `#[test]` 與 `#[expected_failure(...)]` (Merge `#[test]` and `#[expected_failure(...)]`) {#merge-test-and-expected_failure}

```move
// 差！
#[test]
#[expected_failure]
fun value_passes_check() {
    abort
}

// 好！
#[test, expected_failure]
fun value_passes_check() {
    abort
}
```

### 不要清理 `expected_failure` 測試 (Do Not Clean Up `expected_failure` Tests) {#do-not-clean-up-expected_failure-tests}

```move
// bad! 清理是不必要的
#[test, expected_failure(abort_code = my_app::EIncorrectValue)]
fun try_take_missing_object_fail() {
    let mut test = test_scenario::begin(@0);
    my_app::call_function(test.ctx());
    test.end();
}

// good! 容易看出測試預期在哪裡失敗
#[test, expected_failure(abort_code = my_app::EIncorrectValue)]
fun try_take_missing_object_fail() {
    let mut test = test_scenario::begin(@0);
    my_app::call_function(test.ctx());

    abort // will differ from EIncorrectValue
}
```

### 測試模組中的測試函式不要加上 `test_` 前綴 (Do Not Prefix Tests With `test_` in Testing Modules) {#do-not-prefix-tests-with-test_-in-testing-modules}

```move
// bad! 這個模組已經叫做 _tests 了
module my_package::my_module_tests;

#[test]
fun test_this_feature() { /* ... */ }

// good! 因為結果而有更好的函式名稱
#[test]
fun this_feature_works() { /* ... */ }
```

### 非必要時不要使用 `TestScenario` (Do Not Use `TestScenario` Where Not Necessary) {#do-not-use-testscenario-where-not-necessary}

```move
// bad! 不需要，只用到 ctx
let mut test = test_scenario::begin(@0);
let nft = app::mint(test.ctx());
app::destroy(nft);
test.end();

// good! 對於簡單情況有一個 dummy context
let ctx = &mut tx_context::dummy();
app::mint(ctx).destroy();
```

### 測試中的 `assert!` 不要使用錯誤代碼 (Do Not Use Abort Codes in `assert!` in Tests) {#do-not-use-abort-codes-in-assert-in-tests}

```move
// bad! 可能會意外匹配到應用程式的錯誤代碼
assert!(is_success, 0);

// 好！
assert!(is_success);
```

### 盡量使用 `assert_eq!` (Use `assert_eq!` Whenever Possible) {#use-assert_eq-whenever-possible}

```move
// bad! 舊式程式碼
assert!(result == "expected_value", 0);

// good! 如果失敗會印出兩個值
use std::unit_test::assert_eq;

assert_eq!(result, expected_value);
```

### 使用「黑洞」`destroy` 函式 (Use "Black Hole" `destroy` Function) {#use-black-hole-destroy-function}

```move
// 差！
nft.destroy_for_testing();
app.destroy_for_testing();

// good! - 不需要定義特殊的函式來做清理
use sui::test_utils::destroy;

destroy(nft);
destroy(app);
```

## 註解 (Comments) {#comments}

### 文件註解以 `///` 開頭 (Doc Comments Start With `///`) {#doc-comments-start-with}

```move
// bad! 工具鏈不支援 JavaDoc 風格的註解
/**
 * Cool method
 * @param ...
 */
public fun do_something() { /* ... */ }

// good! 會在 docgen 和 IDE 中被呈現為文件註解
/// 酷方法！
public fun do_something() { /* ... */ }
```

### 邏輯複雜？留個 `//` 註解 (Complex Logic? Leave a Comment `//`) {#complex-logic-leave-a-comment}

友善一點，幫助 reviewer 理解程式碼！

```move
// 好！
// Note: 如果一個值小於 10 可能會 underflow。
// TODO: 在這裡加一個 `assert!`
let value = external_call(value, ctx);
```
