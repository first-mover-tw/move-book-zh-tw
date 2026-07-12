---
title: 元組與單元 (Tuples and Unit) | 參考手冊
description: Move 元組與單位型別參考手冊（Move tuples and unit type Reference）：多重回傳值、解構、單位運算式，以及類元組語法。
---

# 元組與單元 (Tuples and Unit)

Move 並未完全支援元組 (tuples)，不像其他將元組視為 [一等公民 (first-class value)](https://en.wikipedia.org/wiki/First-class_citizen) 的語言那樣。然而，為了支援多重回傳值，Move 具有類元組 (tuple-like) 的運算式。這些運算式在執行階段不會產生具體的數值（位元組碼中沒有元組），因此它們非常受限：

- 它們只能出現在運算式中（通常位於函式的回傳位置）。
- 它們不能綁定到區域變數。
- 它們不能儲存在結構體中。
- 元組型別不能用於實例化泛型。

同樣地，[單元 (unit) `()`](https://en.wikipedia.org/wiki/Unit_type) 是 Move 原始語言為了基於運算式而建立的一種型別。單元數值 `()` 不會產生任何執行階段數值。我們可以將單元 `()` 視為空元組，任何適用於元組的限制也適用於單元。

考慮到這些限制，在語言中擁有元組可能感覺很奇怪。但在其他語言中，元組最常見的用途之一是允許函式回傳多個數值。有些語言透過強制使用者編寫包含多重回傳值的結構體來解決這個問題。然而在 Move 中，你不能將參考放在 [結構體 (structs)](./../structs) 內部。這要求 Move 必須支援多重回傳值。這些多重回傳值在位元組碼層級都會被推入堆疊 (stack)。在原始碼層級，這些多重回傳值使用元組來表示。

## 常值 (Literals)

元組是透過括號內以逗號分隔的運算式清單來建立的。

| 語法            | 型別                                                                      | 描述                                               |
| --------------- | ------------------------------------------------------------------------- | -------------------------------------------------- |
| `()`            | `(): ()`                                                                  | 單元 (Unit)、空元組或元數 (arity) 為 0 的元組      |
| `(e1, ..., en)` | `(e1, ..., en): (T1, ..., Tn)`，其中 `e_i: Ti` 且 `0 < i <= n` 且 `n > 0` | `n` 元組、元數為 `n` 的元組、具有 `n` 個元素的元組 |

請注意，`(e)` 的型別並非 `(e): (t)`，換句話說，不存在只有一個元素的元組。如果括號內只有一個元素，則括號僅用於消除歧義，不帶有任何其他特殊含義。

有時，具有兩個元素的元組稱為「對 (pairs)」，具有三個元素的元組稱為「三元組 (triples)」。

### 範例

```move
module 0::example;

// 這 3 個函式都是等價的

// 當未提供回傳型別時，會預設推斷為 `()`
fun returns_unit_1() { }

// 空運算式區塊中存在隱式的 () 數值
fun returns_unit_2(): () { }

// `returns_unit_1` 和 `returns_unit_2` 的明確版本
fun returns_unit_3(): () { () }


fun returns_3_values(): (u64, bool, address) {
    (0, false, @0x42)
}
fun returns_4_values(x: &u64): (&u64, u8, u128, vector<u8>) {
    (x, 0, 1, b"foobar")
}
```

## 操作

目前對元組唯一能做的操作是解構 (destructuring)。

### 解構 (Destructuring)

任何大小的元組都可以在 `let` 綁定或賦值中被解構。

例如：

```move
module 0x42::example;

// 這 3 個函式是等價的
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

更多詳細資訊請參見 [Move 變數](./../variables)。

## 子型別 (Subtyping)

與參考一樣，元組是 Move 中唯一具有 [子型別 (subtyping)](https://en.wikipedia.org/wiki/Subtyping) 的型別。元組僅在與參考（以共變的方式）相關的意義上具有子型別。

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
// 錯誤！ (&u64, &mut u64) 不是 (&mut u64, &mut u64) 的子型別
// 因為 &u64 不是 &mut u64 的子型別
let (e, f): (&mut u64, &mut u64) = (x, y);
// highlight-error-end
```

## 所有權 (Ownership)

如上所述，元組數值在執行階段並不真正存在。因此，目前它們不能儲存到區域變數中（但此功能很可能會在未來某個時間點推出）。因此，元組目前只能被移動 (moved)，因為複製它們需要先將它們放入區域變數中。
