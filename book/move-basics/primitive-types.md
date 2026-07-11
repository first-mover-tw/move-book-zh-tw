---
description:
  Move 基本型別（primitive types）：布林值（booleans）與從 u8 到 u256 的無符號整數（unsigned
  integers）——字面值（literals）與型別推斷（type inference）、算術運算（arithmetic）與比較運算（comparison）、使用
  `as` 進行轉型（casting）、以及溢位行為（overflow behavior）。
---

# 基本型別 (Primitive Types) {#primitive-types}

Move 是一種靜態型別語言：每個值都有一個型別，且在編譯時期即可得知。本節將介紹其中最簡單的型別 —— 內建的_基本_型別：布林值與無號整數。它們與下一節介紹的 [地址](./address) 一起，構成了其他所有型別的基礎材料。

> 本章的程式碼範例都是節錄片段：像下面這樣的運算式，實際上是放在模組內的一個函式中 —— 通常是 [測試函式](./testing) —— 為求簡潔我們省略了模組的部分。若想親自試試某個範例，可以把它放進 [Hello World](./../your-first-move/hello-world) 章節所建立套件中的 `#[test]` 函式裡，然後執行 `sui move test`。

## 變數與賦值 (Variables and Assignment) {#variables-and-assignment}

變數以 `let` 關鍵字宣告，且預設是_不可變的_：一旦賦值後就無法替換。若需要改變的變數，則要以 `let mut` 宣告，如此一來才能用 `=` 運算子重新賦值：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=variables_and_assignment

```

型別標註 —— 也就是名稱後面的 `: u8` —— 在編譯器能從值或後續使用推斷出型別時是可選的；寫出它只是為了清楚易讀，並非必要。

變數名稱也可以透過再次宣告來重複使用，這稱為_遮蔽 (shadowing)_。與重新賦值不同，遮蔽會建立一個新變數，因此它對不可變變數也適用，並且可以改變型別：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=shadowing

```

## 布林值 (Booleans) {#booleans}

`bool` 型別只有兩個值 —— 關鍵字 `true` 和 `false` —— 且編譯器總是能推斷出來，因此 `bool` 永遠不需要型別標註。布林值可以與邏輯運算子 `&&`（且）、`||`（或）、`!`（非）組合使用，其中 `&&` 和 `||` 具有短路求值特性：若左側已經能決定結果，則不會求值右側。

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=boolean

```

布林值用於儲存旗標與驅動條件判斷 —— 也就是 [控制流程](./control-flow) 章節所介紹的 `if` 與 `while` 運算式。

## 整數型別 (Integer Types) {#integer-types}

Move 有六種整數型別，差異僅在於大小 —— 且全部都是_無號的_：Move 中沒有負整數，也沒有專門的有號型別。

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

最常用的是 `u64` —— 代幣數量、大小與索引都使用它。整數字面值可以用十進位（`42`）書寫，並可選擇性地加上底線以提高可讀性（`1_000_000`），或是用 `0x` 前綴以十六進位表示（`0x2A`）：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integers

```

雖然 `true` 和 `false` 明確地就是布林值，但像 `42` 這樣的字面值可能是六種整數型別中的任何一種。編譯器會根據值的使用方式推斷型別，預設為 `u64`；當推斷不夠用時 —— 或是明確寫出來更清楚時 —— 可以用型別標註或字面值後綴來指定型別：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integer_explicit_type

```

### 運算 (Operations) {#operations}

Move 支援整數的標準算術運算：加法、減法、乘法、除法與取模（餘數）。這些運算都不能產生超出該型別範圍的值 —— 運算並不會回繞，而是會直接中止：

<div class="modules-table">

| 語法 | 運算           | 中止條件                 |
| ---- | -------------- | ------------------------ |
| +    | 加法           | 結果對該整數型別而言過大 |
| -    | 減法           | 結果小於零               |
| \*   | 乘法           | 結果對該整數型別而言過大 |
| %    | 取模（餘數）   | 除數為 0                 |
| /    | 無條件捨去除法 | 除數為 0                 |

</div>

除法是_無條件捨去_的：沒有小數值，任何餘數都會被捨棄，所以 `7 / 2` 等於 `3`。整數也可以用 `==`、`!=`、`<`、`>`、`<=` 和 `>=` 進行比較，產生一個 `bool`：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=comparison

```

在每一個運算與比較中，運算元的型別_必須相符_ —— 整數型別之間沒有隱式轉換，將 `u8` 與 `u64` 相加會導致編譯錯誤。若要對不同型別進行運算，其中一個運算元必須先明確轉型。

> 想瞭解更多運算，包含位元運算，請參閱
> [Move 參考文件](./../../reference/primitive-types/integers#bitwise)。

### 使用 `as` 轉型 (Casting with `as`) {#casting-with-as}

`as` 運算子可以將整數從一種型別轉換為另一種型別。請注意，含有轉型的運算式通常需要加上括號以避免歧義：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=cast_as

```

_向上_轉型到較大的型別永遠會成功。_向下_轉型則必須能夠容納：與那些會靜默截斷值的語言不同，當數值超出範圍時 Move 會中止：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=downcast

```

向上轉型的一個常見用途，是為無法放入原本型別的中間結果騰出空間：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=overflow

```

### 溢位與下溢 (Overflow and Underflow) {#overflow-and-underflow}

如運算表所示，Move 中的算術運算永遠不會回繞。若運算結果無法放入該型別 —— 過大或小於零 —— 則會在執行時中止：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=overflow_abort

```

這是一項刻意設計的安全機制。靜默溢位是智能合約 bug 的經典來源 ——
一個餘額回繞成零，或是一個檢查因為某個值悄悄變小而通過。
Move 把每一種這樣的情況都變成一次會讓交易回復的響亮失敗。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Bool](./../../reference/primitive-types/bool)。
- Move 參考文件中的 [Integer](./../../reference/primitive-types/integers)。
- [std::u64](https://docs.sui.io/references/framework/std/u64) 模組文件 —— 每種整數
  型別都有一個輔助模組（`std::u8` 到 `std::u256`），內含 `min`、`max`、`sqrt`
  等函式。
