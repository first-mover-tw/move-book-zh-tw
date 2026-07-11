---
title: 函式 (Functions) | 參考手冊
description:
  Move 函式參考手冊 (Move Functions Reference)：宣告、可見性修飾詞 (Visibility Modifiers)、entry
  函式、回傳值與呼叫慣例。
---

# 函式 (Functions)

函式定義在模組 (Modules) 內部，並定義了該模組的邏輯與行為。函式可以被重複使用，既可以從其他函式中呼叫，也可以作為執行的進入點。

## 宣告

函式使用 `fun` 關鍵字進行宣告，後跟函式名稱、類型參數、參數、回傳類型，最後是函式主體。

```text
<可見性>? <entry>? <macro>? fun <識別碼><[類型參數: 約束],*>([識別碼: 類型],*): <回傳類型> <函式主體>
```

例如：

```move
fun foo<T1, T2>(x: u64, y: T1, z: T2): (T2, T1, u64) { (z, y, x) }
```

### 可見性 (Visibility) {#visibility}

預設情況下，模組函式只能在同一個模組內被呼叫。這些內部（有時稱為私有）函式不能從其他模組呼叫，也不能作為執行的進入點。

```move
module a::m {
    fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效
}

module b::other {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 'foo' 對 'a::m' 是內部的
    }
}
```

若要允許從其他模組存取，函式必須宣告為 `public` 或 `public(package)`。與可見性切線相關的是，[`entry`](#entry-modifier) 函式可以被呼叫作為執行的進入點。

#### `public` 可見性

`public` 函式可以被定義在 _任何_ 模組中的 _任何_ 函式呼叫。如下例所示，`public` 函式可以被以下來源呼叫：

- 定義在同一個模組中的其他函式，
- 定義在另一個模組中的函式，或
- 作為執行的進入點。

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

有關執行進入點的更多細節，請參閱[下方章節](#entry-modifier)。

#### `public(package)` 可見性

`public(package)` 可見性修飾符是 `public` 修飾符的一種更受限形式，旨在對函式的使用位置提供更多控制。`public(package)` 函式可以被以下來源呼叫：

- 定義在同一個模組中的其他函式，或
- 定義在同一個套件 (Package)（相同的地址）中的其他函式。

```move
module a::m {
    public(package) fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效
}

module a::n {
    fun calls_m_foo(): u64 {
        a::m::foo() // 有效，同樣在 `a` 中
    }
}

module b::other {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 'foo' 只能從 `a` 中的模組呼叫
    }
}
```

#### 已棄用：`public(friend)` 可見性

在引入 `public(package)` 之前，`public(friend)` 被用於允許同一個套件中的函式進行有限的公開存取，但必須由被呼叫者的模組顯式列舉允許的模組清單。詳情請參閱 [朋友圈 (Friends)](./friends)。

### `entry` 修飾符 {#entry-modifier}

除了 `public` 函式之外，你的模組中可能還有一些函式想要作為執行的進入點。`entry` 修飾符旨在允許模組函式啟動執行，而無需將功能暴露給其他模組。

從本質上講，`public` 和 `entry` 函式的組合定義了一個模組的「主 (main)」函式，它們指定了 Move 程式可以從何處開始執行。

不過請記住，`entry` 函式 _仍然_ 可以被其他 Move 函式呼叫。因此，雖然它們 _可以_ 作為 Move 程式的起點，但它們並不侷限於這種情況。

例如：

```move
module a::m {
    entry fun foo(): u64 { 0 }
    fun calls_foo(): u64 { foo() } // 有效！
}

module a::n {
    fun calls_m_foo(): u64 {
        a::m::foo() // 錯誤！
//      ^^^^^^^^^^^ 'foo' 對 'a::m' 是內部的
    }
}
```

`entry` 函式的參數和回傳類型可能會受到限制。不過，這些限制具體取決於 Move 的每個個別部署。

[有關 Sui 上 `entry` 函式的文件可以在這裡找到。](https://docs.sui.io/concepts/sui-move-concepts/entry-functions)

為了方便測試，可以從 [`#[test]` 和 `#[test_only]`](./unit-testing) 上下文中呼叫 `entry` 函式。

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

### `macro` 修飾符

與普通函式不同，`macro` (巨集) 函式在執行階段並不存在。相反，這些函式在編譯期間會被內聯 (inline) 替換到每個呼叫點。這些 `macro` 函式利用這種編譯過程提供超出標準函式的功能，例如接受高階的 _lambda_ 風格函式作為參數。這些 lambda 參數同樣在編譯期間展開，允許你將函式主體的部分內容作為參數傳遞給巨集。例如，考慮以下簡單的循環巨集，其中循環主體是以 lambda 形式提供的：

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

欲瞭解更多資訊，請參閱 [巨集 (Macros)](./functions/macros) 章節。

### 名稱

函式名稱可以以字母 `a` 到 `z` 開頭。第一個字元之後，函式名稱可以包含底線 `_`、字母 `a` 到 `z`、字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
fun fOO() {}
fun bar_42() {}
fun bAZ_19() {}
```

### 類型參數

在名稱之後，函式可以擁有類型參數：

```move
fun id<T>(x: T): T { x }
fun example<T1: copy, T2>(x: T1, y: T2): (T1, T1, T2) { (copy x, x, y) }
```

欲瞭解更多細節，請參閱 [Move 泛型 (Generics)](./generics)。

### 參數

函式參數使用本地變數名稱後跟類型標註來宣告：

```move
fun add(x: u64, y: u64): u64 { x + y }
```

我們將其解讀為 `x` 的類型為 `u64`。

一個函式可以完全沒有任何參數。

```move
fun useless() { }
```

這在建立新的或空資料結構的函式中非常常見：

```move
module a::example;

public struct Counter { count: u64 }

fun new_counter(): Counter {
    Counter { count: 0 }
}
```

### 回傳類型

在參數之後，函式會指定其回傳類型。

```move
fun zero(): u64 { 0 }
```

這裡的 `: u64` 表示該函式的回傳類型為 `u64`。

使用 [元組 (Tuples)](./primitive-types/tuples)，函式可以回傳多個數值：

```move
fun one_two_three(): (u64, u64, u64) { (0, 1, 2) }
```

如果未指定回傳類型，函式將具有隱式的單元類型 `()` 作為其回傳類型。以下函式是等價的：

```move
fun just_unit(): () { () }
fun just_unit() { () }
fun just_unit() { }
```

正如在 [元組 (Tuples) 章節](./primitive-types/tuples) 中提到的，這些元組「數值」並不作為執行階段數值存在。這意味著回傳單元類型 `()` 的函式在執行期間不會回傳任何數值。

### 函式主體

函式主體是一個表達式區塊。函式的回傳值是序列中的最後一個值：

```move
fun example(): u64 {
    let mut x = 0;
    x = x + 1;
    x // 回傳 'x'
}
```

有關回傳的更多資訊，請參閱[下方章節](#回傳數值)。

有關表達式區塊的更多資訊，請參閱 [Move 變數 (Variables)](./variables)。

### 原生函式 (Native Functions) {#native-functions}

有些函式沒有指定主體，而是由虛擬機 (VM) 提供主體。這些函式被標記為 `native` (原生)。

在不修改 VM 源程式碼的情况下，程式設計師無法添加新的原生函式。此外，`native` 函式的設計初衷是用於標準程式庫程式碼或該 Move 環境所需的功能。

你可能看到的大多數 `native` 函式都在標準程式庫程式碼中，例如 `vector`。

```move
module std::vector {
    native public fun length<Element>(v: &vector<Element>): u64;
    ...
}
```

## 呼叫

在呼叫函式時，可以透過別名或完全限定名稱來指定函式名稱。

```move
module a::example {
    public fun zero(): u64 { 0 }
}

module b::other {
    use a::example::{Self, zero};
    fun call_zero() {
        // 有了上面的 `use` 語句，所有這些呼叫都是等價的
        a::example::zero();
        example::zero();
        zero();
    }
}
```

呼叫函式時，必須為每個參數提供一個實參 (argument)。

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

類型引數 (Type arguments) 可以被指定，也可以被推導。這兩種呼叫是等價的。

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

欲瞭解更多細節，請參閱 [Move 泛型 (Generics)](./generics)。

## 回傳數值

函式的結果（即其「回傳值」）是其函式主體的最終數值。例如：

```move
fun add(x: u64, y: u64): u64 {
    x + y
}
```

這裡的回傳值是 `x + y` 的結果。

[如前所述](#函式主體)，函式主體是一個 [表達式區塊](./variables)。表達式區塊可以包含各種語句的序列，而區塊中最終的表達式將成為該區塊的數值。

```move
fun double_and_add(x: u64, y: u64): u64 {
    let double_x = x * 2;
    let double_y = y * 2;
    double_x + double_y
}
```

這裡的回傳值是 `double_x + double_y` 的結果。

### `return` 表達式

函式會隱式地回傳其主體求得的數值。不過，函式也可以使用顯式的 `return` 表達式：

```move
fun f1(): u64 { return 0 }
fun f2(): u64 { 0 }
```

這兩個函式是等價的。在這個稍微複雜一點的例子中，函式減去兩個 `u64` 數值，但如果第二個數值太大則提前回傳 `0`：

```move
fun safe_sub(x: u64, y: u64): u64 {
    if (y > x) return 0;
    x - y
}
```

注意，這個函式的主體也可以寫成 `if (y > x) 0 else x - y`。

不過，`return` 的真正亮點在於從深層巢狀的其他控制流結構中退出。在這個範例中，函式遍歷向量以尋找給定數值的索引：

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

使用不帶參數的 `return` 是 `return ()` 的簡寫。也就是說，以下兩個函式是等價的：

```move
fun foo() { return }
fun foo() { return () }
```
