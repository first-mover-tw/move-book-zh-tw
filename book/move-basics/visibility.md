---
description: Move 中的可見性修飾詞 (Visibility modifiers)：private、public、public(package) 與用於控制模組成員 (module members) 存取權的入口函式 (entry functions)。
title: 可見性修飾詞 (Visibility Modifiers)
keywords:
  - Move
  - Sui
  - Move tutorial
  - visibility
  - modifiers
questions:
  - What is Visibility Modifiers in Move?
  - How do I use Visibility Modifiers in Move?
  - What is Internal Visibility in Move?
  - What is Public Visibility in Move?
answer: 'Visibility modifiers in Move: private, public, public(package), and entry functions for controlling access to module members.'
goal:
  description: 'Reader understands visibility modifiers in Move: private, public, public(package), and entry functions for controlling access to module members'
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

# 可見性修飾詞 (Visibility Modifiers) {#visibility-modifiers}

每個模組成員都具有可見性。預設情況下，所有模組成員都是 _private_，這表示它們只能在其定義所在的模組內存取。不過，你可以加入可見性修飾詞，將模組成員設為 _public_，使其在模組外可見；或設為 _public(package)_，使其在相同套件內的模組中可見。此外，函式可以標記為 _entry_ 修飾詞，讓 _non-public_ 函式能夠從交易中呼叫。與其他修飾詞不同，`entry` 並非可見性層級；它可以與可見性修飾詞組合使用，且控制的是函式如何與交易互動，而非如何與其他模組互動。

## 內部可見性 (Internal Visibility) {#internal-visibility}

在模組中定義且沒有可見性修飾詞的函式或結構，是該模組的 _private_ 成員。它無法從其他模組呼叫。

```move
module book::internal_visibility;

// 此函式可從相同模組中的其他函式呼叫
fun internal() { /* ... */ }

// 相同模組 -> 可以呼叫 internal()
fun call_internal() {
    internal();
}
```

下列程式碼無法編譯，因為 `internal` 對 `book::internal_visibility` 而言是私有的：

```move
module book::try_calling_internal;

use book::internal_visibility;

// 不同模組 -> 無法呼叫 internal()
fun try_calling_internal() {
    internal_visibility::internal();
    // ^ 錯誤！[E04001]：受限制的可見性
    //   對內部函式的無效呼叫
    //   'book::internal_visibility::internal'
}
```

請注意，結構欄位無法從 Move 看見，並不表示其值會被保密 &mdash; 始終可以在 Move 外部讀取鏈上物件的內容。絕不應將未加密的機密資訊儲存在物件內。

## 公開可見性 (Public Visibility) {#public-visibility}

在 `fun` 或 `struct` 關鍵字之前加入 `public` 關鍵字，即可將結構或函式設為 _public_。

```move
module book::public_visibility;

// 此函式可從其他模組呼叫
public fun public_fun() { /* ... */ }
```

公開函式可由其他模組匯入及呼叫。下列程式碼可以編譯：

```move
module book::try_calling_public;

use book::public_visibility;

// 不同模組 -> 可以呼叫 public_fun()
fun try_calling_public() {
    public_visibility::public_fun();
}
```

`public` 函式也可以直接從[交易](./../concepts/what-is-a-transaction)呼叫。將函式設為 `public` 是向使用者公開功能的預設且建議方式：公開函式可以是交易中的命令、可與其中其他命令自由組合，並可作為其他套件的建構基礎。這些用途都不需要額外修飾詞。

## 套件可見性 (Package Visibility) {#package-visibility}

具有 _package_ 可見性的函式可從相同套件內的任何模組呼叫，但無法從其他套件中的模組呼叫。換句話說，它對套件而言是 _internal_。

```move
module book::package_visibility;

public(package) fun package_only() { /* ... */ }
```

套件函式可從相同套件內的任何模組呼叫：

```move
module book::try_calling_package;

use book::package_visibility;

// 相同套件 `book` -> 可以呼叫 package_only()
fun try_calling_package() {
    package_visibility::package_only();
}
```

## 入口修飾詞 (Entry Modifier) {#entry-modifier}

如[上文](#public-visibility)所示，`public` 函式已可從[交易](./../concepts/what-is-a-transaction)呼叫；`public` 是讓函式可供交易與其他模組使用的預設且首選方式。`entry` 修飾詞的目標則相反：讓函式 _only_ 能作為交易中的命令呼叫。以 `entry` 標記 _non-public_ 函式，可讓其他模組的原始碼無法觸及它，同時允許它作為交易命令使用，藉此刻意限制誰能呼叫它以及如何呼叫。它不是可見性層級：`entry` 函式會保留其宣告時指定的可見性。沒有其他修飾詞而標記為 `entry` 的函式仍是 _private_，可作為交易命令及從其自身模組呼叫，除此之外無法使用。

```move
module book::entry_functions;

// 可從交易呼叫，但無法從其他模組呼叫
entry fun from_transaction_only() { /* ... */ }

// 可從交易及相同套件的模組呼叫
public(package) entry fun from_package_or_transaction() { /* ... */ }
```

公開函式已可從交易呼叫，因此 `entry` 不會為 `public` 函式增加任何內容，編譯器會對此組合發出警告：

```text
warning[Lint W99010]: 在 `public` 函式上使用了不必要的 `entry`
  │
7 │ public entry fun both() { }
  │        ^^^^^ 在 `public` 上使用 `entry` 沒有意義。與 `public` 結合時，
  │              `entry` 不會增加額外權限或限制。
```

任何 Move 函式都可標記為 `entry`，其簽章沒有任何限制。此修飾詞的價值在於它對 _non-public_ 函式的作用：它們可作為交易命令呼叫，同時仍不會成為模組 API 的一部分；而呼叫它們的交易會接受對所傳遞引數的額外檢查。

此保證關乎 _hot potatoes_，亦即必須在交易結束前消耗的值：非 `public` `entry` 函式的引數，經靜態保證不會與任何此類尚未履行的義務糾纏在一起，這正是 `entry` 能作為安全交易邊界的原因。完整規則及可運作的快閃貸款範例，請參閱「進階 Move 功能」章節中的[入口函式](./../move-advanced/entry-functions)。

總結而言，`entry` 會雙向限制可組合性。非公開 `entry` 函式不是模組 API 的一部分，因此其他套件無法呼叫或以其為基礎建立功能；而在交易內，其引數會受到 `public` 函式引數所沒有的限制。當這正是目的時便應使用它，例如函式應 _only_ 作為交易命令呼叫，或需要該引數保證時。其他所有情況下，`public` 才是正確選擇。

## 原生函式 (Native Functions) {#native-functions}

[框架](./../programmability/sui-framework)和[標準函式庫](./standard-library)中的某些函式標記了 `native` 修飾詞。這些函式由 Move VM 原生提供，且在 Move 原始碼中沒有函式本體。若要進一步了解原生修飾詞，請參閱 [Move 參考文件](./../../reference/functions?highlight=native#native-functions)。

```move
module std::type_name;

public native fun get<T>(): TypeName;
```

這是來自 `std::type_name` 的範例；請在[反射章節](./type-reflection)中進一步了解此模組。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[可見性](./../../reference/functions#visibility)。
