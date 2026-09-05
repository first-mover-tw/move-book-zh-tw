---
title: 能力 (Abilities) | 參考手冊
description: Move 能力 (abilities) 參考手冊：copy、drop、store 與 key——值的使用、儲存、複製與捨棄規則。
keywords:
  - Move
  - Sui
  - Move reference
  - abilities
  - reference
questions:
  - How does Abilities work in Move?
  - What is the syntax for Abilities in Move?
  - What is The Four Abilities in Move?
  - What is Builtin Types in Move?
answer: 'Move abilities reference: copy, drop, store, and key — rules for how values can be used, stored, copied, and discarded.'
goal:
  description: 'Reader understands move abilities reference: copy, drop, store, and key — rules for how values can be used, stored, copied, and discarded'
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

# 能力 (Abilities) {#abilities}

能力是 Move 中的一項型別功能，用於控制指定型別的值允許執行哪些動作。此系統可精細控制值的「線性」型別行為，以及值是否與如何用於儲存空間（依 Move 的特定部署定義，例如區塊鏈的儲存空間概念）。其實作方式是限制對特定位元組碼指令的存取，因此若要將值用於某個位元組碼指令，它必須具備所需的能力（若確實需要能力——並非每個指令都受能力限制）。

對 Sui 而言，`key` 用於表示一個[物件](./abilities/object)。物件是儲存空間的基本單位，每個物件都有唯一的 32 位元組 ID。`store` 則用於同時表示哪些資料可儲存在物件內，也用於表示哪些型別可轉移至其定義模組之外。

<!-- TODO：未來或許新增詳細的逐步解說章節。我們在最後提供了一些範例，但說明為何恰好採用這組能力可能會很有幫助

如果你已經透過撰寫 Move 程式而對能力略有認識，但仍對其運作方式感到困惑，或許可跳至[動機說明](#motivating-walkthrough)章節，以了解此系統為何採用目前的設計方式。 -->

## 四種能力 (The Four Abilities) {#the-four-abilities}

四種能力如下：

- [`copy`](#copy)
  - 允許複製具有此能力之型別的值。
- [`drop`](#drop)
  - 允許彈出／捨棄具有此能力之型別的值。
- [`store`](#store)
  - 允許具有此能力之型別的值存在於儲存空間中的某個值內。
  - 對 Sui 而言，`store` 控制哪些資料可以儲存於[物件](./abilities/object)內。
    `store` 也控制哪些型別可轉移至其定義模組之外。
- [`key`](#key)
  - 允許型別作為儲存空間的「鍵」。表面上，這表示該值可以是儲存空間中的
    頂層值；換言之，它不需要包含在另一個值內即可存在於儲存空間中。
  - 對 Sui 而言，`key` 用於表示[物件](./abilities/object)。

### 複製 (`copy`) {#copy}

`copy` 能力允許複製具有該能力之型別的值。它控制了使用 [`copy`](./variables#move-and-copy)
運算子從區域變數複製值的能力，以及透過
[解參考 `*e`](./primitive-types/references#reading-and-writing-through-references)複製值的能力。

如果某個值具有 `copy`，則該值內包含的所有值也都具有 `copy`。

### 捨棄 (`drop`) {#drop}

`drop` 能力允許捨棄具有該能力之型別的值。所謂捨棄，是指該值不會被轉移，且會在 Move
程式執行時被有效地銷毀。因此，這項能力控制了在多個位置忽略值的能力，包括：

- 不使用區域變數或參數中的值
- 不使用[透過 `;` 的序列](./variables#expression-blocks)中的值
- 在[指派](./variables#assignments)中覆寫變數內的值
- 在透過參考
  [寫入 `*e1 = e2`](./primitive-types/references#reading-and-writing-through-references)時覆寫值。

如果某個值具有 `drop`，則該值內包含的所有值也都具有 `drop`。

### 儲存 (`store`) {#store}

`store` 能力允許具有此能力之型別的值存在於儲存空間中的某個值內，
_但_ 不一定能作為儲存空間中的頂層值。這是唯一不直接控制操作的能力。相反地，當它與
`key` 搭配使用時，會控制值能否存在於儲存空間中。

如果某個值具有 `store`，則該值內包含的所有值也都具有 `store`。

對 Sui 而言，`store` 具有雙重用途。它控制哪些值可以出現在
[物件](/storage/store-ability)內，以及哪些物件可以被
[轉移](./abilities/object#transfer-rules)至其定義模組之外。

### 鍵 (`key`) {#key}

`key` 能力允許型別作為由 Move 部署定義之儲存空間操作的鍵。雖然其具體定義會依各個
Move 實例而異，但它控制所有儲存空間操作；因此，若要將某個型別搭配儲存空間原始操作使用，
該型別必須具有 `key` 能力。

如果某個值具有 `key`，則該值內包含的所有值都具有 `store`。這是唯一具有此類非對稱性的能力。

對 Sui 而言，`key` 用於表示[物件](./abilities/object)。

## 內建型別 (Builtin Types) {#builtin-types}

所有基本內建型別都具有 `copy`、`drop` 與 `store`。

- `bool`、`u8`、`u16`、`u32`、`u64`、`u128`、`u256` 與 `address` 都具有 `copy`、`drop` 與
  `store`。
- `vector<T>` 是否具有 `copy`、`drop` 與 `store`，取決於 `T` 的能力。
  - 如需更多詳細資訊，請參閱[條件式能力與泛型型別 (Conditional Abilities and Generic Types)](#conditional-abilities-and-generic-types)。
- 不可變參考 `&` 與可變參考 `&mut` 都具有 `copy` 與 `drop`。
  - 這是指複製與丟棄參考本身，而非它們所參考的內容。
  - 參考無法出現在全域儲存空間中，因此不具有 `store`。

請注意，所有基本型別都不具有 `key`，這表示它們都無法直接搭配儲存操作使用。

## 結構與列舉的能力註記 (Annotating Structs and Enums) {#annotating-structs-and-enums}

若要宣告某個 `struct` 或 `enum` 具有能力，可在資料型別名稱之後使用 `has <ability>` 宣告，並置於欄位／變體之前或之後。例如：

```move file=packages/reference/sources/abilities.move anchor=annotating_datatypes

```

在此例中：`Ignorable*` 具有 `drop` 能力。`Pair*` 與 `MyVec*` 都具有 `copy`、`drop` 和 `store`。

所有這些能力都對這些受限制的操作提供強力保證。只有當值具有該能力時，才能對它執行操作；即使該值深度巢狀於其他集合中也是如此！

因此，在宣告結構的能力時，欄位必須符合特定要求。所有欄位都必須滿足這些限制。這些規則是必要的，讓結構能符合上述能力的可達性規則。若結構宣告了下列能力……

- `copy`，所有欄位都必須具有 `copy`。
- `drop`，所有欄位都必須具有 `drop`。
- `store`，所有欄位都必須具有 `store`。
- `key`，所有欄位都必須具有 `store`。
  - `key` 是目前唯一不要求欄位本身具有該能力的能力。

除了 `key` 之外，列舉可具有任一種這些能力；列舉無法具有 `key`，因為它們不能作為儲存空間中的最上層值（物件）。不過，套用於列舉變體欄位的規則與結構欄位相同。特別是，若列舉宣告了下列能力……

- `copy`，所有變體的所有欄位都必須具有 `copy`。
- `drop`，所有變體的所有欄位都必須具有 `drop`。
- `store`，所有變體的所有欄位都必須具有 `store`。
- `key`，如前所述，列舉不允許具有此能力。

例如：

```move
// 不具有任何能力的結構
public struct NoAbilities {}

public struct WantsCopy has copy {
    f: NoAbilities, // 錯誤：'NoAbilities' 不具有 'copy'
}

public enum WantsCopyEnum has copy {
    Variant1
    Variant2(NoAbilities), // 錯誤：'NoAbilities' 不具有 'copy'
}
```

同樣地：

```move
// 不具有任何能力的結構
public struct NoAbilities {}

public struct MyData has key {
    f: NoAbilities, // 錯誤：'NoAbilities' 不具有 'store'
}

public struct MyDataEnum has store {
    Variant1,
    Variant2(NoAbilities), // 錯誤：'NoAbilities' 不具有 'store'
}
```

## 條件式能力與泛型型別 (Conditional Abilities and Generic Types) {#conditional-abilities-and-generic-types}

當能力標註於泛型型別時，並非該型別的所有執行個體都保證具備該能力。請考慮以下 struct 宣告：

<!-- file=packages/reference/sources/abilities.move anchor=conditional_abilities -->

```move
public struct Cup<T> has copy, drop, store, key { item: T }
```

若 `Cup` 能夠容納任何型別，而不受其能力限制，將會非常有幫助。型別系統可以 _看見_ 型別參數，因此若它 _看見_ 會違反該能力保證的型別參數，就應該能從 `Cup` 移除能力。

這種行為一開始聽起來可能有些令人困惑，但若從集合型別的角度思考，可能會更容易理解。我們可以將內建型別 `vector` 視為具有以下型別宣告：

```move
vector<T> has copy, drop, store;
```

我們希望 `vector` 能搭配任何型別運作。我們不希望針對不同能力使用不同的 `vector` 型別。因此，我們會希望有哪些規則？確切來說，就是與上述欄位規則相同的規則。因此，只有在內部元素可複製時，複製 `vector` 值才是安全的。只有在內部元素可忽略／丟棄時，忽略 `vector` 值才是安全的。並且，只有在內部元素可儲存時，將 `vector` 放入儲存空間才是安全的。

為了具備這種額外的表達能力，型別可能不會擁有其宣告的所有能力，這取決於該型別的具現化方式；相反地，型別所具備的能力取決於其宣告 **以及** 型別引數。對於任何型別，會悲觀地假設型別參數用於 struct 內部，因此只有在型別參數符合上述欄位所描述的需求時，才會授予能力。以上方的 `Cup` 為例：

- 只有當 `T` 具備 `copy` 時，`Cup` 才具備能力 `copy`。
- 只有當 `T` 具備 `drop` 時，它才具備 `drop`。
- 只有當 `T` 具備 `store` 時，它才具備 `store`。
- 只有當 `T` 具備 `store` 時，它才具備 `key`。

以下是各能力在此條件式系統中的範例：

### 範例：條件式 `copy` (Example: conditional `copy`) {#example-conditional-copy}

```move
public struct NoAbilities {}
public struct S has copy, drop { f: bool }
public struct Cup<T> has copy, drop, store { item: T }

fun example(c_x: Cup<u64>, c_s: Cup<S>) {
    // 有效，因為 'u64' 具有 'copy'，所以 'Cup<u64>' 具有 'copy'
    let c_x2 = copy c_x;
    // 有效，因為 'S' 具有 'copy'，所以 'Cup<S>' 具有 'copy'
    let c_s2 = copy c_s;
}

fun invalid(c_account: Cup<signer>, c_n: Cup<NoAbilities>) {
    // 無效，'Cup<signer>' 不具備 'copy'。
    // 即使 'Cup' 宣告了 copy，該執行個體仍不具備 'copy'
    // 因為 'signer' 不具備 'copy'
    let c_account2 = copy c_account;
    // 無效，'Cup<NoAbilities>' 不具備 'copy'
    // 因為 'NoAbilities' 不具備 'copy'
    let c_n2 = copy c_n;
}
```

### 範例：條件式 `drop` (Example: conditional `drop`) {#example-conditional-drop}

```move
public struct NoAbilities {}
public struct S has copy, drop { f: bool }
public struct Cup<T> has copy, drop, store { item: T }

fun unused() {
    Cup<bool> { item: true }; // 有效，'Cup<bool>' 具有 'drop'
    Cup<S> { item: S { f: false }}; // 有效，'Cup<S>' 具有 'drop'
}

fun left_in_local(c_account: Cup<signer>): u64 {
    let c_b = Cup<bool> { item: true };
    let c_s = Cup<S> { item: S { f: false }};
    // 有效的回傳：'c_account'、'c_b' 與 'c_s' 都有值
    // 但 'Cup<signer>'、'Cup<bool>' 與 'Cup<S>' 都具有 'drop'
    0
}

fun invalid_unused() {
    // 無效，無法忽略 'Cup<NoAbilities>'，因為它不具備 'drop'。
    // 即使 'Cup' 宣告了 'drop'，該執行個體仍不具備 'drop'
    // 因為 'NoAbilities' 不具備 'drop'
    Cup<NoAbilities> { item: NoAbilities {} };
}

fun invalid_left_in_local(): u64 {
    let n = Cup<NoAbilities> { item: NoAbilities {} };
    // 無效的回傳：'c_n' 有值
    // 而且 'Cup<NoAbilities>' 不具備 'drop'
    0
}
```

### 範例：條件式 `store` (Example: conditional `store`) {#example-conditional-store}

```move
public struct Cup<T> has copy, drop, store { item: T }

// 'MyInnerData 宣告了 'store'，因此所有欄位都需要 'store'
struct MyInnerData has store {
    yes: Cup<u64>, // 有效，'Cup<u64>' 具有 'store'
    // no: Cup<signer>, 無效，'Cup<signer>' 不具備 'store'
}

// 'MyData' 宣告了 'key'，因此所有欄位都需要 'store'
struct MyData has key {
    yes: Cup<u64>, // 有效，'Cup<u64>' 具有 'store'
    inner: Cup<MyInnerData>, // 有效，'Cup<MyInnerData>' 具有 'store'
    // no: Cup<signer>, 無效，'Cup<signer>' 不具備 'store'
}
```

### 範例：條件式 `key` (Example: conditional `key`) {#example-conditional-key}

```move
public struct NoAbilities {}
public struct MyData<T> has key { f: T }

fun valid(addr: address) acquires MyData {
    // 有效，'MyData<u64>' 具有 'key'
    transfer(addr, MyData<u64> { f: 0 });
}

fun invalid(addr: address) {
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   transfer(addr, MyData<NoAbilities> { f: NoAbilities {} })
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   borrow<NoAbilities>(addr);
   // 無效，'MyData<NoAbilities>' 不具備 'key'
   borrow_mut<NoAbilities>(addr);
}

// 模擬儲存操作
native public fun transfer<T: key>(addr: address, value: T);
}
```
