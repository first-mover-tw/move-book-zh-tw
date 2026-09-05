---
description: Move 原始碼品質檢查清單：依據目前的安全性、風格與可維護性最佳實務，檢閱你的 Sui 智慧合約。
title: 程式碼品質檢查清單 (Code Quality Checklist)
keywords:
  - Move
  - Sui
  - Move tutorial
  - code
  - quality
  - checklist
questions:
  - What is Code Quality Checklist in Move?
  - How do I use Code Quality Checklist in Move?
  - What is Code Organization in Move?
  - What is Package Manifest in Move?
answer: 'Move code quality checklist: review your Sui smart contracts against current best practices for safety, style, and maintainability.'
goal:
  description: 'Reader understands move code quality checklist: review your Sui smart contracts against current best practices for safety, style, and maintainability'
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

# 原始碼品質檢查清單 (Code Quality Checklist) {#code-quality-checklist}

Move 語言及其生態系統的快速演進，已使許多較舊的實務做法過時。本指南作為開發者檢視其原始碼的檢查清單，以確保其符合目前 Move 開發的最佳實務。請仔細閱讀，並盡可能將更多建議套用至你的原始碼。

## 原始碼組織 (Code Organization) {#code-organization}

本指南提到的部分問題可以透過使用 [Move Formatter](https://www.npmjs.com/package/@mysten/prettier-plugin-move) 解決，可將其作為 CLI 工具使用、[作為 CI 檢查](https://github.com/marketplace/actions/move-formatter)，或[作為 VSCode（Cursor）的外掛程式](https://marketplace.visualstudio.com/items?itemName=mysten.prettier-move)。

## 套件清單 (Package Manifest) {#package-manifest}

### 使用正確版本 (Use Right Edition) {#use-right-edition}

本指南中的所有功能都需要 Move 2024 版本，且必須在套件清單中指定。

```toml
[package]
name = "my_package"
edition = "2024.beta" # 或（僅）使用 "2024"
```

### 隱含的框架依賴項 (Implicit Framework Dependency) {#implicit-framework-dependency}

從 Sui 1.45 開始，你不再需要在 `Move.toml` 中指定框架依賴項：

```toml
# 舊版，1.45 之前
[dependencies]
Sui = { ... }

# 現代作法：Sui、Bridge、MoveStdlib 和 SuiSystem 會隱含匯入！
[dependencies]
```

### 為具名地址加上前綴 (Prefix Named Addresses) {#prefix-named-addresses}

如果你的套件名稱很通用（例如 `token`）——尤其是專案包含多個套件時——請務必為具名地址加上前綴：

```toml
# 不佳！無法表示任何意義，也可能造成衝突
[addresses]
math = "0x0"

# 良好！清楚表明專案，不太可能發生衝突
[addresses]
my_protocol_math = "0x0"
```

## 匯入、模組與常數 (Imports, Module and Constants) {#imports-module-and-constants}

### 使用模組標籤 (Using Module Label) {#using-module-label}

```move
// 不佳：會增加縮排，舊版風格
module my_package::my_module {
    public struct A {}
}

// 良好！
module my_package::my_module;

public struct A {}
```

### `use` 陳述式中不單獨使用 `Self` (No Single `Self` in `use` Statements) {#no-single-self-in-use-statements}

```move
// 正確：成員 + self 匯入
use my_package::other::{Self, OtherMember};

// 不佳！`{Self}` 是多餘的
use my_package::my_module::{Self};

// 良好！
use my_package::my_module;
```

### 使用 `Self` 分組 `use` 陳述式 (Group `use` Statements with `Self`) {#group-use-statements-with-self}

```move
// 不佳！
use my_package::my_module;
use my_package::my_module::OtherMember;

// 良好！
use my_package::my_module::{Self, OtherMember};
```

### 錯誤常數採用 `EPascalCase` (Error Constants Are in `EPascalCase`) {#error-constants-are-in-epascalcase}

```move
// 不佳！全大寫用於一般常數
const NOT_AUTHORIZED: u64 = 0;

// 良好！清楚表示這是錯誤常數
const ENotAuthorized: u64 = 0;
```

### 一般常數採用 `ALL_CAPS` (Regular Constants Are `ALL_CAPS`) {#regular-constants-are-all_caps}

```move
// 不佳！PascalCase 與錯誤常數相關
const MyConstant: vector<u8> = "my const";

// 良好！清楚表示這是常數值
const MY_CONSTANT: vector<u8> = "my const";
```

## 結構 (Structs) {#structs}

### 功能憑證以 `Cap` 為後綴 (Capabilities are Suffixed with `Cap`) {#capabilities-are-suffixed-with-cap}

```move
// 不佳！若是功能憑證，請加上 `Cap` 後綴
public struct Admin has key, store {
    id: UID,
}

// 良好！審查者知道可從型別預期什麼
public struct AdminCap has key, store {
    id: UID,
}
```

### 名稱中不要使用 `Potato` (No `Potato` in Names) {#no-potato-in-names}

```move
// 不佳！它沒有能力，我們已經知道它是 Hot-Potato 型別
public struct PromisePotato {}

// 良好！
public struct Promise {}
```

### 事件應以過去式命名 (Events Should Be Named in Past Tense) {#events-should-be-named-in-past-tense}

```move
// 不佳！不清楚這個結構的用途
public struct RegisterUser has copy, drop { user: address }

// 良好！很明確，這是一個事件
public struct UserRegistered has copy, drop { user: address }
```

### 動態欄位鍵使用位置結構與 `Key` 後綴 (Use Positional Structs for Dynamic Field Keys + `Key` Suffix) {#use-positional-structs-for-dynamic-field-keys-key-suffix}

```move
// 不算太差，但違反了標準風格
public struct DynamicField has copy, drop, store {}

// 良好！標準風格，使用 Key 後綴
public struct DynamicFieldKey() has copy, drop, store;
```

## 函式 (Functions) {#functions}

### 不使用 `public entry`，僅使用 `public` 或 `entry` (No `public entry`, Only `public` or `entry`) {#no-public-entry-only-public-or-entry}

```move
// 不佳！函式可在交易中呼叫，不需要 entry
public entry fun do_something() { /* ... */ }

// 良好！public 函式更具彈性，可以回傳值
public fun do_something_2(): T { /* ... */ }
```

### 為 PTB 撰寫可組合函式 (Write Composable Functions for PTBs) {#write-composable-functions-for-ptbs}

```move
// 不佳！不可組合，較難測試！
public fun mint_and_transfer(ctx: &mut TxContext) {
    /* ... */
    transfer::transfer(nft, ctx.sender());
}

// 良好！可組合！
public fun mint(ctx: &mut TxContext): NFT { /* ... */ }

// 良好！刻意設計為不可組合
entry fun mint_and_keep(ctx: &mut TxContext) { /* ... */ }
```

### 物件優先（Clock 除外） (Objects Go First (Except for Clock)) {#objects-go-first-except-for-clock}

```move
// 不佳！難以閱讀！
public fun call_app(
    value: u8,
    app: &mut App,
    is_smth: bool,
    cap: &AppCap,
    clock: &Clock,
    ctx: &mut TxContext,
) { /* ... */ }

// 良好！
public fun call_app(
    app: &mut App,
    cap: &AppCap,
    value: u8,
    is_smth: bool,
    clock: &Clock,
    ctx: &mut TxContext,
) { /* ... */ }
```

### 能力物件置於第二位 (Capabilities Go Second) {#capabilities-go-second}

```move
// 不佳！破壞方法關聯性
public fun authorize_action(cap: &AdminCap, app: &mut App) { /* ... */ }

// 良好！讓 Cap 在函式簽章中保持可見，並維持 `.calls()`
public fun authorize_action(app: &mut App, cap: &AdminCap) { /* ... */ }
```

### 取值函式以欄位名稱加上 `_mut` 命名 (Getters Named After Field + `_mut`) {#getters-named-after-field-_mut}

```move
// 不佳！不必要的 `get_`
public fun get_name(u: &User): String { /* ... */ }

// 良好！明確表示其存取 `name` 欄位
public fun name(u: &User): String { /* ... */ }

// 良好！可變參考使用 `_mut`
public fun details_mut(u: &mut User): &mut Details { /* ... */ }
```

## 函式主體：結構方法 (Function Body: Struct Methods) {#function-body-struct-methods}

### 常見的 Coin 操作 (Common Coin Operations) {#common-coin-operations}

```move
// 不佳！舊版原始碼，難以閱讀！
let paid = coin::split(&mut payment, amount, ctx);
let balance = coin::into_balance(paid);

// 良好！結構方法讓操作更容易！
let balance = payment.split(amount, ctx).into_balance();

// 更佳（在此範例中，無須建立暫存 Coin）
let balance = payment.balance_mut().split(amount);

// 也可以這樣做！
let coin = balance.into_coin(ctx);
```

### 請勿匯入 `std::string::utf8` (Do Not Import `std::string::utf8`) {#do-not-import-stdstringutf8}

```move
// 不佳！很遺憾，這非常常見！
use std::string::utf8;

let str = utf8(b"hello, world!");

// 良好！字面值會在編譯時期檢查
let str: String = "hello, world!";

// 也適用於 ASCII 字串
let ascii: ascii::String = "hello, world!";
```

> `vector<u8>` 上的 `.to_string()` 與 `.to_ascii_string()` 方法仍有其用途——
> 用於轉換在編譯時期未知的位元組。對於字面值，請優先使用字串字面值
> 語法。

### UID 具有 `delete` (UID has `delete`) {#uid-has-delete}

```move
// 不佳！
object::delete(id);

// 良好！
id.delete();
```

### `ctx` 具有 `sender()` (`ctx` has `sender()`) {#ctx-has-sender}

```move
// 不佳！
tx_context::sender(ctx);

// 良好！
ctx.sender()
```

### Vector 具有字面值與關聯函式 (Vector Has a Literal. And Associated Functions) {#vector-has-a-literal-and-associated-functions}

```move
// 不佳！
let mut my_vec = vector::empty();
vector::push_back(&mut my_vec, 10);
let first_el = vector::borrow(&my_vec);
assert!(vector::length(&my_vec) == 1);

// 良好！
let mut my_vec = vector[10];
let first_el = my_vec[0];
assert!(my_vec.length() == 1);
```

### 集合支援索引語法 (Collections Support Index Syntax) {#collections-support-index-syntax}

```move
let x: VecMap<u8, String> = /* ... */;

// 不佳！
x.get(&10);
x.get_mut(&10);

// 良好！
&x[&10];
&mut x[&10];
```

## Option 到巨集 (Option -> Macros) {#option---macros}

### 解構並呼叫函式 (Destroy And Call Function) {#destroy-and-call-function}

```move
// 不佳！
if (opt.is_some()) {
    let inner = opt.destroy_some();
    call_function(inner);
};

// 良好！有對應的巨集！
opt.do!(|value| call_function(value));
```

### 使用預設值解構 Some (Destroy Some With Default) {#destroy-some-with-default}

```move
let opt = option::none();

// 不佳！
let value = if (opt.is_some()) {
    opt.destroy_some()
} else {
    abort EError
};

// 良好！有對應的巨集！
let value = opt.destroy_or!(default_value);

// 你甚至可以在 `none` 時中止
let value = opt.destroy_or!(abort ECannotBeEmpty);
```

## 迴圈 -> 巨集 (Loops -> Macros) {#loops---macros}

### 執行操作 N 次 (Do Operation N Times) {#do-operation-n-times}

```move
// 不佳！難以閱讀！
let mut i = 0;
while (i < 32) {
    do_action();
    i = i + 1;
};

// 良好！任何 uint 都有這個巨集！
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
// 不佳！
let mut i = 0;
while (i < vec.length()) {
    call_function(&vec[i]);
    i = i + 1;
};

// 良好！
vec.do_ref!(|e| call_function(e));
```

### 銷毀向量並對每個元素呼叫函式 (Destroy a Vector and Call a Function on Each Element) {#destroy-a-vector-and-call-a-function-on-each-element}

```move
// 不佳！
while (!vec.is_empty()) {
    call(vec.pop_back());
};

// 良好！
vec.destroy!(|e| call(e));
```

### 將向量摺疊為單一值 (Fold Vector Into a Single Value) {#fold-vector-into-a-single-value}

```move
// 不佳！
let mut aggregate = 0;
let mut i = 0;

while (i < source.length()) {
    aggregate = aggregate + source[i];
    i = i + 1;
};

// 良好！
let aggregate = source.fold!(0, |acc, v| {
    acc + v
});
```

### 篩選向量的元素 (Filter Elements of the Vector) {#filter-elements-of-the-vector}

> 注意：`source` 向量中的 `T: drop`

```move
// 不佳！
let mut filtered = [];
let mut i = 0;
while (i < source.length()) {
    if (source[i] > 10) {
        filtered.push_back(source[i]);
    };
    i = i + 1;
};

// 良好！
let filtered = source.filter!(|e| e > 10);
```

## 其他 (Other) {#other}

### 解構中的忽略值可完全省略 (Ignored Values In Unpack Can Be Ignored Altogether) {#ignored-values-in-unpack-can-be-ignored-altogether}

```move
// 不好！非常稀疏！
let MyStruct { id, field_1: _, field_2: _, field_3: _ } = value;
id.delete();

// 好！2024 語法
let MyStruct { id, .. } = value;
id.delete();
```

## 測試 (Testing) {#testing}

### 合併 `#[test]` 與 `#[expected_failure(...)]` (Merge `#[test]` and `#[expected_failure(...)]`) {#merge-test-and-expected_failure}

```move
// 不佳！
#[test]
#[expected_failure]
fun value_passes_check() {
    abort
}

// 良好！
#[test, expected_failure]
fun value_passes_check() {
    abort
}
```

### 請勿清理 `expected_failure` 測試 (Do Not Clean Up `expected_failure` Tests) {#do-not-clean-up-expected_failure-tests}

```move
// 不佳！無須清理
#[test, expected_failure(abort_code = my_app::EIncorrectValue)]
fun try_take_missing_object_fail() {
    let mut test = test_scenario::begin(@0);
    my_app::call_function(test.ctx());
    test.end();
}

// 良好！容易看出預期在哪裡失敗
#[test, expected_failure(abort_code = my_app::EIncorrectValue)]
fun try_take_missing_object_fail() {
    let mut test = test_scenario::begin(@0);
    my_app::call_function(test.ctx());

    abort // 將與 EIncorrectValue 不同
}
```

### 測試模組中的測試函式請勿以 `test_` 為前綴 (Do Not Prefix Tests With `test_` in Testing Modules) {#do-not-prefix-tests-with-test_-in-testing-modules}

```move
// 不佳！模組已命名為 _tests
module my_package::my_module_tests;

#[test]
fun test_this_feature() { /* ... */ }

// 良好！因此可使用更好的函式名稱
#[test]
fun this_feature_works() { /* ... */ }
```

### 非必要時請勿使用 `TestScenario` (Do Not Use `TestScenario` Where Not Necessary) {#do-not-use-testscenario-where-not-necessary}

```move
// 不佳！不需要，僅使用 ctx
let mut test = test_scenario::begin(@0);
let nft = app::mint(test.ctx());
app::destroy(nft);
test.end();

// 良好！簡單情況有虛擬 context 可用
let ctx = &mut tx_context::dummy();
app::mint(ctx).destroy();
```

### 測試中的 `assert!` 請勿使用中止碼 (Do Not Use Abort Codes in `assert!` in Tests) {#do-not-use-abort-codes-in-assert-in-tests}

```move
// 不佳！可能意外符合應用程式錯誤碼
assert!(is_success, 0);

// 良好！
assert!(is_success);
```

### 盡可能使用 `assert_eq!` (Use `assert_eq!` Whenever Possible) {#use-assert_eq-whenever-possible}

```move
// 不佳！舊式原始碼
assert!(result == "expected_value", 0);

// 良好！若失敗將印出兩個值
use std::unit_test::assert_eq;

assert_eq!(result, expected_value);
```

### 使用「黑洞」`destroy` 函式 (Use "Black Hole" `destroy` Function) {#use-black-hole-destroy-function}

```move
// 不佳！
nft.destroy_for_testing();
app.destroy_for_testing();

// 良好！無須為清理定義特殊函式
use std::unit_test::destroy;

destroy(nft);
destroy(app);
```

## 註解 (Comments) {#comments}

### 文件註解以 `///` 開頭 (Doc Comments Start With `///`) {#doc-comments-start-with}

```move
// 不佳！工具不支援 JavaDoc 樣式的註解
/**
 * 很酷的方法
 * @param ...
 */
public fun do_something() { /* ... */ }

// 良好！將在 docgen 與 IDE 中顯示為文件註解
/// 很酷的方法！
public fun do_something() { /* ... */ }
```

### 複雜邏輯？留下註解 `//` (Complex Logic? Leave a Comment `//`) {#complex-logic-leave-a-comment}

保持友善，並協助檢閱者理解程式碼！

```move
// 良好！
// 注意：若值小於 10，可能發生下溢位。
// TODO：在此加入 `assert!`
let value = external_call(value, ctx);
```
