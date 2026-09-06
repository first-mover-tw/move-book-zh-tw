---
title: 具標籤的控制流程 (Labeled Control Flow) | 參考手冊
description: Move 標籤控制流程參考手冊：具名迴圈與區塊、使用標籤中斷，以及從具名區塊回傳。
keywords:
  - Move
  - Sui
  - Move reference
  - labeled
  - control
  - flow
  - reference
questions:
  - How does Labeled Control Flow work in Move?
  - What is the syntax for Labeled Control Flow in Move?
  - What is Loops in Move?
  - What is Labeled Blocks in Move?
answer: 'Move labeled control flow reference: named loops and blocks, break with labels, and return from named blocks.'
goal:
  description: 'Reader understands move labeled control flow reference: named loops and blocks, break with labels, and return from named blocks'
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

# 標籤式控制流程 (Labeled Control Flow) {#labeled-control-flow}

Move 在撰寫迴圈與程式碼區塊時支援標籤式控制流程，讓你可以對迴圈使用 `break` 和 `continue`，並從區塊中 `return`（這在使用巨集時尤其有幫助）。

## 迴圈 (Loops) {#loops}

迴圈可讓你在函式中定義並將控制權轉移至特定標籤。例如，我們可以巢狀使用兩個迴圈，並搭配這些標籤使用 `break` 和 `continue`，以精確指定控制流程。你可以在任何 `loop` 或 `while` 形式前加上 `'label:` 形式，以便直接在該處中斷或繼續迴圈。

為了示範此行為，請考慮一個接受巢狀數字向量（即 `vector<vector<u64>>`）並針對某個閾值加總的函式，其行為如下：

- 若所有數字的總和低於閾值，則回傳該總和。
- 若將一個數字加到目前總和會超過閾值，則回傳目前總和。

我們可以透過巢狀迴圈走訪向量的向量，並為外層迴圈加上標籤來撰寫此函式。若內層迴圈中的任何加法會使總和超過閾值，我們可以搭配外層標籤使用 `break`，一次跳出兩個迴圈：

```move
fun sum_until_threshold(input: &vector<vector<u64>>, threshold: u64): u64 {
    let mut sum = 0;
    let mut i = 0;
    let input_size = input.length();

    'outer: loop {
        // 中斷至 outer，因為它是最近的外層迴圈
        if (i >= input_size) break sum;

        let vec = &input[i];
        let size = vec.length();
        let mut j = 0;

        while (j < size) {
            let v_entry = vec[j];
            if (sum + v_entry < threshold) {
                sum = sum + v_entry;
            } else {
                // 下一個遇到的元素會超過閾值，
                // 因此我們回傳目前的總和
                break 'outer sum
            };
            j = j + 1;
        };
        i = i + 1;
    }
}
```

這類標籤也可以搭配巢狀迴圈形式使用，為較大的程式碼主體提供精確控制。例如，若我們正在處理大型資料表，其中每個項目都需要迭代，且可能需要繼續內層或外層迴圈，我們可以使用標籤來表達該程式碼：

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

> 相較於迴圈，這是使用巨集的更好方式；同樣地，可使用 `return` 控制流程。
> 如同上方的 `sum_until_threshold` 函式，可使用 `macro` 改寫它：

```move
fun sum_until_threshold(input: &vector<vector<u64>>, threshold: u64): u64 {
    'outer: {
        (*input).fold!(0, |sum, inner_vec| {
            inner_vec.fold!(sum, |sum, num| if (sum + num < threshold) sum + num else return 'outer sum)
        })
    }
}
```

## 標籤式區塊 (Labeled Blocks) {#labeled-blocks}

標籤式區塊可讓你撰寫包含函式內非區域控制流程的 Move 程式，包括在巨集 lambda 內部以及回傳值：

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

在這個簡單範例中，程式會檢查輸入的 `n` 是否為偶數。若是，程式會以值 `b"even"` 離開標記為 `'a:` 的區塊。若否，程式碼會繼續執行，並以值 `b"odd"` 結束標記為 `'a:` 的區塊。最後，我們將該值設定給 `x`，然後回傳它。

此控制流程功能也可跨越巨集主體運作。例如，假設我們想撰寫一個函式來尋找向量中的第一個偶數，且我們有一個會在迴圈中走訪向量元素的巨集 `for_ref`：

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

使用 `for_ref` 和標籤，我們可以撰寫一個 lambda 運算式並傳遞給 `for_ref`，使其跳出迴圈並回傳找到的第一個偶數：

```move
fun find_first_even(vs: vector<u64>): Option<u64> {
    'result: {
        for_ref!(&vs, |n| if (*n % 2 == 0) { return 'result option::some(*n)});
        option::none()
    }
}
```

此函式會走訪 `vs`，直到找到偶數並回傳該值（若不存在偶數則回傳 `option::none()`）。這使具名標籤成為與 `for!` 等控制流程巨集互動的強大工具，讓你可以在這些情境中自訂迭代行為。

## 限制 (Restrictions) {#restrictions}

為了明確程式行為，你只能將 `break` 和 `continue` 用於迴圈標籤，而 `return` 僅能搭配區塊標籤使用。因此，下列程式會產生錯誤：

```move
fun bad_loop() {
    'name: loop {
        return 'name 5
            // ^^^^^ 將 'return' 用於迴圈區塊標籤的用法無效
    }
}

fun bad_block() {
    'name: {
        continue 'name;
              // ^^^^^ 將 'break' 用於迴圈區塊標籤的用法無效
        break 'name;
           // ^^^^^ 將 'break' 用於迴圈區塊標籤的用法無效
    }
}
```
