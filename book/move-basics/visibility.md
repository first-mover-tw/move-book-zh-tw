---
description: Move 中的可見度修飾詞 (Visibility Modifiers)：private、public、public(package)，以及用於控制模組成員存取權限的 entry 函式。
---

# 可見度修飾詞 (Visibility Modifiers) {#visibility-modifiers}

每個模組成員都有可見度。預設情況下，所有模組成員都是*私有的（private）*——意即它們只能在定義它們的模組內被存取。不過，你可以加上可見度修飾詞，讓模組成員變成*公開的（public）*——可在模組外被看見，或是*public(package)*——可在同一個 package 內的模組中被看見。此外，函式可以標記 _entry_ 修飾詞，讓一個*非公開的（non-public）* 函式能夠從交易中被呼叫。與其他修飾詞不同，`entry` 並非可見度層級——它可以與其他可見度修飾詞組合使用，且它控制的是函式如何與交易互動，而非與其他模組互動。

## 內部可見度 (Internal Visibility) {#internal-visibility}

一個在模組中定義、沒有可見度修飾詞的函式或結構體是該模組的*私有（private）* 成員。它無法從其他模組被呼叫。

```move
module book::internal_visibility;

// 這個函式可以從同一模組內的其他函式呼叫
fun internal() { /* ... */ }

// 同一模組 -> 可以呼叫 internal()
fun call_internal() {
    internal();
}
```

以下程式碼無法編譯，因為 `internal` 是 `book::internal_visibility` 的私有成員：

```move
module book::try_calling_internal;

use book::internal_visibility;

// 不同模組 -> 無法呼叫 internal()
fun try_calling_internal() {
    internal_visibility::internal();
    // ^ ERROR! [E04001]: 受限的可見性
    //   對內部函式的呼叫無效
    //   'book::internal_visibility::internal'
}
```

請注意，結構體欄位在 Move 中不可見，並不代表其值是保密的 &mdash; 從 Move 之外讀取鏈上物件的內容永遠是可行的。你不應該在物件中儲存未加密的機密資料。

## 公開可見度 (Public Visibility) {#public-visibility}

在 `fun` 或 `struct` 關鍵字前加上 `public` 關鍵字，可以讓結構體或函式變成*公開的（public）*。

```move
module book::public_visibility;

// 這個函式可以從其他模組呼叫
public fun public_fun() { /* ... */ }
```

公開函式可以被其他模組匯入並呼叫。以下程式碼可以編譯：

```move
module book::try_calling_public;

use book::public_visibility;

// 不同模組 -> 可以呼叫 public_fun()
fun try_calling_public() {
    public_visibility::public_fun();
}
```

`public` 函式也可以直接從[交易](./../concepts/what-is-a-transaction)中被呼叫。將函式設為 `public` 是預設——也是推薦——用來將功能開放給使用者的方式：公開函式可以作為交易中的一個命令，可以自由地與交易中的其他命令組合，並可作為其他 package 的建構區塊。這一切都不需要額外的修飾詞。

## Package 可見度 (Package Visibility) {#package-visibility}

具有 _package_ 可見度的函式可以從同一個 package 內的任何模組呼叫，但無法從其他 package 的模組呼叫。換句話說，它是 package 的*內部（internal）* 成員。

```move
module book::package_visibility;

public(package) fun package_only() { /* ... */ }
```

package 函式可以從同一個 package 內的任何模組呼叫：

```move
module book::try_calling_package;

use book::package_visibility;

// 同一個 package `book` -> 可以呼叫 package_only()
fun try_calling_package() {
    package_visibility::package_only();
}
```

## Entry 修飾詞 (Entry Modifier) {#entry-modifier}

如[上文](#public-visibility)所示，`public` 函式已經可以從[交易](./../concepts/what-is-a-transaction)中被呼叫——`public` 是預設且首選的方式，讓函式同時對交易與其他模組可用。`entry` 修飾詞的目標則相反：讓函式*只能*作為交易中的命令被呼叫。將一個*非公開的（non-public）* 函式標記為 `entry`，可以讓它無法被其他模組的程式碼呼叫，同時允許它作為交易命令——刻意限制誰能呼叫它以及如何呼叫。它並非可見度層級：`entry` 函式會保留宣告時所帶有的任何可見度。一個標記為 `entry` 且沒有其他修飾詞的函式，仍然是*私有的（private）*——可以作為交易命令被呼叫，也可以從其所屬模組內被呼叫，僅此而已。

```move
module book::entry_functions;

// 可以從交易中呼叫，但無法從其他模組呼叫
entry fun from_transaction_only() { /* ... */ }

// 可以從交易中呼叫，也可以從同一個 package 的模組中呼叫
public(package) entry fun from_package_or_transaction() { /* ... */ }
```

公開函式本來就已經可以從交易中被呼叫，所以 `entry` 對 `public` 函式而言不會增加任何東西，編譯器會對這種組合發出警告：

```text
warning[Lint W99010]: unnecessary `entry` on a `public` function
  │
7 │ public entry fun both() { }
  │        ^^^^^ `entry` on `public` is meaningless. In conjunction with `public`,
  │              `entry` adds no additional permissions or restrictions.
```

任何 Move 函式都可以被標記為 `entry`——它的函式簽章沒有任何限制。這個修飾詞的價值在於它對*非公開的（non-public）* 函式帶來的效果：它們可以作為交易命令被呼叫，同時保持在模組 API 之外——並且呼叫它們的交易，會對它傳入的引數接受額外的檢查。

這項保證與*熱馬鈴薯（hot potatoes）* 有關——也就是必須在交易結束前被消耗掉的值：一個非 `public` 的 `entry` 函式的引數，會被靜態保證不會與任何這類尚未了結的義務糾纏在一起，這正是 `entry` 能夠作為安全交易邊界的原因。完整規則連同一個完整運作的閃電貸範例，涵蓋在進階 Move 功能章節的[進入函式 (Entry Functions)](./../move-advanced/entry-functions)中。

總結來說：`entry` 會限制可組合性——在兩個方向上都是。一個非公開的 `entry` 函式並非模組 API 的一部分，因此其他 package 無法呼叫它或以它為基礎建構；而在交易中，它的引數會面臨 `public` 函式引數所沒有的限制。當這正是你要的效果時——當一個函式應該*只能*作為交易命令被呼叫，或是它需要引數保證時——就選擇使用它。至於其他情況，`public` 才是正確的選擇。

## 原生函式 (Native Functions) {#native-functions}

[framework](./../programmability/sui-framework) 與[標準函式庫](./standard-library)中的一些函式標記了 `native` 修飾詞。這些函式是由 Move VM 原生提供的，在 Move 原始碼中沒有函式主體。想進一步了解 native 修飾詞，請參閱
[Move Reference](./../../reference/functions?highlight=native#native-functions)。

```move
module std::type_name;

public native fun get<T>(): TypeName;
```

這是取自 `std::type_name` 的範例，可在[反射章節](./type-reflection)中進一步了解此模組。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[可見度 (Visibility)](./../../reference/functions#visibility)。
