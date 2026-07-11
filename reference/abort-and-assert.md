---
title: 終止與斷言 (Abort and Assert) | 參考手冊
description:
  'Move 中止與斷言參考手冊：以錯誤代碼中止執行、用 assert! 強制條件、處理交易失敗 (Move abort and assert
  reference: halt execution with error codes, enforce conditions with assert!, and
  handle transaction failures)'
---

# 終止與斷言 (Abort and Assert)

[`return`](./functions) 和 `abort` 是兩種結束執行的控制流結構，一個用於當前函式，一個用於整個交易。

[在連結章節中可以找到更多關於 `return` 的資訊](./functions#return-表達式)

## `abort`

`abort` 是一個表達式，它可以不帶參數，也可以只帶一個參數 —— 類型為 `u64` 的 **終止程式碼 (abort code)**。例如：

```move
abort
abort 42
```

`abort` 表達式會停止當前函式的執行，並撤銷當前交易對狀態所做的所有更改（但請注意，這項保證必須由特定 Move 部署的適配器來維護）。沒有「捕捉 (catching)」或以其他方式處理 `abort` 的機制。

幸運的是，Move 中的交易是「全有或全無 (all or nothing)」的，這意味著只有在交易成功時，才會一次性完成對儲存空間的所有更改。對於 Sui 來說，這意味著不會有物件被修改。

由於這種變更的交易式提交機制，在終止之後無需擔心撤銷更改。雖然這種方法缺乏靈活性，但它非常簡單且可預測。

與 [`return`](./functions) 類似，`abort` 在某些條件無法滿足時對於退出控制流非常有用。

在這個範例中，函式將從向量中彈出兩個項目，但如果向量中沒有兩個項目，則會提前終止。

```move
fun pop_twice<T>(v: &mut vector<T>): (T, T) {
    if (v.length() < 2) abort 42;
    (v.pop_back(), v.pop_back())
}
```

這在控制流結構的深層處更為有用。例如，此函式檢查向量中的所有數字是否都小於指定的 `bound`。否則終止：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    let mut i = 0;
    let n = v.length();
    while (i < n) {
        let cur = v[i];
        if (cur > bound) abort 42;
        i = i + 1;
    }
}
```

> 將 `macro` 與 `abort` 結合使用：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    v.do_ref!(|num| if (*num > bound) abort 42);
}
```

### `assert`

`assert` 是 Move 編譯器提供的內建巨集操作。它接受兩個參數：類型為 `bool` 的條件和類型為 `u64` 的程式碼。

```move
assert!(條件: bool, 程式碼: u64)
```

由於該操作是一個巨集，因此必須使用 `!` 呼叫。這是為了傳達 `assert` 的參數是按表達式呼叫 (call-by-expression) 的。換句話說，`assert` 不是普通函式，且在字節碼層級並不存在。它在編譯器內部被替換為：

```move
if (條件) () else abort 程式碼
```

`assert` 比單獨使用 `abort` 更常被使用。上面的 `abort` 範例可以使用 `assert` 重寫：

```move
fun pop_twice<T>(v: &mut vector<T>): (T, T) {
    assert!(v.length() >= 2, 42); // 現在使用 'assert'
    (v.pop_back(), v.pop_back())
}
```

以及：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    let mut i = 0;
    let n = v.length();
    while (i < n) {
        let cur = v[i];
        assert!(cur <= bound, 42); // 現在使用 'assert'
        i = i + 1;
    }
}
```

> 將 `macro` 與 `assert` 結合使用：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    v.do_ref!(|num| assert!(*num <= bound, 42));
}
```

請注意，由於操作被替換為此 `if-else` 結構，因此 `code` 參數並不總是會被求值。例如：

```move
assert!(true, 1 / 0)
```

這將不會導致算術錯誤，它等價於：

```move
if (true) () else abort (1 / 0)
```

因此算術表達式永遠不會被評估！

### Move VM 中的終止程式碼

使用 `abort` 時，瞭解 VM 如何使用 `u64` 程式碼非常重要。

通常，在成功執行後，Move VM 以及特定部署的適配器會決定對儲存空間所做的變更。

如果觸發了 `abort`，VM 將轉而指示錯誤。該錯誤將包含兩部分資訊：

- 產生終止的模組（套件/地址值和模組名稱）
- 終止程式碼。

例如：

```move
module 0x2::example {
    public fun aborts() {
        abort 42
    }
}

module 0x3::invoker {
    public fun always_aborts() {
        0x2::example::aborts()
    }
}
```

如果一筆交易（例如上面的函式 `always_aborts`）呼叫了 `0x2::example::aborts`，VM 將產生一個錯誤，指出模組 `0x2::example` 和程式碼 `42`。

這對於在一個模組中將多個相關的終止操作分組在一起非常有用。

在這個範例中，該模組在多個函式中使用了兩個不同的錯誤程式碼：

```move
module 0::example;

use std::vector;

const EEmptyVector: u64 = 0;
const EIndexOutOfBounds: u64 = 1;

// 將 i 移動到 j，j 移動到 k，k 移動到 i
public fun rotate_three<T>(v: &mut vector<T>, i: u64, j: u64, k: u64) {
    let n = v.length();
    assert!(n > 0, EEmptyVector);
    assert!(i < n, EIndexOutOfBounds);
    assert!(j < n, EIndexOutOfBounds);
    assert!(k < n, EIndexOutOfBounds);

    v.swap(i, k);
    v.swap(j, k);
}

public fun remove_twice<T>(v: &mut vector<T>, i: u64, j: u64): (T, T) {
    let n = v.length();
    assert!(n > 0, EEmptyVector);
    assert!(i < n, EIndexOutOfBounds);
    assert!(j < n, EIndexOutOfBounds);
    assert!(i > j, EIndexOutOfBounds);

    (v.remove(i), v.remove(j))
}
```

## `abort` 的類型

`abort i` 表達式可以具有任何類型！這是因為這兩種建構都打破了正常的控制流，因此它們永遠不需要求值為該類型的數值。

以下內容雖然沒什麼用，但可以通過類型檢查：

```move
let y: address = abort 0;
```

此行為在某些情況下很有幫助，例如你有一個分支指令，在某些分支上產生數值，但在其他分支上不產生。例如：

```move
let b =
    if (x == 0) false
    else if (x == 1) true
    else abort 42;
//       ^^^^^^^^ `abort 42` 具有類型 `bool`
```
