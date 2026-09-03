---
description: 改善 Move 智慧合約中的錯誤處理：在 Sui 上使用具描述性的中止代碼與錯誤常數以獲得更好的除錯效果。
title: 更好的錯誤處理 (Better Error Handling)
keywords:
  - Move
  - Sui
  - Move tutorial
  - better
  - error
  - handling
  - error handling
questions:
  - What is Better Error Handling in Move?
  - How do I use Better Error Handling in Move?
  - 'What is Rule 1: Handle All Possible Scenarios in Move?'
  - 'What is Rule 2: Abort with Different Codes in Move?'
answer: 'Improve error handling in Move smart contracts: use descriptive abort codes and error constants for better debugging on Sui.'
goal:
  description: 'Reader understands improve error handling in Move smart contracts: use descriptive abort codes and error constants for better debugging on Sui'
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

# 更好的錯誤處理 (Better Error Handling) {#better-error-handling}

每當執行遇到終止時，交易會失敗並將終止代碼回傳給呼叫者。
Move VM 會回傳終止交易的模組名稱與終止代碼。這種行為對交易的呼叫者而言並非完全透明，特別是當單一函式包含多個可能會終止的相同函式呼叫時。在這種情況下，呼叫者將無法得知是哪一次呼叫終止了交易，這會導致除錯困難，或者難以向使用者提供有意義的錯誤訊息。

```move
module book::module_a;

use book::module_b;

public fun do_something() {
    let field_1 = module_b::get_field(1); // 可能會以 0 終止
    /* ... 大量邏輯 ... */
    let field_2 = module_b::get_field(2); // 可能會以 0 終止
    /* ... 更多邏輯 ... */
    let field_3 = module_b::get_field(3); // 可能會以 0 終止
}
```

上述範例說明瞭單一函式包含多個可能終止的呼叫的情況。如果 `do_something` 函式的呼叫者收到終止代碼 `0`，將很難理解是哪一次對 `module_b::get_field` 的呼叫終止了交易。為了常試解決這個問題，有一些常見的模式可以用來改善錯誤處理。

## 規則 1：處理所有可能的情境 (Rule 1: Handle All Possible Scenarios) {#rule-1-handle-all-possible-scenarios}

提供一個安全的「檢查」函式被認為是良好的實踐，該函式會回傳布林值，以指示是否能安全地執行操作。如果 `module_b` 提供了一個 `has_field` 函式來回傳欄位是否存在的情形（布林值），那麼 `do_something` 函式可以改寫如下：

```move
module book::module_a;

use book::module_b;

const ENoField: u64 = 0;

public fun do_something() {
    assert!(module_b::has_field(1), ENoField);
    let field_1 = module_b::get_field(1);
    /* ... */
    assert!(module_b::has_field(2), ENoField);
    let field_2 = module_b::get_field(2);
    /* ... */
    assert!(module_b::has_field(3), ENoField);
    let field_3 = module_b::get_field(3);
}
```

透過在每次呼叫 `module_b::get_field` 之前加入自訂檢查，`module_a` 的開發者就能掌控錯誤處理，這也允許實作第二個規則。

## 規則 2：使用不同的代碼終止 (Rule 2: Abort with Different Codes) {#rule-2-abort-with-different-codes}

一旦由呼叫者模組處理終止代碼後，第二個技巧是針對不同的情境使用不同的終止代碼。透過這種方式，呼叫者模組可以向使用者提供有意義的錯誤訊息。`module_a` 可以改寫如下：

```move
module book::module_a;

use book::module_b;

const ENoFieldA: u64 = 0;
const ENoFieldB: u64 = 1;
const ENoFieldC: u64 = 2;

public fun do_something() {
    assert!(module_b::has_field(1), ENoFieldA);
    let field_1 = module_b::get_field(1);
    /* ... */
    assert!(module_b::has_field(2), ENoFieldB);
    let field_2 = module_b::get_field(2);
    /* ... */
    assert!(module_b::has_field(3), ENoFieldC);
    let field_3 = module_b::get_field(3);
}
```

現在，呼叫者模組可以向使用者提供有意義的錯誤訊息。如果呼叫者收到終止代碼 `0`，它可以被轉譯為「欄位 1 不存在 (Field 1 does not exist)」。如果呼叫者收到終止代碼 `1`，它可以被轉譯為「欄位 2 不存在 (Field 2 does not exist)」。以此類推。

## 規則 3：回傳 `bool` 而不是 `assert` (Rule 3: Return `bool` Instead of `assert`) {#rule-3-return-bool-instead-of-assert}

開發者經常會忍不住去新增一個公開函式來斷言所有條件並終止執行。然而，建立一個回傳布林值的函式是更好的實踐。透過這種方式，呼叫者模組可以處理錯誤並向使用者提供有意義的錯誤訊息。

```move
module book::some_app_assert;

const ENotAuthorized: u64 = 0;

public fun do_a() {
    assert_is_authorized();
    // ...
}

public fun do_b() {
    assert_is_authorized();
    // ...
}

/// 不要這樣做
public fun assert_is_authorized() {
    assert!(/* 某個條件 */ true, ENotAuthorized);
}
```

這個模組可以改寫如下：

```move
module book::some_app;

const ENotAuthorized: u64 = 0;

public fun do_a() {
    assert!(is_authorized(), ENotAuthorized);
    // ...
}

public fun do_b() {
    assert!(is_authorized(), ENotAuthorized);
    // ...
}

public fun is_authorized(): bool {
    /* 某個條件 */ true
}

// 私有函式仍然可以用於避免在多個地方使用相同終止代碼的相同條件時發生程式碼重複
fun assert_is_authorized() {
    assert!(is_authorized(), ENotAuthorized);
}
```

善用這三個規則將使交易的錯誤處理對呼叫者而言更加透明，並允許其他開發者在其模組中使用自訂的終止代碼。
