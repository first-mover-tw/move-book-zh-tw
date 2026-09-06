---
title: 參考資料 | 參考手冊
description: Move 參考 (references) 參考手冊：不可變與可變借用、讀取、寫入、所有權規則，以及借用檢查器 (borrow checker)。
keywords:
  - Move
  - Sui
  - Move reference
  - references
  - reference
questions:
  - How does References work in Move?
  - What is the syntax for References in Move?
  - What is Reference Operators in Move?
  - What is Reading and Writing Through References in Move?
answer: 'Move references reference: immutable and mutable borrows, reading, writing, ownership rules, and the borrow checker.'
goal:
  description: 'Reader understands move references reference: immutable and mutable borrows, reading, writing, ownership rules, and the borrow checker'
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

# 參考 (References) {#references}

Move 有兩種參考：不可變的 `&` 與可變的 `&mut`。不可變參考僅能讀取，
無法修改底層值（或其任何欄位）。可變參考允許透過該參考寫入以進行修改。Move 的型別系統強制執行一套所有權
規則，以避免參考錯誤。

## 參考運算子 (Reference Operators) {#reference-operators}

Move 提供用於建立及延伸參考的運算子，以及將可變
參考轉換為不可變參考的運算子。此處及其他地方，我們使用記號 `e: T` 表示「運算式 `e`
具有型別 `T`」。

| 語法        | 型別                                      | 說明                                       |
| ----------- | ----------------------------------------- | ------------------------------------------ |
| `&e`        | `&T`，其中 `e: T` 且 `T` 是非參考型別     | 建立指向 `e` 的不可變參考                  |
| `&mut e`    | `&mut T`，其中 `e: T` 且 `T` 是非參考型別 | 建立指向 `e` 的可變參考。                  |
| `&e.f`      | `&T`，其中 `e.f: T`                       | 建立指向結構 `e` 之欄位 `f` 的不可變參考。 |
| `&mut e.f`  | `&mut T`，其中 `e.f: T`                   | 建立指向結構 `e` 之欄位 `f` 的可變參考。   |
| `freeze(e)` | `&T`，其中 `e: &mut T`                    | 將可變參考 `e` 轉換為不可變參考。          |

`&e.f` 與 `&mut e.f` 運算子既可用來建立指向結構的新參考，也可用於
延伸既有參考：

```move
let s = S { f: 10 };
let f_ref1: &u64 = &s.f; // 可運作
let s_ref: &S = &s;
let f_ref2: &u64 = &s_ref.f // 同樣可運作
```

只要兩個結構都位於相同模組中，具有多個欄位的參考運算式即可運作：

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
// 突顯錯誤
let z: &&u64 = &y; // 錯誤！無法編譯
```

## 透過參考讀取與寫入 (Reading and Writing Through References) {#reading-and-writing-through-references}

可變與不可變參考皆可讀取，以產生被參考值的複本。

只有可變參考可寫入。寫入 `*x = v` 會捨棄先前儲存在 `x` 中的值，
並以 `v` 更新它。

兩項操作皆使用類似 C 的 `*` 語法。不過請注意，讀取是運算式，而
寫入是必須出現在等號左側的變更操作。

| 語法       | 型別                               | 說明                         |
| ---------- | ---------------------------------- | ---------------------------- |
| `*e`       | `T`，其中 `e` 為 `&T` 或 `&mut T`  | 讀取 `e` 所指向的值          |
| `*e1 = e2` | `()`，其中 `e1: &mut T` 且 `e2: T` | 使用 `e2` 更新 `e1` 中的值。 |

若要讀取參考，底層型別必須具有
[`copy` ability](../abilities)，因為讀取參考會建立該值的新複本。此規則
可避免資產遭到複製：

```move
fun copy_coin_via_ref_bad(c: Coin) {
    let c_ref = &c;
    // 突顯錯誤
    let counterfeit: Coin = *c_ref; // 不允許！
    pay(c);
    pay(counterfeit);
}
```

相對地：若要寫入參考，底層型別必須具有
[`drop` ability](../abilities)，因為寫入參考會捨棄（或「drop」）舊值。
此規則可避免資源值遭到銷毀：

```move
fun destroy_coin_via_ref_bad(mut ten_coins: Coin, c: Coin) {
    let ref = &mut ten_coins;
    // 突顯錯誤
    *ref = c; // 錯誤！不允許——會銷毀 10 個 coin！
}
```

## `freeze` 推論 (`freeze` inference) {#freeze-inference}

可在預期不可變參考的情境中使用可變參考：

```move
let mut x = 7;
let y: &u64 = &mut x;
```

這之所以可行，是因為編譯器會在底層於需要之處插入 `freeze`
指令。以下是幾個 `freeze` 推論運作中的額外範例：

```move
fun takes_immut_returns_immut(x: &u64): &u64 { x }

// 回傳值上的 freeze 推論
fun takes_mut_returns_immut(x: &mut u64): &u64 { x }

fun expression_examples() {
    let mut x = 0;
    let mut y = 0;
    takes_immut_returns_immut(&x); // 無推論
    takes_immut_returns_immut(&mut x); // 推論出 freeze(&mut x)
    takes_mut_returns_immut(&mut x); // 無推論

    assert!(&x == &mut y, 42); // 推論出 freeze(&mut y)
}

fun assignment_examples() {
    let x = 0;
    let y = 0;
    let imm_ref: &u64 = &x;

    imm_ref = &x; // 無推論
    imm_ref = &mut y; // 推論出 freeze(&mut y)
}
```

### 子型別 (Subtyping) {#subtyping}

透過此 `freeze` 推論，Move 型別檢查器可將 `&mut T` 視為 `&T` 的子型別。如上所示，
這表示在任何使用 `&T` 值的運算式位置，也可使用 `&mut T` 值。此術語用於錯誤訊息中，
以簡潔指出在提供 `&T` 的位置需要 `&mut T`。例如：

```move
module a::example {
    fun read_and_assign(store: &mut u64, new_value: &u64) {
        *store = *new_value
    }

    fun subtype_examples() {
        let mut x: &u64 = &0;
        let mut y: &mut u64 = &mut 1;

        x = &mut 1; // 有效
        // 突顯錯誤
        y = &2; // 錯誤！無效！

        read_and_assign(y, x); // 有效
        // 突顯錯誤
        read_and_assign(x, y); // 錯誤！無效！
    }
}
```

將產生以下錯誤訊息：

```text
錯誤：

    ┌── example.move:11:9 ───
    │
 12 │         y = &2; // 無效！
    │         ^ 無效的區域變數 'y' 指派
    ·
 12 │         y = &2; // 無效！
    │             -- 型別：'&{integer}'
    ·
  9 │         let mut y: &mut u64 = &mut 1;
    │                    -------- 不是下列型別的子型別：'&mut u64'
    │

錯誤：

    ┌── example.move:14:9 ───
    │
 15 │         read_and_assign(x, y); // 無效！
    │         ^^^^^^^^^^^^^^^^^^^^^ 無效地呼叫 'a::example::read_and_assign'。參數 'store' 的引數無效
    ·
  8 │         let mut x: &u64 = &0;
    │                    ---- 型別：'&u64'
    ·
  3 │     fun read_and_assign(store: &mut u64, new_value: &u64) {
    │                                -------- 不是下列型別的子型別：'&mut u64'
    │
```

目前唯一其他具有子型別關係的型別是[元組](./tuples)。

## 所有權 (Ownership) {#ownership}

可變與不可變參考皆可隨時複製及延伸，_即使相同參考已有既有的
複本或延伸_：

```move
fun reference_copies(s: &mut S) {
  let s_copy1 = s; // 可以
  let s_extension = &mut s.f; // 同樣可以
  let s_copy2 = s; // 仍然可以
  ...
}
```

這對熟悉 Rust 所有權系統的程式設計者而言可能令人意外，因為 Rust 會拒絕
上述程式碼。Move 的型別系統在處理
[複製](./../variables#move-and-copy)時較為寬鬆，但在確保寫入前可變
參考的唯一所有權方面同樣嚴格。

### 參考無法儲存 (References Cannot Be Stored) {#references-cannot-be-stored}

參考與元組是*唯一*無法作為結構欄位值儲存的型別，這也表示它們無法存在於
儲存空間或[物件](./../abilities/object)中。程式執行期間建立的所有參考，
都會在 Move 程式中止時被銷毀；它們完全是暫時性的。這也適用於所有不具 `store`
ability 的型別：任何非 `store` 型別的值都必須在程式中止前銷毀。

這是 Move 與 Rust 的另一項差異，Rust 允許將參考儲存在
結構內。

可以想像有一個更精巧、更具表達力的型別系統，允許將參考儲存在結構中。我們可以允許
不具 `store`
[ability](./../abilities) 的結構內含有參考，但核心困難在於 Move 擁有一套相當複雜的系統，
用以追蹤靜態參考安全性。型別系統的這個面向也必須擴充，才能支援將參考儲存在結構內。
簡而言之，Move 的參考安全系統必須擴充以支援已儲存的參考；隨著語言演進，我們會持續關注此事。

<!-- TODO 實際記錄借用規則的草圖 -->
