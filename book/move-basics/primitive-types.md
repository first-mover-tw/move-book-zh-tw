# 原生類型 (Primitive Types)

對於簡單的值，Move 有許多內建的原生類型。它們是所有其他類型的基礎。原生類型包括：

- [布林值 (Booleans)](#booleans)
- [無號整數 (Unsigned Integers)](#integer-types)
- [地址 (Addresses)](./address) — 在下一節中介紹

在我們深入瞭解原生類型之前，讓我們先看看如何在 Move 中宣告和指派變數。

## 變數與指派 (Variables and Assignment)

變數使用 `let` 關鍵字宣告。它們預設是不可變的 (immutable)，但可以透過添加 `mut` 關鍵字使其變為可變的 (mutable)：

```
let <變數名稱>[: <類型>]  = <表達式>;
let mut <變數名稱>[: <類型>] = <表達式>;
```

其中：

- `<變數名稱>` — 變數的名稱
- `<類型>` — 變數的類型，選填
- `<表達式>` — 要指派給變數的值

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=variables_and_assignment

```

可變變數可以使用 `=` 運算子重新指派。

```move
y = 43;
```

變數也可以透過重新宣告來進行遮蔽 (shadowing)。

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=shadowing

```

## 布林值 (Booleans)

`bool` 類型表示布林值 — 是或否，真或假。它有兩個可能的值：`true` 和 `false`，它們是 Move 中的關鍵字。對於布林值，編譯器始終可以從值推斷類型，因此無需明確指定。

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=boolean

```

布林值通常用於儲存旗標和控制程式流程。請參考 [流程控制](./control-flow) 章節瞭解更多資訊。

## 整數類型 (Integer Types)

Move 支援各種大小的無號整數，從 8 位元到 256 位元。整數類型有：

- `u8` — 8 位元
- `u16` — 16 位元
- `u32` — 32 位元
- `u64` — 64 位元
- `u128` — 128 位元
- `u256` — 256 位元

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integers

```

布林常值如 `true` 和 `false` 顯然是布林值，但整數常值如 `42` 可以是任何整數類型。在大多數情況下，編譯器會從值中推斷類型，通常預設為 `u64`。然而，有時編譯器無法推斷類型，將需要明確的類型註解。這可以在指派期間提供，或透過使用類型後綴來提供。

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=integer_explicit_type

```

### 運算

Move 支援整數的標準算術運算：加法、減法、乘法、除法和取模（餘數）。這些運算的語法如下：

| 語法 | 運算                | 在以下情況中斷                         |
| ---- | ------------------- | -------------------------------------- |
| +    | 加法                | 結果對於該整數類型而言太大             |
| -    | 減法                | 結果小於零                             |
| \*   | 乘法                | 結果對於該整數類型而言太大             |
| %    | 取模 (餘數)         | 除數為 0                               |
| /    | 截斷除法 (整除)     | 除數為 0                               |

> 更多運算（包含位元運算），請參考 [Move 參考手冊](./../../reference/primitive-types/integers#bitwise)。

運算元的類型 **必須匹配**，否則編譯器將報錯。運算結果將與運算元具有相同的類型。若要對不同類型執行運算，運算元需要轉型為相同的類型。

### 使用 `as` 進行轉型 (Casting)

Move 支援在整數類型之間進行明確轉型。語法如下：

```move
<表達式> as <類型>
```

請注意，表達式周圍可能需要括號以防止歧義：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=cast_as

```

一個更複雜的例子，防止溢位：

```move file=packages/samples/sources/move-basics/primitive-types.move anchor=overflow

```

### 溢位 (Overflow)

Move 不支援溢位 / 負溢位 (underflow)；導致值超出類型範圍的運算將引發執行時期錯誤。這是一項安全功能，可防止非預期的行為。

```move
let x = 255u8;
let y = 1u8;

// 這將引發錯誤
let z = x + y;
```

## 延伸閱讀

- Move 參考手冊中的 [布林值 (Bool)](./../../reference/primitive-types/bool)。
- Move 參考手冊中的 [整數 (Integer)](./../../reference/primitive-types/integers)。
