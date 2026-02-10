---
title: '引用 (References) | 參考手冊'
description: "Move 引用參考手冊：不可變與可變借用、讀取、寫入、所有權規則以及借用檢查器。"
---

# 引用 (References)

Move 有兩種類型的引用：不可變的 `&` 和可變的 `&mut`。不可變引用是唯讀的，不能修改底層數值（或其任何欄位）。可變引用允許透過該引用進行寫入來進行修改。Move 的類型系統強制執行一種所有權規範，以防止引用錯誤。

## 引用運算子 (Reference Operators)

Move 提供了用於建立和擴展引用的運算子，以及將可變引用轉換為不可變引用的運算子。在這裡和其他地方，我們使用符號 `e: T` 表示「表達式 `e` 具有類型 `T`」。

| 語法 | 類型 | 描述 |
| ----------- | ----------------------------------------------------- | -------------------------------------------------------------- |
| `&e` | `&T`，其中 `e: T` 且 `T` 是非引用類型 | 建立對 `e` 的不可變引用 |
| `&mut e` | `&mut T`，其中 `e: T` 且 `T` 是非引用類型 | 建立對 `e` 的可變引用 |
| `&e.f` | `&T`，其中 `e.f: T` | 建立對結構體 `e` 的欄位 `f` 的不可變引用 |
| `&mut e.f` | `&mut T`，其中 `e.f: T` | 建立對結構體 `e` 的欄位 `f` 的可變引用 |
| `freeze(e)` | `&T`，其中 `e: &mut T` | 將可變引用 `e` 轉換為不可變引用 |

`&e.f` 和 `&mut e.f` 運算子既可以用於在結構體中建立新引用，也可以用於擴展現有引用：

```move
let s = S { f: 10 };
let f_ref1: &u64 = &s.f; // 正常運作
let s_ref: &S = &s;
let f_ref2: &u64 = &s_ref.f // 同樣可以運作
```

帶有多個欄位的引用表達式只要兩個結構體都在同一個模組中就可以運作：

```move
public struct A { b: B }
public struct B { c : u64 }
fun f(a: &A): &u64 {
    &a.b.c
}
```

最後，請注意不允許引用的引用：

```move
let x = 7;
let y: &u64 = &x;
// highlight-error
let z: &&u64 = &y; // 錯誤！無法編譯
```

## 透過引用讀取和寫入

可變和不可變引用都可以被讀取以產生被引用數值的副本。

只有可變引用可以被寫入。寫入操作 `*x = v` 會捨棄先前存儲在 `x` 中的數值，並將其更新為 `v`。

這兩種操作都使用類似 C 的 `*` 語法。但是請注意，讀取是一個表達式，而寫入則是必須發生在等號左側的變更 (mutation)。

| 語法 | 類型 | 描述 |
| ---------- | ----------------------------------- | ----------------------------------- |
| `*e` | `T`，其中 `e` 是 `&T` 或 `&mut T` | 讀取 `e` 指向的數值 |
| `*e1 = e2` | `()`，其中 `e1: &mut T` 且 `e2: T` | 使用 `e2` 更新 `e1` 中的數值 |

為了使引用可以被讀取，底層類型必須具有 [`copy` 能力](../abilities)，因為讀取引用會建立該數值的一個新副本。此規則防止了資產的複製：

```move
fun copy_coin_via_ref_bad(c: Coin) {
    let c_ref = &c;
    // highlight-error
    let counterfeit: Coin = *c_ref; // 不允許！
    pay(c);
    pay(counterfeit);
}
```

相對地：為了使引用可以被寫入，底層類型必須具有 [`drop` 能力](../abilities)，因為寫入引用會捨棄（或「丟棄 (drop)」）舊值。此規則防止了資源數值的銷毀：

```move
fun destroy_coin_via_ref_bad(mut ten_coins: Coin, c: Coin) {
    let ref = &mut ten_coins;
    // highlight-error
    *ref = c; // 錯誤！不允許 —— 這會銷毀 10 枚代幣！
}
```

## `freeze` (凍結) 推斷

可變引用可以在預期不可變引用的上下文中使用：

```move
let mut x = 7;
let y: &u64 = &mut x;
```

這之所以可行，是因為在底層，編譯器會在需要的地方插入 `freeze` 指令。以下是更多 `freeze` 推斷運行的範例：

```move
fun takes_immut_returns_immut(x: &u64): &u64 { x }

// 對回傳值進行 freeze 推斷
fun takes_mut_returns_immut(x: &mut u64): &u64 { x }

fun expression_examples() {
    let mut x = 0;
    let mut y = 0;
    takes_immut_returns_immut(&x); // 無需推斷
    takes_immut_returns_immut(&mut x); // 推斷為 freeze(&mut x)
    takes_mut_returns_immut(&mut x); // 無需推斷

    assert!(&x == &mut y, 42); // 推斷為 freeze(&mut y)
}

fun assignment_examples() {
    let x = 0;
    let y = 0;
    let imm_ref: &u64 = &x;

    imm_ref = &x; // 無需推斷
    imm_ref = &mut y; // 推斷為 freeze(&mut y)
}
```

### 子類型 (Subtyping)

透過這種 `freeze` 推斷，Move 類型檢查器可以將 `&mut T` 視為 `&T` 的子類型。如上所示，這意味著在任何使用 `&T` 數值的表達式中，也可以使用 `&mut T` 數值。此術語用於錯誤訊息中，以簡潔地表示在提供 `&T` 的地方需要 `&mut T`。例如：

```move
module a::example {
    fun read_and_assign(store: &mut u64, new_value: &u64) {
        *store = *new_value
    }

    fun subtype_examples() {
        let mut x: &u64 = &0;
        let mut y: &mut u64 = &mut 1;

        x = &mut 1; // 有效
        // highlight-error
        y = &2; // 錯誤！無效！

        read_and_assign(y, x); // 有效
        // highlight-error
        read_and_assign(x, y); // 錯誤！無效！
    }
}
```

將產生以下錯誤訊息：

```text
error:

    ┌── example.move:11:9 ───
    │
 12 │         y = &2; // invalid!
    │         ^ Invalid assignment to local 'y'
    ·
 12 │         y = &2; // invalid!
    │             -- The type: '&{integer}'
    ·
  9 │         let mut y: &mut u64 = &mut 1;
    │                    -------- Is not a subtype of: '&mut u64'
    │

error:

    ┌── example.move:14:9 ───
    │
 15 │         read_and_assign(x, y); // invalid!
    │         ^^^^^^^^^^^^^^^^^^^^^ Invalid call of 'a::example::read_and_assign'. Invalid argument for parameter 'store'
    ·
  8 │         let mut x: &u64 = &0;
    │                    ---- The type: '&u64'
    ·
  3 │     fun read_and_assign(store: &mut u64, new_value: &u64) {
    │                                -------- Is not a subtype of: '&mut u64'
    │
```

目前唯一具有子類型的其他類型是 [元組 (tuples)](./tuples)。

## 所有權 (Ownership)

可變和不可變引用始終可以被複製和擴展，*即使同一引用存在現有的副本或擴展*：

```move
fun reference_copies(s: &mut S) {
  let s_copy1 = s; // 沒問題
  let s_extension = &mut s.f; // 也沒問題
  let s_copy2 = s; // 依然沒問題
  ...
}
```

這對於熟悉 Rust 所有權系統的程式設計師來說可能會感到驚訝，因為 Rust 會拒絕上面的程式碼。Move 的類型系統在處理 [副本 (copies)](./../variables#移動與複製) 時更為寬鬆，但在確保寫入前可變引用的唯一所有權方面同樣嚴格。

### 引用不能被存儲

引用和元組是 *唯一* 不能作為結構體欄位值存儲的類型，這也意味著它們不能存在於存儲或 [物件 (objects)](./../abilities/object) 中。程式執行期間建立的所有引用都將在 Move 程式終止時銷毀；它們完全是暫時性的 (ephemeral)。這也適用於所有沒有 `store` 能力的類型：任何非 `store` 類型的數值都必須在程式終止前被銷毀。

這是 Move 與 Rust 的另一個區別，Rust 允許將引用存儲在結構體內部。

人們可以想像一個更花俏、更具表現力的類型系統，允許將引用存儲在結構體中。我們可以允許引用存在於沒有 `store` [能力 (ability)](./../abilities) 的結構體內部，但核心困難在於 Move 有一個相當複雜的系統來追蹤靜態引用安全性。類型系統的這個面向也必須擴展，以支援在結構體內部存儲引用。簡而言之，Move 的引用安全系統必須擴展以支援存儲的引用，隨著語言的演進，這是我們正在關注的事情。

<!-- TODO actually document a sketch of the borrow rules -->
