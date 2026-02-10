# 更好的錯誤處理 (Better Error Handling)

Move 2024 提供了更好的錯誤處理機制。在一個函式中呼叫多個可能中斷的函式時，如果呼叫者收到中斷碼 `0`，將很難理解是哪個呼叫導致了中斷。

## 規則 1：處理所有可能的情境

良好的實踐是提供一個安全的「檢查」函式，返回一個布林值，指示操作是否可以安全執行。

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

## 規則 2：使用不同的中斷碼

第二個技巧是為不同的情境提供不同的中斷碼。

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

## 規則 3：返回 `bool` 而不是直接 `assert`

開發者通常傾向於添加一個直接斷言所有條件並中斷執行的公開函式。然而，更好的做法是建立一個返回布林值的函式。

```move
module book::some_app;

const ENotAuthorized: u64 = 0;

public fun do_a() {
    assert!(is_authorized(), ENotAuthorized);
    // ...
}

public fun is_authorized(): bool {
    /* 某些條件 */ true
}
```
