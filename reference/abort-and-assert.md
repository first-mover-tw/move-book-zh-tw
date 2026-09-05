---
title: 中止 (Abort) 與斷言 (Assert) | 參考手冊
description: Move 中止 (abort) 與斷言 (assert) 參考：以錯誤碼中止執行、使用 assert! 強制條件，以及處理交易 (transaction) 失敗。
keywords:
  - Move
  - Sui
  - Move reference
  - abort
  - assert
  - reference
  - error handling
questions:
  - How does Abort and Assert work in Move?
  - What is the syntax for Abort and Assert in Move?
  - What is abort in Move?
  - What is The type of abort in Move?
answer: 'Move abort and assert reference: halt execution with error codes, enforce conditions with assert!, and handle transaction failures.'
goal:
  description: 'Reader understands move abort and assert reference: halt execution with error codes, enforce conditions with assert!, and handle transaction failures'
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

# 中止與斷言 (Abort and Assert) {#abort-and-assert}

[`return`](./functions) 與 `abort` 是兩種結束執行的控制流程建構；前者結束目前的函式，後者則結束整筆交易。

更多關於 [`return` 的資訊可在連結章節中找到](./functions#return-expression)

## 中止 (`abort`) {#abort}

`abort` 是一個運算式，可以不接受引數，或只接受一個引數——型別為 `u64` 的**中止代碼**。例如：

```move
abort
abort 42
```

`abort` 運算式會停止目前函式的執行，並還原目前交易對狀態所做的所有變更（但請注意，這項保證必須由特定 Move 部署的轉接器維護）。沒有任何機制可「捕捉」或以其他方式處理 `abort`。

幸運的是，Move 中的交易是全有或全無的，意即只有在交易成功時，才會一次套用所有對儲存空間的變更。對 Sui 而言，這表示不會修改任何物件。

由於這種交易式的變更提交方式，中止後無須擔心要復原變更。雖然這種方法的彈性較低，但非常簡單且可預測。

與 [`return`](./functions) 類似，當某個條件無法滿足時，`abort` 可用於退出控制流程。

在此範例中，函式會從向量移除兩個項目，但如果向量不足兩個項目，便會提早中止

<!-- {{#include ../../packages/reference/sources/abort-and-assert.move}} -->

```move
fun pop_twice<T>(v: &mut vector<T>): (T, T) {
    if (v.length() < 2) abort 42;
    (v.pop_back(), v.pop_back())
}
```

這在控制流程建構的深層位置中更加實用。例如，此函式會檢查向量中的所有數字是否都小於指定的 `bound`。否則便中止。

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

> 將 `macro` 與 `abort` 結合：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    v.do_ref!(|num| if (*num > bound) abort 42);
}
```

### 斷言 (`assert`) {#assert}

`assert` 是由 Move 編譯器提供的內建巨集操作。它接受兩個引數：型別為 `bool` 的條件，以及型別為 `u64` 的代碼。

```move
assert!(condition: bool, code: u64)
```

由於此操作是巨集，必須使用 `!` 呼叫。這表示 `assert` 的引數採運算式呼叫。換言之，`assert` 並非一般函式，且不存在於位元組碼層級。編譯器會將其替換為：

```move
if (condition) () else abort code
```

相較於單獨使用 `abort`，更常使用 `assert`。以上的 `abort` 範例可改寫為使用 `assert`：

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

> 將 `macro` 與 `assert` 結合：

```move
fun check_vec(v: &vector<u64>, bound: u64) {
    v.do_ref!(|num| assert!(*num <= bound, 42));
}
```

請注意，由於此操作會被替換為這個 `if-else`，`code` 的引數並不一定會被求值。例如：

```move
assert!(true, 1 / 0)
```

這不會造成算術錯誤，等同於：

```move
if (true) () else abort (1 / 0)
```

因此，該算術運算式永遠不會被求值！

### Move VM 中的中止代碼 (Abort codes in the Move VM) {#abort-codes-in-the-move-vm}

使用 `abort` 時，了解 VM 如何使用 `u64` 代碼非常重要。

通常在成功執行後，Move VM 與特定部署的轉接器會判定對儲存空間所做的變更。

如果執行到 `abort`，VM 會改為指出一項錯誤。該錯誤包含兩項資訊：

- 產生中止的模組（套件／地址值與模組名稱）
- 中止代碼。

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

如果某筆交易（例如上述的函式 `always_aborts`）呼叫 `0x2::example::aborts`，VM 會產生錯誤，指出模組 `0x2::example` 與代碼 `42`。

這可用於將多個中止集中歸類於同一模組內。

在此範例中，模組有兩個獨立的錯誤代碼，並在多個函式中使用。

```move
module 0::example;

use std::vector;

const EEmptyVector: u64 = 0;
const EIndexOutOfBounds: u64 = 1;

// 將 i 移至 j、將 j 移至 k、將 k 移至 i
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

## `abort` 的型別 (The type of `abort`) {#the-type-of-abort}

`abort i` 運算式可以具有任何型別！這是因為兩種建構都會中斷正常控制流程，因此永遠不需要求值為該型別的值。

以下寫法沒有實際用途，但能通過型別檢查：

```move
let y: address = abort 0;
```

當你有一個分支指令，在部分分支產生值、但並非所有分支都產生值時，這種行為會很有幫助。例如：

```move
let b =
    if (x == 0) false
    else if (x == 1) true
    else abort 42;
//       ^^^^^^^^ `abort 42` 的型別為 `bool`
```
