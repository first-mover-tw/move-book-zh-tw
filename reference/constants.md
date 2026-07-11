---
title: 常數 (Constants) | 參考
description: Move 常數 (Move Constants) 參考手冊：定義編譯時期值、支援的型別、命名規則，以及在模組 (module) 中的用法。
---

# 常數 (Constants)

常數是在 `module` 內給予共享靜態值一個名稱的方式。

常數的值必須在編譯時已知。常數的值儲存在編譯後的模組中。每次使用常數時，該值都會建立一份新副本。

## 宣告 (Declaration)

常數宣告以 `const` 關鍵字開始，後接名稱、類型和值。

```text
const <name>: <type> = <expression>;
```

舉例

```move
module a::example;

const MY_ADDRESS: address = @a;

public fun permissioned(addr: address) {
    assert!(addr == MY_ADDRESS, 0);
}
```

## 命名 (Naming)

常數必須以大寫字母 `A` 到 `Z` 開頭。首字母之後，常數名稱可包含底線 `_`、小寫字母 `a` 到 `z`、大寫字母 `A` 到 `Z` 或數字 `0` 到 `9`。

```move
const FLAG: bool = false;
const EMyErrorCode: u64 = 0;
const ADDRESS_42: address = @0x42;
```

雖然常數名稱可以包含小寫字母 `a` 到 `z`，但 [一般風格指南](./coding-conventions) 建議只使用大寫字母 `A` 到 `Z`，並用底線 `_` 分隔各單字。對於錯誤程式碼，我們使用 `E` 作為前綴，然後使用上駝峰式命名法（也稱為 Pascal case），如 `EMyErrorCode` 所示。

目前命名限制須以 `A` 到 `Z` 開頭，是為了給未來的語言功能預留空間。

## 可見性 (Visibility)

目前不支援 `public` 或 `public(package)` 常數。`const` 值只能在宣告它的模組內使用。但為了方便起見，它們可以在 [單元測試屬性](./unit-testing) 中跨模組使用。

## 有效的運算式 (Valid Expressions)

目前常數限制於原始類型 `bool`、`u8`、`u16`、`u32`、`u64`、`u128`、`u256`、`address` 和 `vector<T>`，其中 `T` 是常數的有效類型。

### 值 (Values)

常見的情況是，`const` 被賦予其類型的簡單值或字面值。舉例

```move
const MY_BOOL: bool = false;
const MY_ADDRESS: address = @0x70DD;
const BYTES: vector<u8> = b"hello world";
const HEX_BYTES: vector<u8> = x"DEADBEEF";
```

### 複雜運算式 (Complex Expressions)

除了字面值外，常數可以包含更複雜的運算式，只要編譯器能在編譯時將運算式化簡為一個值。

目前可以使用相等運算、所有布林運算、所有位元運算和所有算術運算。

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

如果運算會導致執行時異常，編譯器會給出錯誤，表示無法產生該常數的值。

```move
const DIV_BY_ZERO: u64 = 1 / 0; // 錯誤！
const SHIFT_BY_A_LOT: u64 = 1 << 100; // 錯誤！
const NEGATIVE_U64: u64 = 0 - 1; // 錯誤！
```

此外，常數可以在同一模組內引用其他常數。

```move
const BASE: u8 = 4;
const SQUARE: u8 = BASE * BASE;
```

但注意，常數定義中的任何循環都會導致錯誤。

```move
const A: u16 = B + 1;
const B: u16 = A + 1; // 錯誤！
```
