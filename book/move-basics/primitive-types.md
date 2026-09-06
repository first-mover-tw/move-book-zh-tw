---
description: Move 基本型別 (primitive types)：布林值 (booleans) 與從 u8 到 u256 的無號整數 (unsigned integers)——字面值 (literals) 與型別推斷 (type inference)、算術 (arithmetic) 與比較 (comparison)、使用 as 進行型別轉換 (casting)，以及溢位行為 (overflow behavior)。
title: 原始型別 (Primitive Types)
keywords:
  - Move
  - Sui
  - Move tutorial
  - primitive
  - types
  - type system
questions:
  - What is Primitive Types in Move?
  - How do I use Primitive Types in Move?
  - What is Variables and Assignment in Move?
  - What is Booleans in Move?
answer: 'Move primitive types: booleans and unsigned integers from u8 to u256 - literals and type inference, arithmetic and comparison, casting with as, and overflow behavior.'
goal:
  description: 'Reader understands move primitive types: booleans and unsigned integers from u8 to u256 - literals and type inference, arithmetic and comparison, casting with as, and overflow behavior'
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

# 原始型別 (Primitive Types) {#primitive-types}

Move 是靜態型別語言：每個值都有一個在編譯時期已知的型別。本節介紹其中最簡單的型別——內建的*原始*型別：布林值與無號整數。再加上下一節介紹的[地址](./address)，它們構成了所有其他型別的基礎。

> 本章的程式碼範例皆為摘錄：如下方所示的運算式位於模組中的函式內——通常是[測試函式](./testing)——為求簡潔，我們省略了模組。若要自行嘗試範例，請將其放入 [Hello World](./../your-first-move/hello-world) 章節所建立套件的 `#[test]` 函式中，並執行 `sui move test`。

## 變數與指派 (Variables and Assignment) {#variables-and-assignment}

變數使用 `let` 關鍵字宣告，且預設為 _不可變_：一旦指派值後，
便無法取代。需要變更的變數會以 `let mut` 宣告，且只有在此情況下，
才能使用 `=` 運算子重新指派：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=variables_and_assignment

```

型別註記——名稱後方的 `: u8`——在編譯器能從值或後續使用方式推斷
型別的任何地方皆為選用；將其明確寫出是為了清楚，而非必要。

也可以再次宣告變數來重複使用變數名稱，這稱為 _遮蔽_。不同於
重新指派，遮蔽會建立新的變數，因此可用於不可變變數，且能變更
型別：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=shadowing

```

## 布林值 (Booleans) {#booleans}

`bool` 型別恰有兩個值——關鍵字 `true` 與 `false`——而編譯器一律會推斷它，因此 `bool` 永遠不需要型別註記。布林值可與邏輯運算子 `&&`（且）、`||`（或）和 `!`（非）搭配使用，其中 `&&` 與 `||` 會短路：如果左側已決定結果，就不會評估右側。

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=boolean

```

布林值儲存旗標並驅動條件判斷——即 [控制流程](./control-flow) 章節涵蓋的 `if` 與 `while` 運算式。

## 整數型別 (Integer Types) {#integer-types}

Move 有六種整數型別，僅大小不同，而且全都是 _無號_：Move 中沒有負整數，也沒有專用的帶號型別。

<div class="modules-table">

| 型別   | 大小（位元） | 最大值                       |
| ------ | ------------ | ---------------------------- |
| `u8`   | 8            | `255`                        |
| `u16`  | 16           | `65_535`                     |
| `u32`  | 32           | `4_294_967_295`              |
| `u64`  | 64           | `18_446_744_073_709_551_615` |
| `u128` | 128          | 2<sup>128</sup> − 1          |
| `u256` | 256          | 2<sup>256</sup> − 1          |

</div>

主要使用的是 `u64`：代幣數量、大小與索引都使用它。整數常值可用十進位（`42`）撰寫，並可選擇加入底線以提升可讀性（`1_000_000`），或使用帶有 `0x` 前綴的十六進位（`0x2A`）：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integers

```

雖然 `true` 與 `false` 明確是布林值，但像 `42` 這樣的常值可能是六種整數型別中的任何一種。編譯器會根據值的使用方式推斷型別，預設為 `u64`；當推斷不足，或明確指定可讓程式碼更易讀時，可以透過型別註記或常值後綴指定型別：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integer_explicit_type

```

### 運算 (Operations) {#operations}

Move 支援整數的標準算術運算：加法、減法、乘法、除法與模數（餘數）。它們都無法產生超出型別範圍的值；運算不會環繞，而是會中止：

<div class="modules-table">

| 語法 | 運算         | 中止條件               |
| ---- | ------------ | ---------------------- |
| +    | 加法         | 結果對整數型別而言過大 |
| -    | 減法         | 結果小於零             |
| \*   | 乘法         | 結果對整數型別而言過大 |
| %    | 模數（餘數） | 除數為 0               |
| /    | 截斷除法     | 除數為 0               |

</div>

除法為 _截斷式_：不存在小數值，且任何餘數都會被捨棄，因此 `7 / 2` 為 `3`。整數也可以使用 `==`、`!=`、`<`、`>`、`<=` 與 `>=` 進行比較，產生 `bool`：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=comparison

```

在每項運算與比較中，運算元的型別 _必須相符_：整數型別之間沒有隱含轉換，將 `u8` 加上 `u64` 會造成編譯錯誤。若要對不同型別進行運算，必須明確轉型其中一個運算元。

> 如需更多運算，包括位元運算，請參閱
> [Move 參考文件](./../../reference/primitive-types/integers#bitwise)。

### 使用 `as` 轉型 (Casting with `as`) {#casting-with-as}

`as` 運算子可將整數從一種型別轉換為另一種型別。請注意，包含轉型的運算式通常需要以括號包住，以避免歧義：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=cast_as

```

向 _上_ 轉型至較大的型別時一定成功。向 _下_ 轉型必須能容納該值：不同於會悄悄截斷值的語言，Move 在值超出範圍時會中止：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=downcast

```

向上轉型的常見用途是為無法容納於原始型別的中間結果預留空間：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=overflow

```

### 溢位與下溢 (Overflow and Underflow) {#overflow-and-underflow}

如運算表所示，Move 中的算術運算絕不會環繞。結果無法容納於型別中的運算——過大或小於零——會在執行階段中止：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=overflow_abort

```

這是一項刻意設計的安全功能。靜默溢位是智慧合約錯誤的典型來源——餘額環繞為零，或因為某個值悄悄變小而使檢查通過。Move 會將每一種這類情況轉為明確失敗，並還原交易。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Bool](./../../reference/primitive-types/bool)。
- Move 參考文件中的 [Integer](./../../reference/primitive-types/integers)。
- [std::u64](https://docs.sui.io/references/framework/std/u64) 模組文件——每個整數
  型別都有一個輔助模組（從 `std::u8` 到 `std::u256`），提供如 `min`、`max`、`sqrt`
  等函式。
