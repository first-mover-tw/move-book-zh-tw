---
title: 能力 (Abilities) | 參考手冊
description: Move 能力（abilities）參考手冊：copy、drop、store 與 key — 決定數值如何被使用、儲存、複製與捨棄的規則。
---

# 能力 (Abilities)

能力 (Abilities) 是 Move 中的一項型別功能，用於控制對給定型別的數值允許執行哪些操作。此系統可以對數值的「線性 (linear)」型別行為進行細粒度控制，並決定數值是否以及如何在儲存中使用（如 Move 的具體部署所定義的，例如區塊鏈的儲存概念）。這是透過對某些位元組碼指令進行存取控制來實現的，因此數值若要與該位元組碼指令一起使用，就必須具備所需的能力（如果需要的話 —— 並非所有指令都受能力的限制）。

對於 Sui 而言，`key` 被用來表示一項 [物件 (Object)](./abilities/object)。物件是儲存的基本單位，每個物件都有一個唯一的 32 位元組 ID。`store` 則用於指示哪些資料可以儲存在物件內部，同時也用於指示哪些型別可以被轉移到其定義模組之外。

## 四種能力

這四種能力分別是：

- [`copy`](#copy)
  - 允許具有此能力的型別的數值被複製。
- [`drop`](#drop)
  - 允許具有此能力的型別的數值被彈出 (popped) 或丟棄 (dropped)。
- [`store`](#store)
  - 允許具有此能力的型別的數值存在於儲存中的某個數值內。
  - 對於 Sui 而言，`store` 控制哪些資料可以儲存在 [物件 (Object)](./abilities/object) 內部。`store` 還控制哪些型別可以被轉移到其定義模組之外。
- [`key`](#key)
  - 允許該型別作為儲存的「鍵 (key)」。表面上，這意味著該數值可以作為儲存中的頂層數值；換句話說，它不需要包含在另一個數值中即可存在於儲存中。
  - 對於 Sui 而言，`key` 被用來表示一項 [物件 (Object)](./abilities/object)。

### `copy`

`copy` 能力允許具有該能力的型別的數值被複製。它限制了使用 [`copy`](./variables#move-and-copy) 運算子從本地變數複製數值的能力，以及透過[解參考 `*e`](./primitive-types/references#reading-and-writing-through-references) 透過參考複製數值的能力。

如果一個數值具有 `copy`，則該數值內包含的所有數值也都具有 `copy`。

### `drop`

`drop` 能力允許具有該能力的型別的數值被丟棄。所謂丟棄，是指該數值未被轉移，並且在 Move 程式執行時被有效地銷毀。因此，這種能力限制了在多處位置忽略數值的能力，包括：

- 在本地變數或參數中不使用該數值
- 在[透過 `;` 連接的序列](./variables#expression-blocks)中不使用該數值
- 在[賦值](./variables#move-and-copy)中覆寫變數中的數值
- 在[寫入 `*e1 = e2`](./primitive-types/references#reading-and-writing-through-references) 時透過參考覆寫數值。

如果一個數值具有 `drop`，則該數值內包含的所有數值也都具有 `drop`。

### `store`

`store` 能力允許具有此能力的型別的數值存在於儲存中的某個數值內，但*不一定*是作為儲存中的頂層數值。這是唯一不直接限制操作的能力。相反，它與 `key` 配合使用時限制了在儲存中的存在。

如果一個數值具有 `store`，則該數值內包含的所有數值也都具有 `store`。

對於 Sui 而言，`store` 具有雙重職責。它控制哪些數值可以出現在 [物件](/storage/store-ability) 內部，以及哪些物件可以被[轉移](./abilities/object#transfer-rules)到其定義模組之外。

### `key`

`key` 能力允許該型別充當 Move 部署所定義的儲存操作的鍵。雖然它因 Move 實例而異，但它用於限制所有儲存操作，因此為了將某個型別與儲存原語 (primitives) 一起使用，該型別必須具有 `key` 能力。

如果一個數值具有 `key`，則該數值中包含的所有數值都必須具有 `store`。這是唯一具有這種不對稱性的能力。

對於 Sui 而言，`key` 被用來表示一項 [物件 (Object)](./abilities/object)。

## 內建型別 (Builtin Types)

所有原始內建型別都具有 `copy`、`drop` 和 `store` 能力。

- `bool`、`u8`、`u16`、`u32`、`u64`、`u128`、`u256` 以及 `address` 全都具有 `copy`、`drop` 和 `store`。
- `vector<T>` 可能具有 `copy`、`drop` 和 `store`，具體取決於 `T` 的能力。
  - 詳情請參閱[條件能力與泛型型別](#conditional-abilities-and-generic-types)。
- 不可變參考 `&` 和可變參考 `&mut` 全都具有 `copy` 和 `drop`。
  - 這指的是複製和丟棄參考本身，而不是它們所指向的內容。
  - 參考不能出現在全域儲存中，因此它們不具有 `store`。

請注意，原始型別都不具備 `key` 能力，這意味著它們都不能直接與儲存操作一起使用。

## 標記結構體與列舉 {#annotating-structs-and-enums}

要宣告 `struct` 或 `enum` 具有某種能力，可以在資料型別名稱之後、欄位/變體之前或之後使用 `has <ability>`。例如：

```move file=packages/reference/sources/abilities.move anchor=annotating_datatypes

```

在這種情況下：`Ignorable*` 具有 `drop` 能力。`Pair*` 和 `MyVec*` 都具有 `copy`、`drop` 和 `store`。

所有這些能力都對這些受限操作提供了強大的保證。只有在數值具備該能力時，才能對其執行該操作；即使該數值深深巢狀在某些其他集合內部也是如此！

因此：在宣告結構體的能力時，對欄位有一定的要求。所有欄位都必須滿足這些約束。這些規則是必要的，以便結構體滿足上述能力的連通性規則。如果一個結構體宣告具備以下能力...

- `copy`：所有欄位都必須具備 `copy`。
- `drop`：所有欄位都必須具備 `drop`。
- `store`：所有欄位都必須具備 `store`。
- `key`：所有欄位都必須具備 `store`。
  - `key` 是目前唯一不需要自身具備相同能力的。

列舉可以具備除了 `key` 以外的任何能力，列舉不能具備 `key` 是因為它們不能作為儲存中的頂層數值（物件）。不過，對於列舉變體的欄位，同樣適用於結構體欄位的規則。特別是，如果一個列舉宣告具備以下能力...

- `copy`：所有變體的所有欄位都必須具備 `copy`。
- `drop`：所有變體的所有欄位都必須具備 `drop`。
- `store`：所有變體的所有欄位都必須具備 `store`。
- `key`：如前所述，列舉不允許使用此能力。

例如：

```move
// 一個沒有任何能力的結構體
public struct NoAbilities {}

public struct WantsCopy has copy {
    f: NoAbilities, // ERROR 'NoAbilities' 不具備 'copy'
}

public enum WantsCopyEnum has copy {
    Variant1,
    Variant2(NoAbilities), // ERROR 'NoAbilities' 不具備 'copy'
}
```

同樣地：

```move
// 一個沒有任何能力的結構體
public struct NoAbilities {}

public struct MyData has key {
    f: NoAbilities, // Error 'NoAbilities' 不具備 'store'
}

public struct MyDataEnum has store {
    Variant1,
    Variant2(NoAbilities), // Error 'NoAbilities' 不具備 'store'
}
```

## 條件能力與泛型型別 (Conditional Abilities and Generic Types) {#conditional-abilities-and-generic-types}

當在泛型型別上標記能力時，並非該型別的所有實例都保證具備該能力。考慮這個結構體宣告：

```move
public struct Cup<T> has copy, drop, store, key { item: T }
```

如果 `Cup` 可以容納任何型別，無論其能力如何，這將非常有幫助。型別系統可以 _看到_ 型別參數，因此如果它 _看到_ 一個會違反該能力保證的型別參數，它應該能夠移除 `Cup` 的能力。

這種行為起初聽起來可能有點令人困惑，但如果我們考慮集合型別，可能會更容易理解。我們可以認為內建型別 `vector` 具有以下型別宣告：

```move
vector<T> has copy, drop, store;
```

我們希望 `vector` 能夠與任何型別配合使用。我們不希望針對不同能力使用不同的 `vector` 型別。那麼我們想要什麼規則呢？正是我們在上面欄位規則中所想要的。因此，只有在內部元素可以被複製時，複製 `vector` 數值才是安全的。只有在內部元素可以被忽略/丟棄時，忽略 `vector` 數值才是安全的。並且，只有在內部元素可以存在於儲存中時，將 `vector` 放入儲存才是安全的。

為了擁有這種額外的表現力，一個型別可能不具備它宣告時的所有能力，這取決於該型別的實例化；相反，一個型別將具備的能力取決於其宣告 **以及** 其型別參數。對於任何型別，型別參數都會被悲觀地假設在結構體內部使用，因此只有在型別參數滿足上述欄位要求時，才會授予能力。以上面的 `Cup` 為例：

- 只有當 `T` 具備 `copy` 時，`Cup` 才具備 `copy` 能力。
- 只有當 `T` 具備 `drop` 時，它才具備 `drop`。
- 只有當 `T` 具備 `store` 時，它才具備 `store`。
- 只有當 `T` 具備 `store` 時，它才具備 `key`。

以下是針對每種能力的此類條件系統示例：

### 示例：條件 `copy`

```move
public struct NoAbilities {}
public struct S has copy, drop { f: bool }
public struct Cup<T> has copy, drop, store { item: T }

fun example(c_x: Cup<u64>, c_s: Cup<S>) {
    // 有效，'Cup<u64>' 具備 'copy' 因為 'u64' 具備 'copy'
    let c_x2 = copy c_x;
    // 有效，'Cup<S>' 具備 'copy' 因為 'S' 具備 'copy'
    let c_s2 = copy c_s;
}

fun invalid(c_account: Cup<signer>, c_n: Cup<NoAbilities>) {
    // 無效，'Cup<signer>' 不具備 'copy'。
    // 儘管 'Cup' 宣告具備 copy，但該實例不具備 'copy'，
    // 因為 'signer' 不具備 'copy'
    let c_account2 = copy c_account;
    // 無效，'Cup<NoAbilities>' 不具備 'copy'，
    // 因為 'NoAbilities' 不具備 'copy'
    let c_n2 = copy c_n;
}
```

### 示例：條件 `drop`

```move
public struct NoAbilities {}
public struct S has copy, drop { f: bool }
public struct Cup<T> has copy, drop, store { item: T }

fun unused() {
    Cup<bool> { item: true }; // 有效，'Cup<bool>' 具備 'drop'
    Cup<S> { item: S { f: false }}; // 有效，'Cup<S>' 具備 'drop'
}

fun left_in_local(c_account: Cup<signer>): u64 {
    let c_b = Cup<bool> { item: true };
    let c_s = Cup<S> { item: S { f: false }};
    // 有效回傳：'c_account', 'c_b', 與 'c_s' 都有數值
    // 但 'Cup<signer>', 'Cup<bool>', 與 'Cup<S>' 都具備 'drop'
    0
}

fun invalid_unused() {
    // 無效，不能忽略 'Cup<NoAbilities>' 因為它不具備 'drop'。
    // 儘管 'Cup' 宣告具備 'drop'，但該實例不具備 'drop'，
    // 因為 'NoAbilities' 不具備 'drop'
    Cup<NoAbilities> { item: NoAbilities {} };
}

fun invalid_left_in_local(): u64 {
    let n = Cup<NoAbilities> { item: NoAbilities {} };
    // 無效回傳：'c_n' 有數值
    // 且 'Cup<NoAbilities>' 不具備 'drop'
    0
}
```

### 示例：條件 `store`

```move
public struct Cup<T> has copy, drop, store { item: T }

// 'MyInnerData 宣告具備 'store'，所以所有欄位都需要 'store'
struct MyInnerData has store {
    yes: Cup<u64>, // 有效，'Cup<u64>' 具備 'store'
    // no: Cup<signer>, 無效，'Cup<signer>' 不具備 'store'
}

// 'MyData' 宣告具備 'key'，所以所有欄位都需要 'store'
struct MyData has key {
    yes: Cup<u64>, // 有效，'Cup<u64>' 具備 'store'
    inner: Cup<MyInnerData>, // 有效，'Cup<MyInnerData>' 具備 'store'
    // no: Cup<signer>, 無效，'Cup<signer>' 不具備 'store'
}
```

### 示例：條件 `key`

```move
public struct NoAbilities {}
public struct MyData<T> has key { f: T }

fun valid(addr: address) acquires MyData {
    // 有效，'MyData<u64>' 具備 'key'
    transfer(addr, MyData<u64> { f: 0 });
}

fun invalid(addr: address) {
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   transfer(addr, MyData<NoAbilities> { f: NoAbilities {} });
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   borrow<NoAbilities>(addr);
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   borrow_mut<NoAbilities>(addr);
}

// 模擬儲存操作
native public fun transfer<T: key>(addr: address, value: T);
```
