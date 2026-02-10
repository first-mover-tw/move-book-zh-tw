# 所有權與作用域 (Ownership and Scope)

Move 中的每個變數都有一個作用域 (Scope) 和一個所有者 (Owner)。作用域是變數有效的程式碼範圍，而所有者是該變數所屬的作用域。一旦所有者作用域結束，變數就會被丟棄 (dropped)。這是 Move 中的一個核心概念，瞭解其運作方式非常重要。

<!--

- Borrow Checker (借用檢查器)
- 提及 Rust 的 borrow checker
- 借用 / 參照簡介

-->

## 所有權 (Ownership)

在函式作用域中定義的變數歸該作用域所有。執行時期會遍歷函式作用域並執行每個表達式和語句。函式作用域結束後，其中定義的變數會被丟棄或釋放。

```move
module book::ownership;

public fun owner() {
    let a = 1; // a 歸 `owner` 函式所有
} // a 在此處被丟棄

public fun other() {
    let b = 2; // b 歸 `other` 函式所有
} // b 在此處被丟棄

#[test]
fun test_owner() {
    owner();
    other();
    // a 和 b 在此處無效
}
```

在上面的範例中，變數 `a` 歸 `owner` 函式所有，變數 `b` 歸 `other` 函式所有。當呼叫這些函式中的每一個時，變數被定義；當函式結束時，變數被丟棄。

## 傳回值 (Returning a Value)

如果我們更改 `owner` 函式以傳回變數 `a`，則 `a` 的所有權將轉移給該函式的呼叫者。

```move
module book::ownership;

public fun owner(): u8 {
    let a = 1; // a 在此處定義
    a // 作用域結束，a 被傳回
}

#[test]
fun test_owner() {
    let a = owner();
    // a 在此處有效
} // a 在此處被丟棄
```

## 按值傳遞 (Passing by Value)

此外，如果我們將變數 `a` 傳遞給另一個函式，`a` 的所有權將轉移給該函式。在執行此操作時，我們將值從一個作用域 **移動 (move)** 到另一個作用域。這也被稱為 **移動語意 (move semantics)**。

```move
module book::ownership;

public fun owner(): u8 {
    let a = 10;
    a
} // a 被傳回

public fun take_ownership(v: u8) {
    // v 歸 `take_ownership` 所有
} // v 在此處被丟棄

#[test]
fun test_owner() {
    let a = owner();
    // `u8` 是可複製的，呼叫函式時使用 `move a` 以強制轉移其所有權
    take_ownership(move a);
    // a 在此處無效
}
```

## 區塊作用域 (Scopes with Blocks)

每個函式都有一個主作用域，它也可以透過使用區塊 (blocks) 擁有子作用域。區塊是一系列的語句和表達式，它有自己的作用域。在區塊中定義的變數歸該區塊所有，當區塊結束時，變數被丟棄。

```move
module book::ownership;

public fun owner() {
    let a = 1; // a 歸 `owner` 函式的作用域所有
    {
        let b = 2; // 宣告 b 的區塊擁有它
        {
            let c = 3; // 宣告 c 的區塊擁有它
        }; // c 在此處被丟棄
    }; // b 在此處被丟棄
    // a = b; // 錯誤：b 在此處無效
    // a = c; // 錯誤：c 在此處無效
} // a 在此處被丟棄
```

發但也，如果我們從區塊中傳回一個值，則變數的所有權將轉移給該區塊的呼叫者。

```move
module book::ownership;

public fun owner(): u8 {
    let a = 1; // a 歸 `owner` 函式的作用域所有
    let b = {
        let c = 2; // 宣告 c 的區塊擁有它
        c // c 從區塊中傳回並轉移給 b
    };
    a + b // a 和 b 在此處均有效
}
```

## 可複製類型 (Copyable Types)

Move 中的某些類型是 **可複製的 (copyable)**，這意味著它們可以被複製而無需轉移所有權。這對於體積小且複製成本低的類型（如整數和布林值）非常有用。當這些類型被傳遞給函式、從函式傳回，或者當它們被「移動」到另一個作用域然後在其原始作用域中被存取時，Move 編譯器會自動複製這些類型。

## 延伸閱讀

- Move 參考手冊中的 [局部變數與作用域](./../../reference/variables)。
