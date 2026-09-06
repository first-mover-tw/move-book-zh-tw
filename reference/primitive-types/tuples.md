---
title: 元組與單元 (Tuples and Unit) | 參考手冊
description: Move 元組 (tuples) 與單位型別 (unit type) 參考手冊：多個回傳值、解構、單位運算式，以及類似元組的語法。
keywords:
  - Move
  - Sui
  - Move reference
  - tuples
  - unit
  - reference
questions:
  - How does Tuples and Unit work in Move?
  - What is the syntax for Tuples and Unit in Move?
  - What is Literals in Move?
  - What is Operations in Move?
answer: 'Move tuples and unit type reference: multiple return values, destructuring, unit expressions, and tuple-like syntax.'
goal:
  description: 'Reader understands move tuples and unit type reference: multiple return values, destructuring, unit expressions, and tuple-like syntax'
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

# 元組與單位 (Tuples and Unit) {#tuples-and-unit}

Move 並未如同其他將元組視為[一級值](https://en.wikipedia.org/wiki/First-class_citizen)的語言一般，完整支援元組。不過，為了支援多個回傳值，Move 提供了類似元組的運算式。這些運算式不會在執行階段產生具體值（位元組碼中沒有元組），因此其限制相當多：

- 它們只能出現在運算式中（通常位於函式的回傳位置）。
- 無法繫結至區域變數。
- 無法儲存在結構中。
- 元組型別無法用來具現化泛型。

同樣地，[單位 `()`](https://en.wikipedia.org/wiki/Unit_type)是 Move 原始碼語言為了採用運算式導向而建立的型別。單位值 `()` 不會產生任何執行階段值。我們可以將單位`()`視為空元組，而套用至元組的所有限制也同樣套用至單位。

在有這些限制的情況下，語言中仍包含元組或許令人感到奇怪。不過，在其他語言中，元組最常見的使用案例之一，是讓函式能夠回傳多個值。有些語言會要求使用者撰寫包含多個回傳值的結構來迴避此問題。然而，在 Move 中，你無法將參考放入[結構](./../structs)中。因此，Move 必須支援多個回傳值。這些多個回傳值都會在位元組碼層級推入堆疊。在原始碼層級，這些多個回傳值會以元組表示。

## 字面值 (Literals) {#literals}

元組是由括號內以逗號分隔的運算式清單建立。

| 語法            | 型別                                                                         | 說明                                                     |
| --------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------- |
| `()`            | `(): ()`                                                                     | 單位、空元組，或是元素數量為 0 的元組                    |
| `(e1, ..., en)` | `(e1, ..., en): (T1, ..., Tn)` where `e_i: Ti` s.t. `0 < i <= n` and `n > 0` | `n` 元組、元素數量為 `n` 的元組，或具有 `n` 個元素的元組 |

請注意，`(e)` 的型別不是 `(e): (t)`；換句話說，不存在只有一個元素的元組。若括號內只有單一元素，括號僅用於消除歧義，並不帶有其他特殊意義。

有時候，具有兩個元素的元組稱為「配對」，具有三個元素的元組稱為「三元組」。

### 範例 (Examples) {#examples}

```move
module 0::example;

// 這 3 個函式全都等效

// 未提供回傳型別時，會假定為 `()`
fun returns_unit_1() { }

// 空的運算式區塊中隱含一個 () 值
fun returns_unit_2(): () { }

// `returns_unit_1` 與 `returns_unit_2` 的明確版本
fun returns_unit_3(): () { () }


fun returns_3_values(): (u64, bool, address) {
    (0, false, @0x42)
}
fun returns_4_values(x: &u64): (&u64, u8, u128, vector<u8>) {
    (x, 0, 1, b"foobar")
}
```

## 操作 (Operations) {#operations}

目前唯一能對元組執行的操作是解構。

### 解構 (Destructuring) {#destructuring}

任何大小的元組都可以在 `let` 繫結或指派中解構。

例如：

```move
module 0x42::example;

// 這 3 個函式全都等效
fun returns_unit() {}
fun returns_2_values(): (bool, bool) { (true, false) }
fun returns_4_values(x: &u64): (&u64, u8, u128, vector<u8>) { (x, 0, 1, b"foobar") }

fun examples(cond: bool) {
    let () = ();
    let (mut x, mut y): (u8, u64) = (0, 1);
    let (mut a, mut b, mut c, mut d) = (@0x0, 0, false, b"");

    () = ();
    (x, y) = if (cond) (1, 2) else (3, 4);
    (a, b, c, d) = (@0x1, 1, true, b"1");
}

fun examples_with_function_calls() {
    let () = returns_unit();
    let (mut x, mut y): (bool, bool) = returns_2_values();
    let (mut a, mut b, mut c, mut d) = returns_4_values(&0);

    () = returns_unit();
    (x, y) = returns_2_values();
    (a, b, c, d) = returns_4_values(&1);
}
```

如需更多詳細資訊，請參閱 [Move 變數](./../variables)。

## 子型別 (Subtyping) {#subtyping}

除了參考以外，元組是 Move 中唯一具有[子型別](https://en.wikipedia.org/wiki/Subtyping)的型別。元組僅在其包含參考的子型別關係中具有子型別性質（以協變方式）。

例如：

```move
let x: &u64 = &0;
let y: &mut u64 = &mut 1;

// (&u64, &mut u64) 是 (&u64, &u64) 的子型別
// 因為 &mut u64 是 &u64 的子型別
let (a, b): (&u64, &u64) = (x, y);

// (&mut u64, &mut u64) 是 (&u64, &u64) 的子型別
// 因為 &mut u64 是 &u64 的子型別
let (c, d): (&u64, &u64) = (y, y);

// highlight-error-start
// 錯誤！(&u64, &mut u64) 並非 (&mut u64, &mut u64) 的子型別
// 因為 &u64 並非 &mut u64 的子型別
let (e, f): (&mut u64, &mut u64) = (x, y);
// highlight-error-end
```

## 所有權 (Ownership) {#ownership}

如上所述，元組值實際上並不存在於執行階段。由於這個原因，目前它們無法儲存至區域變數中（但這項功能很可能會在未來某個時間點推出）。因此，目前元組只能被移動，因為複製元組會要求先將其放入區域變數中。
