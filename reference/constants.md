---
title: 常數 (Constants) | 參考手冊
description: Move 常數 (constants) 參考手冊：定義編譯時期值 (compile-time values)、支援的型別 (types)、命名規則，以及在模組 (modules) 中的使用方式。
keywords:
  - Move
  - Sui
  - Move reference
  - constants
  - reference
questions:
  - How does Constants work in Move?
  - What is the syntax for Constants in Move?
  - What is Declaration in Move?
  - What is Naming in Move?
answer: 'Move constants reference: define compile-time values, supported types, naming rules, and usage in modules.'
goal:
  description: 'Reader understands move constants reference: define compile-time values, supported types, naming rules, and usage in modules'
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

# 常數 (Constants) {#constants}

常數是在 `module` 內為共用的靜態值命名的一種方式。

常數的值必須在編譯時已知。常數的值會儲存在已編譯的
模組中。每次使用該常數時，都會建立該值的新副本。

## 宣告 (Declaration) {#declaration}

常數宣告以 `const` 關鍵字開始，後接名稱、型別和值。

```text
const <name>: <type> = <expression>;
```

例如：

```move
module a::example;

const MY_ADDRESS: address = @a;

public fun permissioned(addr: address) {
    assert!(addr == MY_ADDRESS, 0);
}
```

## 命名 (Naming) {#naming}

常數必須以大寫字母 `A` 至 `Z` 開頭。第一個字母之後，常數名稱可以
包含底線 `_`、字母 `a` 至 `z`、字母 `A` 至 `Z`，或數字 `0` 至 `9`。

```move
const FLAG: bool = false;
const EMyErrorCode: u64 = 0;
const ADDRESS_42: address = @0x42;
```

雖然常數中可以使用字母 `a` 至 `z`，[一般風格指南](./coding-conventions)建議僅使用大寫字母 `A` 至 `Z`，並在每個單字之間使用底線 `_`。對於錯誤碼，我們使用 `E` 作為前綴，接著將名稱其餘部分採用大駝峰式命名
（亦稱 Pascal 命名法），如 `EMyErrorCode` 所示。

目前要求以 `A` 至 `Z` 開頭的命名限制，是為未來的語言功能預留空間。

## 可見性 (Visibility) {#visibility}

目前不支援 `public` 或 `public(package)` 常數。`const` 值僅能在其宣告的模組中使用。不過，為了便利起見，它們可以跨模組用於
[單元測試屬性](./unit-testing)。

## 有效運算式 (Valid Expressions) {#valid-expressions}

目前，常數僅限使用原始型別 `bool`、`u8`、`u16`、`u32`、`u64`、`u128`、
`u256`、`address` 與 `vector<T>`，其中 `T` 是常數的有效型別。

### 值 (Values) {#values}

通常會為 `const` 指派其型別的簡單值或常值。例如：

```move
const MY_BOOL: bool = false;
const MY_ADDRESS: address = @0x70DD;
const BYTES: vector<u8> = b"hello world";
const HEX_BYTES: vector<u8> = x"DEADBEEF";
```

### 複雜運算式 (Complex Expressions) {#complex-expressions}

除了常值以外，只要編譯器能夠在編譯時將運算式化簡為值，常數也可以包含更複雜的運算式。

目前可以使用相等性運算、所有布林運算、所有位元運算，以及所有算術運算。

```move
const RULE: bool = true && false;
const CAP: u64 = 10 * 100 + 1;
const SHIFTY: u8 = {
    (1 << 1) * (1 << 2) * (1 << 3) * (1 << 4)
};
const HALF_MAX: u128 = 340282366920938463463374607431768211455 / 2;
const REM: u256 =
    57896044618658097711785492504343953926634992332820282019728792003956564819968 % 654321;
const EQUAL: bool = 1 == 1;
```

如果該運算會導致執行階段例外，編譯器會回報無法產生常數值的錯誤。

```move
const DIV_BY_ZERO: u64 = 1 / 0; // 錯誤！
const SHIFT_BY_A_LOT: u64 = 1 << 100; // 錯誤！
const NEGATIVE_U64: u64 = 0 - 1; // 錯誤！
```

此外，常數可以參考同一模組內的其他常數。

```move
const BASE: u8 = 4;
const SQUARE: u8 = BASE * BASE;
```

但請注意，常數定義中的任何迴圈都會導致錯誤。

```move
const A: u16 = B + 1;
const B: u16 = A + 1; // 錯誤！
```
