---
description:
  改善 Move 智慧合約的錯誤處理 (Improve error handling)：使用具描述性的中止代碼 (abort code) 與錯誤常數
  (error constant)，提升在 Sui 上除錯的效率。
---

# 更好的錯誤處理 (Better Error Handling) {#better-error-handling}

每當執行過程遇到中止（abort），交易就會失敗，並將中止代碼（abort code）回傳給呼叫端。Move VM 會回傳中止交易的模組名稱以及中止代碼。這個行為對交易的呼叫端而言並非完全透明，尤其是當單一函式內含多個呼叫同一個可能中止的函式時。在這種情況下，呼叫端將無法得知是哪一次呼叫導致交易中止，也難以除錯或向使用者提供有意義的錯誤訊息。

```move
module book::module_a;

use book::module_b;

public fun do_something() {
    let field_1 = module_b::get_field(1); // 可能以 0 中止
    /* ... 大量邏輯 ... */
    let field_2 = module_b::get_field(2); // 可能以 0 中止
    /* ... 更多邏輯 ... */
    let field_3 = module_b::get_field(3); // 可能以 0 中止
}
```

上面的範例說明了單一函式內含多個可能中止的呼叫的情況。如果 `do_something` 函式的呼叫端收到中止代碼 `0`，將難以理解是哪一次呼叫 `module_b::get_field` 導致交易中止。為了解決這個問題，有一些常見的模式可以用來改善錯誤處理。

## 規則一：處理所有可能的情境 (Rule 1: Handle All Possible Scenarios) {#rule-1-handle-all-possible-scenarios}

一個被認為良好的實務做法是提供一個安全的「檢查」函式，回傳一個布林值來指示某個操作是否可以安全執行。如果 `module_b` 提供了一個 `has_field` 函式，回傳布林值來指示某個欄位是否存在，`do_something` 函式可以重寫如下：

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

透過在每次呼叫 `module_b::get_field` 之前加上自訂檢查，`module_a` 的開發者掌控了錯誤處理的主導權。而且這也讓實作第二條規則成為可能。

## 規則二：以不同代碼中止 (Rule 2: Abort with Different Codes) {#rule-2-abort-with-different-codes}

第二個技巧是，一旦中止代碼由呼叫端模組處理，就要針對不同的情境使用不同的中止代碼。這樣一來，呼叫端模組就能向使用者提供有意義的錯誤訊息。`module_a` 可以重寫如下：

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

現在，呼叫端模組就能向使用者提供有意義的錯誤訊息。如果呼叫端收到中止代碼 `0`，就可以轉譯為「欄位 1 不存在」。如果呼叫端收到中止代碼 `1`，就可以轉譯為「欄位 2 不存在」。以此類推。

## 規則三：回傳 `bool` 而非使用 `assert` (Rule 3: Return `bool` Instead of `assert`) {#rule-3-return-bool-instead-of-assert}

開發者常常會想新增一個公開函式，斷言（assert）所有條件並中止執行。然而，更好的做法是建立一個回傳布林值的函式。這樣一來，呼叫端模組就能自行處理錯誤並向使用者提供有意義的錯誤訊息。

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

這個模組可以重寫如下：

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

// 在多處使用相同條件與相同中止代碼的情況下，仍可用私有函式來避免程式碼重複
fun assert_is_authorized() {
    assert!(is_authorized(), ENotAuthorized);
}
```

運用這三條規則，將使錯誤處理對交易的呼叫端更加透明，也能讓其他開發者在自己的模組中使用自訂的中止代碼。
