---
title: 整數 (Integers) | 參考手冊
description: Move 整數型別 (integer types) 參考：u8、u16、u32、u64、u128、u256 — 字面值 (literals)、運算 (operations)、型別轉換 (casting) 與溢位行為 (overflow behavior)。
keywords:
  - Move
  - Sui
  - Move reference
  - integers
  - reference
questions:
  - How does Integers work in Move?
  - What is the syntax for Integers in Move?
  - What is Literals in Move?
  - What is Operations in Move?
answer: 'Move integer types reference: u8, u16, u32, u64, u128, u256 — literals, operations, casting, and overflow behavior.'
goal:
  description: 'Reader understands move integer types reference: u8, u16, u32, u64, u128, u256 — literals, operations, casting, and overflow behavior'
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

# 整數 (Integers) {#integers}

Move 支援六種無符號整數型別：`u8`、`u16`、`u32`、`u64`、`u128` 與 `u256`。這些型別的值範圍從 0 到取決於型別大小的最大值。

| 型別                        | 值範圍                   |
| --------------------------- | ------------------------ |
| 無符號 8 位元整數，`u8`     | 0 到 2<sup>8</sup> - 1   |
| 無符號 16 位元整數，`u16`   | 0 到 2<sup>16</sup> - 1  |
| 無符號 32 位元整數，`u32`   | 0 到 2<sup>32</sup> - 1  |
| 無符號 64 位元整數，`u64`   | 0 到 2<sup>64</sup> - 1  |
| 無符號 128 位元整數，`u128` | 0 到 2<sup>128</sup> - 1 |
| 無符號 256 位元整數，`u256` | 0 到 2<sup>256</sup> - 1 |

## 字面值 (Literals) {#literals}

這些型別的字面值可指定為數字序列（例如 `112`）或十六進位字面值，例如 `0xFF`。字面值的型別可選擇性地新增為後綴，例如 `112u8`。若未指定型別，編譯器會嘗試從使用字面值的上下文推斷型別。若無法推斷型別，則假定為 `u64`。

數字字面值可使用底線分隔，以利分組與閱讀。（例如 `1_234_5678`、`1_000u128`、`0xAB_CD_12_35`）。

若字面值對其指定（或推斷）的大小範圍而言過大，將回報錯誤。

### 範例 (Examples) {#examples}

```move
// 具有明確型別註記的字面值；
let explicit_u8 = 1u8;
let explicit_u16 = 1u16;
let explicit_u32 = 1u32;
let explicit_u64 = 2u64;
let explicit_u128 = 3u128;
let explicit_u256 = 1u256;
let explicit_u64_underscored = 154_322_973u64;

// 具有簡單型別推斷的字面值
let simple_u8: u8 = 1;
let simple_u16: u16 = 1;
let simple_u32: u32 = 1;
let simple_u64: u64 = 2;
let simple_u128: u128 = 3;
let simple_u256: u256 = 1;

// 具有較複雜型別推斷的字面值
let complex_u8 = 1; // 推斷為：u8
// 位移的右側引數必須是 u8
let _unused = 10 << complex_u8;

let x: u8 = 38;
let complex_u8 = 2; // 推斷為：u8
// `+` 的引數必須具有相同型別
let _unused = x + complex_u8;

let complex_u128 = 133_876; // 推斷為：u128
// 從函式引數型別推斷
function_that_takes_u128(complex_u128);

// 字面值可以十六進位表示
let hex_u8: u8 = 0x1;
let hex_u16: u16 = 0x1BAE;
let hex_u32: u32 = 0xDEAD80;
let hex_u64: u64 = 0xCAFE;
let hex_u128: u128 = 0xDEADBEEF;
let hex_u256: u256 = 0x1123_456A_BCDE_F;
```

## 運算 (Operations) {#operations}

### 算術運算 (Arithmetic) {#arithmetic}

每種型別都支援相同的一組受檢查算術運算。對於所有這些運算，兩個引數（左側與右側運算元）都 _必須_ 是相同型別。若你需要對不同型別的值進行運算，必須先進行[型別轉換](#casting)。同樣地，若你預期運算結果對整數型別而言過大，請在進行運算前先[轉換](#casting)為較大的型別。

所有算術運算都會中止，而不會以不符合數學整數規則的方式運作（例如溢位、下溢或除以零）。

| 語法 | 運算     | 中止條件               |
| ---- | -------- | ---------------------- |
| `+`  | 加法     | 結果對整數型別而言過大 |
| `-`  | 減法     | 結果小於零             |
| `*`  | 乘法     | 結果對整數型別而言過大 |
| `%`  | 模除法   | 除數為 `0`             |
| `/`  | 截斷除法 | 除數為 `0`             |

### 位元運算 (Bitwise) {#bitwise}

整數型別支援下列位元運算；這些運算將每個數字視為由個別的 0 或 1 位元組成的序列，而非數值整數值。

位元運算不會中止。

| 語法                | 運算     | 說明                        |
| ------------------- | -------- | --------------------------- |
| `&`                 | 位元 AND | 對每一對位元執行布林 AND    |
| <code>&#124;</code> | 位元 OR  | 對每一對位元執行布林 OR     |
| `^`                 | 位元 XOR | 對每一對位元執行布林互斥 OR |

### 位元位移 (Bit Shifts) {#bit-shifts}

與位元運算相同，每種整數型別都支援位元位移。但與其他運算不同的是，右側運算元（要位移的位元數）_一律_ 必須是 `u8`，且不需要與左側運算元（你要位移的數字）相同型別。

對於 `u8`、`u16`、`u32`、`u64`、`u128` 與 `u256`，若要位移的位元數分別大於或等於 `8`、`16`、`32`、`64`、`128` 或 `256`，位元位移可能會中止。

| 語法 | 運算   | 中止條件                         |
| ---- | ------ | -------------------------------- |
| `<<` | 左位移 | 要位移的位元數大於整數型別的大小 |
| `>>` | 右位移 | 要位移的位元數大於整數型別的大小 |

### 比較 (Comparisons) {#comparisons}

整數型別是 Move 中*唯一*可以使用比較運算子的型別。兩個引數必須是相同型別。若你需要比較不同型別的整數，必須先對其中一個進行[型別轉換](#casting)。

比較運算不會中止。

| 語法 | 運算       |
| ---- | ---------- |
| `<`  | 小於       |
| `>`  | 大於       |
| `<=` | 小於或等於 |
| `>=` | 大於或等於 |

### 相等性 (Equality) {#equality}

如同所有具有 [`drop`](./../abilities) 的型別，所有整數型別都支援[「相等」](./../equality)與[「不相等」](./../equality)運算。兩個引數必須是相同型別。若你需要比較不同型別的整數，必須先對其中一個進行[型別轉換](#casting)。

相等性運算不會中止。

| 語法 | 運算   |
| ---- | ------ |
| `==` | 相等   |
| `!=` | 不相等 |

如需更多詳細資訊，請參閱[相等性](./../equality)章節。

## 型別轉換 (Casting) {#casting}

一種大小的整數型別可以轉換為另一種大小的整數型別。整數是 Move 中唯一支援型別轉換的型別。

型別轉換*不會*截斷。若結果對指定型別而言過大，型別轉換會中止。

| 語法       | 運算                                | 中止條件                 |
| ---------- | ----------------------------------- | ------------------------ |
| `(e as T)` | 將整數運算式 `e` 轉換為整數型別 `T` | `e` 過大，無法表示為 `T` |

此處，`e` 的型別必須是 `8`、`16`、`32`、`64`、`128` 或 `256`，而 `T` 必須是 `u8`、`u16`、`u32`、`u64`、`u128` 或 `u256`。

例如：

- `(x as u8)`
- `(y as u16)`
- `(873u16 as u32)`
- `(2u8 as u64)`
- `(1 + 3 as u128)`
- `(4/2 + 12345 as u256)`

## 所有權 (Ownership) {#ownership}

如同語言內建的其他純量值，整數值可隱式複製，這表示無須 [`copy`](./../variables#move-and-copy) 等明確指令即可複製。
