---
title: '帶標籤的控制流 (Labeled Control Flow) | 參考手冊'
description: "Move 帶標籤的控制流參考手冊：命名循環和區塊、帶標籤的 break，以及從命名區塊 return。"
---

# 帶標籤的控制流 (Labeled Control Flow)

Move 在編寫循環和程式碼區塊時支援帶標籤的控制流，允許你對循環執行 `break` 和 `continue`，以及從區塊中 `return`（這在存在巨集的情況下特別有用）。

## 循環 (Loops)

循環標籤允許你定義並將控制權轉移到函式中的特定標籤。例如，我們可以巢狀兩個循環，並在這些標籤上使用 `break` 和 `continue` 來精確指定控制流。你可以在任何 `loop` 或 `while` 形式前加上 `'label:` 形式，以便直接在那裡進行中斷或繼續。

為了演示這種行為，考慮一個函式，它接受數字的巢狀向量（即 `vector<vector<u64>>`），以便針對某個閾值進行加總，其行為如下：

- 如果所有數字的總和低於閾值，則回傳該總和。
- 如果將數字添加到當前總和會超過閾值，則回傳當前總和。

我們可以透過將向量的向量作為巢狀循環進行迭代並標記外部循環來編寫此功能。如果內部循環中的任何添加會使我們超過閾值，我們可以使用帶有外部標籤的 `break` 來同時逃離兩個循環：

```move
fun sum_until_threshold(input: &vector<vector<u64>>, threshold: u64): u64 {
    let mut sum = 0;
    let mut i = 0;
    let input_size = input.length();

    'outer: loop {
        // 中斷至 outer 標籤，因為它是最近的封閉循環
        if (i >= input_size) break sum;

        let vec = &input[i];
        let size = vec.length();
        let mut j = 0;

        while (j < size) {
            let v_entry = vec[j];
            if (sum + v_entry < threshold) {
                sum = sum + v_entry;
            } else {
                // 我們看到的下一個元素會突破閾值，
                // 因此我們回傳當前總和
                break 'outer sum
            };
            j = j + 1;
        };
        i = i + 1;
    }
}
```

這類標籤也可以用於巢狀循環形式，在較大的程式碼主體中提供精確控制。例如，如果我們正在處理一個大型表格，其中每個項目都需要可能看到我們繼續內部或外部循環的迭代，我們可以使用標籤來表達：

```move
let x = 'outer: loop {
    ...
    'inner: while (cond) {
        ...
        if (cond0) { break 'outer value };
        ...
        if (cond1) { continue 'inner }
        else if (cond2) { continue 'outer }
        ...
    }
        ...
};
```

> 使用巨集 (Macros) 而非循環 (Loops) 是一種更好的方式，同樣地，使用 `return` 來控制流程。
> 就像上面的函式 `sum_until_threshold`，可以使用 `macro` 重寫：
```move
fun sum_until_threshold(input: &vector<vector<u64>>, threshold: u64): u64 {
    'outer: {
        (*input).fold!(0, |sum, inner_vec| {
            inner_vec.fold!(sum, |sum, num| if (sum + num < threshold) sum + num else return 'outer sum)
        })
    }
}
```

## 命名區塊 (Labeled Blocks)

帶標籤的區塊允許你編寫包含函式內非局部 (non-local) 控制流的 Move 程式，包括在巨集 lambda 內部以及回傳數值：

```move
fun named_return(n: u64): vector<u8> {
    let x = 'a: {
        if (n % 2 == 0) {
            return 'a b"even"
        };
        b"odd"
    };
    x
}
```

在這個簡單的範例中，程式檢查輸入 `n` 是否為偶數。如果是，程式將帶著數值 `b"even"` 離開標記為 `'a:` 的區塊。如果不是，程式碼將繼續，並以數值 `b"odd"` 結束標記為 `'a:` 的區塊。最後，我們將 `x` 設置為該數值並回傳。

這種控制流功能也跨越巨集主體。例如，假設我們想編寫一個函式來尋找向量中第一個偶數，且我們有一個 `for_ref` 巨集可以在循環中迭代向量元素：

```move
macro fun for_ref<$T>($vs: &vector<$T>, $f: |&$T|) {
    let vs = $vs;
    let mut i = 0;
    let end = vs.length();
    while (i < end) {
        $f(vs.borrow(i));
        i = i + 1;
    }
}
```

利用 `for_ref` 和標籤，我們可以編寫一個傳遞給 `for_ref` 的 lambda 表達式，該表達式將逃離循環，並回傳它找到的第一個偶數：

```move
fun find_first_even(vs: vector<u64>): Option<u64> {
    'result: {
        for_ref!(&vs, |n| if (*n % 2 == 0) { return 'result option::some(*n)});
        option::none()
    }
}
```

此函式將迭代 `vs` 直到找到偶數，並回傳該數值（如果不存在偶數則回傳 `option::none()`）。這使得命名標籤成為與控制流巨集（如 `for!`）交互的強大工具，允許你在這些上下文中自定義迭代行為。

## 限制

為了釐清程式行為，你只能在循環標籤中使用 `break` 和 `continue`，而 `return` 僅適用於區塊標籤。為此，以下程式會產生錯誤：

```move
fun bad_loop() {
    'name: loop {
        return 'name 5
            // ^^^^^ 在循環區塊標籤中無效地使用了 'return'
    }
}

fun bad_block() {
    'name: {
        continue 'name;
              // ^^^^^ 在區塊標籤中無效地使用了 'continue'
        break 'name;
           // ^^^^^ 在區塊標籤中無效地使用了 'break'
    }
}
```
