---
title: 函式 (Functions) | 參考手冊
description: Move 函式 (functions) 參考：宣告 (declaration)、可見性修飾詞 (visibility modifiers)、入口函式 (entry functions)、回傳值 (return values) 與呼叫慣例 (calling conventions)。
keywords:
  - Move
  - Sui
  - Move reference
  - functions
  - reference
questions:
  - How does Functions work in Move?
  - What is the syntax for Functions in Move?
  - What is Declaration in Move?
  - What is Calling in Move?
answer: 'Move functions reference: declaration, visibility modifiers, entry functions, return values, and calling conventions.'
goal:
  description: 'Reader understands move functions reference: declaration, visibility modifiers, entry functions, return values, and calling conventions'
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

# 函式 (Functions) {#functions}

函式會在模組內宣告，並定義模組的邏輯與行為。函式可重複使用，可由其他函式呼叫，或作為執行的入口點。

## 宣告 (Declaration) {#declaration}

函式會使用 `fun` 關鍵字宣告，後接函式名稱、型別參數、
參數、回傳型別，以及最後的函式主體。

```text
<visibility>? <entry>? <macro>? fun <identifier><[type_parameters: constraint],*>([identifier: type],*): <return_type> <function_body>
```

例如：

```move
fun foo<T1, T2>(x: u64, y: T1, z: T2): (T2, T1, u64) { (z, y, x) }
```

### 可見性 (Visibility) {#visibility}

預設情況下，模組函式只能在同一個模組內呼叫。這些內部（有時稱為私有）函式無法從其他模組或作為入口函式呼叫。

```move
module a::m {
    fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效
}

module b::other {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 'foo' 是 'a::m' 的內部函式
    }
}
```

若要允許其他模組存取，函式必須宣告為 `public` 或 `public(package)`。
與可見性相關的是，[`entry`](#entry-modifier) 函式可作為執行的入口函式呼叫。

#### `public` 可見性 (`public` visibility) {#public-visibility}

`public` 函式可由定義於*任何*模組中的*任何*函式呼叫。如以下範例所示，
`public` 函式可由下列方式呼叫：

- 定義於同一模組中的其他函式，
- 定義於另一個模組中的函式，或
- 作為執行的入口函式。

```move
module a::m {
    public fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效
}

module b::other {
    fun calls_m_foo(): u64 {
        a::m::foo() // 有效
    }
}
```

如需執行入口函式的更多詳細資訊，請參閱[下方章節](#entry-modifier)。

#### `public(package)` 可見性 (`public(package)` visibility) {#publicpackage-visibility}

`public(package)` 可見性修飾詞是 `public` 修飾詞較受限制的形式，可更精確地控制函式可在何處使用。`public(package)` 函式可由下列方式呼叫：

- 定義於同一模組中的其他函式，或
- 定義於同一套件（相同地址）中的其他函式

```move
module a::m {
    public(package) fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效
}

module a::n {
    fun calls_m_foo(): u64 {
        a::m::foo() // 有效，也位於 `a` 中
    }
}

module b::other {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 只能從 `a` 中的模組呼叫 'foo'
    }
}
```

#### 已棄用的 `public(friend)` 可見性 (DEPRECATED `public(friend)` visibility) {#deprecated-publicfriend-visibility}

在新增 `public(package)` 之前，`public(friend)` 用於允許同一套件中的函式具有受限的公開存取權，但允許的模組清單必須由被呼叫函式的模組明確列舉。如需更多詳細資訊，請參閱[Friends](./friends)。

### `entry` 修飾詞 (`entry` modifier) {#entry-modifier}

除了 `public` 函式之外，你的模組中可能還有一些函式想作為執行的進入點使用。`entry` 修飾詞旨在讓模組函式能夠啟動執行，而不必將功能公開給其他模組。

本質上，`public` 與 `entry` 函式的組合定義了模組的「主要」函式，並指定 Move 程式可從何處開始執行。

但請記住，`entry` 函式*仍然可以*由其他 Move 函式呼叫。因此，雖然它們*可以*作為 Move 程式的起點，但並不僅限於該情況。

例如：

```move
module a::m {
    entry fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效！
}

module a::n {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 'foo' 是 'a::m' 的內部函式
    }
}
```

`entry` 函式的參數與回傳型別可能會受到限制。不過，這些限制取決於 Move 的個別部署版本。

[你可以在此找到 Sui 上 `entry` 函式的文件。](https://docs.sui.io/concepts/sui-move-concepts#entry-functions)

為了讓測試更容易進行，可以從
[`#[test]` 與 `#[test_only]`](./unit-testing) 情境中呼叫 `entry` 函式。

```move
module a::m {
    entry fun foo(): u64 { 0 }
}
module a::m_test {
    #[test]
    fun my_test(): u64 { a::m::foo() } // 有效！
    #[test_only]
    fun my_test_helper(): u64 { a::m::foo() } // 有效！
}
```

### `macro` 修飾詞 (`macro` modifier) {#macro-modifier}

不同於一般函式，`macro` 函式在執行階段並不存在。這些函式會在編譯期間，於每個呼叫位置以內嵌方式替換。這些 `macro` 函式利用此編譯程序提供超越標準函式的功能，例如接受高階的 _lambda_ 風格函式作為引數。這些 lambda 引數也會在編譯期間展開，讓你能將函式主體的部分內容作為引數傳遞給巨集。例如，請考慮以下簡單的迴圈巨集，其中迴圈主體會以 lambda 提供：

```move
macro fun n_times($n: u64, $body: |u64| -> ()) {
    let n = $n;
    let mut i = 0;
    while (i < n) {
        $body(i);
        i = i + 1;
    }
}

fun example() {
    let mut sum = 0;
    n_times!(10, |x| sum = sum + x );
}
```

如需更多資訊，請參閱 [巨集](./functions/macros) 章節。

### 名稱 (Name) {#name}

函式名稱可以以字母 `a` 到 `z` 開頭。第一個字元之後，函式名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z`，或數字 `0` 到 `9`。

```move
fun fOO() {}
fun bar_42() {}
fun bAZ_19() {}
```

### 型別參數 (Type Parameters) {#type-parameters}

在名稱之後，函式可以具有型別參數。

```move
fun id<T>(x: T): T { x }
fun example<T1: copy, T2>(x: T1, y: T2): (T1, T1, T2) { (copy x, x, y) }
```

如需更多詳細資訊，請參閱 [Move 泛型](./generics)。

### 參數 (Parameters) {#parameters}

函式參數會以區域變數名稱後接型別標註的方式宣告。

```move
fun add(x: u64, y: u64): u64 { x + y }
```

我們將此解讀為 `x` 的型別是 `u64`。

函式完全不一定要有任何參數。

```move
fun useless() { }
```

這對於建立新的或空的資料結構的函式非常常見。

```move
module a::example;

public struct Counter { count: u64 }

fun new_counter(): Counter {
    Counter { count: 0 }
}
```

### 回傳型別 (Return type) {#return-type}

在參數之後，函式會指定其回傳型別。

```move
fun zero(): u64 { 0 }
```

此處的 `: u64` 表示函式的回傳型別為 `u64`。

使用 [元組](./primitive-types/tuples)，函式可以回傳多個值：

```move
fun one_two_three(): (u64, u64, u64) { (0, 1, 2) }
```

如果未指定回傳型別，函式會隱含地使用單位型別 `()` 作為回傳型別。下列
函式彼此等價：

```move
fun just_unit(): () { () }
fun just_unit() { () }
fun just_unit() { }
```

如同在[元組章節](./primitive-types/tuples)中提到，這些元組「值」不會作為
執行階段值存在。這表示回傳單位型別 `()` 的函式在
執行期間不會回傳任何值。

### 函式主體 (Function body) {#function-body}

函式的主體是運算式區塊。函式的回傳值是序列中的最後一個值。

```move
fun example(): u64 {
    let mut x = 0;
    x = x + 1;
    x // 回傳 'x'
}
```

請參閱[下方關於回傳值的章節](#returning-values)，以取得更多資訊。

如需運算式區塊的更多資訊，請參閱 [Move 變數](./variables)。

### 原生函式 (Native Functions) {#native-functions}

有些函式沒有指定函式本體，而是由 VM 提供函式本體。這些
函式會標示為 `native`。

在不修改 VM 原始碼的情況下，程式設計師無法新增原生函式。此外，
`native` 函式的用途是提供標準函式庫原始碼，或提供特定 Move 環境所需的功能。

你最常見到的 `native` 函式大多位於標準函式庫原始碼中，例如 `vector`

```move
module std::vector {
    native public fun length<Element>(v: &vector<Element>): u64;
    ...
}
```

## 呼叫 (Calling) {#calling}

呼叫函式時，可以透過別名或完整限定名稱指定名稱。

```move
module a::example {
    public fun zero(): u64 { 0 }
}

module b::other {
    use a::example::{Self, zero};
    fun call_zero() {
        // 使用上述的 `use` 時，這些呼叫全都等效
        a::example::zero();
        example::zero();
        zero();
    }
}
```

呼叫函式時，必須為每個參數提供引數。

```move
module a::example {
    public fun takes_none(): u64 { 0 }
    public fun takes_one(x: u64): u64 { x }
    public fun takes_two(x: u64, y: u64): u64 { x + y }
    public fun takes_three(x: u64, y: u64, z: u64): u64 { x + y + z }
}

module b::other {
    fun call_all() {
        a::example::takes_none();
        a::example::takes_one(0);
        a::example::takes_two(0, 1);
        a::example::takes_three(0, 1, 2);
    }
}
```

型別引數可以明確指定或由系統推斷。兩種呼叫皆等效。

```move
module a::example {
    public fun id<T>(x: T): T { x }
}

module b::other {
    fun call_all() {
        a::example::id(0);
        a::example::id<u64>(0);
    }
}
```

如需更多詳細資料，請參閱 [Move 泛型](./generics)。

## 回傳值 (Returning values) {#returning-values}

函式的結果，也就是其「回傳值」，是其函式主體的最終值。例如：

```move
fun add(x: u64, y: u64): u64 {
    x + y
}
```

此處的回傳值是 `x + y` 的結果。

[如上所述](#function-body)，函式主體是一個[運算式區塊](./variables)。運算式區塊可以依序執行各種陳述式，而區塊中的最終運算式將會是該區塊的值：

```move
fun double_and_add(x: u64, y: u64): u64 {
    let double_x = x * 2;
    let double_y = y * 2;
    double_x + double_y
}
```

此處的回傳值是 `double_x + double_y` 的結果。

### `return` 運算式 (`return` expression) {#return-expression}

函式會隱含地回傳其主體所評估的值。不過，函式也可以使用明確的 `return` 運算式：

```move
fun f1(): u64 { return 0 }
fun f2(): u64 { 0 }
```

這兩個函式等效。在這個稍微複雜的範例中，函式會將兩個 `u64` 值相減；但若第二個值過大，則會提早回傳 `0`：

```move
fun safe_sub(x: u64, y: u64): u64 {
    if (y > x) return 0;
    x - y
}
```

請注意，此函式的主體也可以寫成 `if (y > x) 0 else x - y`。

不過，`return` 在離開其他控制流程結構的深層位置時特別有用。在此範例中，函式會走訪向量，以尋找指定值的索引：

```move
fun index_of<T>(v: &vector<T>, target: &T): Option<u64> {
    let mut i = 0;
    let n = v.length();
    while (i < n) {
        if (&v[i] == target) return option::some(i);
        i = i + 1
    };

    option::none()
}
```

不帶引數使用 `return` 是 `return ()` 的簡寫。也就是說，下列兩個函式等效：

```move
fun foo() { return }
fun foo() { return () }
```
