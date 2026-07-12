---
title: 參考 (References) | 參考手冊
description:
  Move 參考手冊：不可變借用與可變借用 (immutable and mutable borrows)、讀取 (reading)、寫入
  (writing)、所有權規則 (ownership rules)，以及借用檢查器 (borrow checker)。
---

# 參考 (References)

Move 有兩種型別的參考：不可變的 `&` 和可變的 `&mut`。不可變參考是唯讀的，不能修改底層數值（或其任何欄位）。可變參考允許透過該參考進行寫入來進行修改。Move 的型別系統強制執行一種所有權規範，以防止參考錯誤。

## 參考運算子 (Reference Operators)

Move 提供了用於建立和擴展參考的運算子，以及將可變參考轉換為不可變參考的運算子。在這裡和其他地方，我們使用符號 `e: T` 表示「運算式 `e` 具有型別 `T`」。

| 語法        | 型別                                      | 描述                                     |
| ----------- | ----------------------------------------- | ---------------------------------------- |
| `&e`        | `&T`，其中 `e: T` 且 `T` 是非參考型別     | 建立對 `e` 的不可變參考                  |
| `&mut e`    | `&mut T`，其中 `e: T` 且 `T` 是非參考型別 | 建立對 `e` 的可變參考                    |
| `&e.f`      | `&T`，其中 `e.f: T`                       | 建立對結構體 `e` 的欄位 `f` 的不可變參考 |
| `&mut e.f`  | `&mut T`，其中 `e.f: T`                   | 建立對結構體 `e` 的欄位 `f` 的可變參考   |
| `freeze(e)` | `&T`，其中 `e: &mut T`                    | 將可變參考 `e` 轉換為不可變參考          |

`&e.f` 和 `&mut e.f` 運算子既可以用於在結構體中建立新參考，也可以用於擴展現有參考：

```move
let s = S { f: 10 };
let f_ref1: &u64 = &s.f; // 正常運作
let s_ref: &S = &s;
let f_ref2: &u64 = &s_ref.f // 同樣可以運作
```

帶有多個欄位的參考運算式只要兩個結構體都在同一個模組中就可以運作：

```move
public struct A { b: B }
public struct B { c : u64 }
fun f(a: &A): &u64 {
    &a.b.c
}
```

最後，請注意不允許參考的參考：

```move
let x = 7;
let y: &u64 = &x;
// highlight-error
let z: &&u64 = &y; // 錯誤！無法編譯
```

## 透過參考讀取和寫入 {#reading-and-writing-through-references}

可變和不可變參考都可以被讀取以產生被參考數值的副本。

只有可變參考可以被寫入。寫入操作 `*x = v` 會捨棄先前儲存在 `x` 中的數值，並將其更新為 `v`。

這兩種操作都使用類似 C 的 `*` 語法。但是請注意，讀取是一個運算式，而寫入則是必須發生在等號左側的變更 (mutation)。

| 語法       | 型別                               | 描述                         |
| ---------- | ---------------------------------- | ---------------------------- |
| `*e`       | `T`，其中 `e` 是 `&T` 或 `&mut T`  | 讀取 `e` 指向的數值          |
| `*e1 = e2` | `()`，其中 `e1: &mut T` 且 `e2: T` | 使用 `e2` 更新 `e1` 中的數值 |

為了使參考可以被讀取，底層型別必須具有 [`copy` 能力](../abilities)，因為讀取參考會建立該數值的一個新副本。此規則防止了資產的複製：

```move
fun copy_coin_via_ref_bad(c: Coin) {
    let c_ref = &c;
    // highlight-error
    let counterfeit: Coin = *c_ref; // 不允許！
    pay(c);
    pay(counterfeit);
}
```

相對地：為了使參考可以被寫入，底層型別必須具有 [`drop` 能力](../abilities)，因為寫入參考會捨棄（或「丟棄 (drop)」）舊值。此規則防止了資源數值的銷毀：

```move
fun destroy_coin_via_ref_bad(mut ten_coins: Coin, c: Coin) {
    let ref = &mut ten_coins;
    // highlight-error
    *ref = c; // 錯誤！不允許 —— 這會銷毀 10 枚代幣！
}
```

## `freeze` (凍結) 推斷

可變參考可以在預期不可變參考的上下文中使用：

```move
let mut x = 7;
let y: &u64 = &mut x;
```

這之所以可行，是因為在底層，編譯器會在需要的地方插入 `freeze` 指令。以下是更多 `freeze` 推斷執行的範例：

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

### 子型別 (Subtyping)

透過這種 `freeze` 推斷，Move 型別檢查器可以將 `&mut T` 視為 `&T` 的子型別。如上所示，這意味著在任何使用 `&T` 數值的運算式中，也可以使用 `&mut T` 數值。此術語用於錯誤訊息中，以簡潔地表示在提供 `&T` 的地方需要 `&mut T`。例如：

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

目前唯一具有子型別的其他型別是 [元組 (tuples)](./tuples)。

## 所有權 (Ownership)

可變和不可變參考始終可以被複製和擴展，_即使同一參考存在現有的副本或擴展_：

```move
fun reference_copies(s: &mut S) {
  let s_copy1 = s; // 沒問題
  let s_extension = &mut s.f; // 也沒問題
  let s_copy2 = s; // 依然沒問題
  ...
}
```

這對於熟悉 Rust 所有權系統的程式設計師來說可能會感到驚訝，因為 Rust 會拒絕上面的程式碼。Move 的型別系統在處理 [副本 (copies)](./../variables#move-and-copy) 時更為寬鬆，但在確保寫入前可變參考的唯一所有權方面同樣嚴格。

### 參考不能被儲存

參考和元組是 _唯一_ 不能作為結構體欄位值儲存的型別，這也意味著它們不能存在於儲存或 [物件 (objects)](./../abilities/object) 中。程式執行期間建立的所有參考都將在 Move 程式終止時銷毀；它們完全是暫時性的 (ephemeral)。這也適用於所有沒有 `store` 能力的型別：任何非 `store` 型別的數值都必須在程式終止前被銷毀。

這是 Move 與 Rust 的另一個區別，Rust 允許將參考儲存在結構體內部。

人們可以想像一個更花俏、更具表現力的型別系統，允許將參考儲存在結構體中。我們可以允許參考存在於沒有 `store` [能力 (ability)](./../abilities) 的結構體內部，但核心困難在於 Move 有一個相當複雜的系統來追蹤靜態參考安全性。型別系統的這個面向也必須擴展，以支援在結構體內部儲存參考。簡而言之，Move 的參考安全系統必須擴展以支援儲存的參考，隨著語言的演進，這是我們正在關注的事情。

<!-- TODO actually document a sketch of the borrow rules -->
