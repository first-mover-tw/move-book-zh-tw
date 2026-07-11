---
description: 'The Sui Verifier internal constraint: why storage operations require the type to be defined in the calling module.'
---

# Sui 校驗器：內部約束 (Internal Constraint)

Sui 位元組碼校驗器 (Sui Bytecode Verifier) 對 Move 位元組碼強制執行一組規則，以確保關鍵存儲操作的安全。其中一項規則就是「內部約束」。它要求具有類型參數 `T` 的函式呼叫者必須是該類型的「定義模組 (defining module)」。換句話說，`T` 對於發起呼叫的模組來說必須是「內部的 (internal)」。

這項規則（目前）尚未成為 Move 語言本身的一部分，因此有時會讓人感到不透明。儘管如此，它是一項非常重要的規則，特別是在 Sui 上執行與存儲相關的操作時。

讓我們看一個來自 [Sui 框架][sui-framework] 的例子。[`sui::event`][event] 模組中的 `emit` 函式要求其類型參數 `T` 對於呼叫者來說必須是內部的：

```move
// 實際強制執行 `T` 的「內部 (internal)」約束的函式範例。
module sui::event;

// 如果從未定義 `T` 的模組呼叫此函式，Sui 校驗器將在編譯時發出錯誤。
public native fun emit<T: copy + drop>(event: T);
```

以下是對 `emit` 的正確呼叫。類型 `A` 定義在模組 `exercise_internal` 內部，因此它是內部的且有效：

```move
// 定義類型 `A`。
module book::exercise_internal;

use sui::event;

/// 此模組中定義的類型，因此在本地是內部的。
public struct A has copy, drop {}

// 運作正常，因為 `A` 定義在本地。
public fun call_internal() {
    event::emit(A {})
}
```

但如果您嘗試使用定義在其他地方的類型呼叫 `emit`，校驗器將會拒絕。例如，當將以下函式添加到同一個模組時，它會失敗，因為它嘗試使用來自 [標準函式庫][move-stdlib] 的 `TypeName` 類型：

```move
// 這一個會失敗！
public fun call_foreign_fail() {
    use std::type_name;

    event::emit(type_name::get<A>());
    // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 無效事。
    // 錯誤：`sui::event::emit` 必須使用在目前模組中定義的類型來呼叫。
}
```

內部約束僅適用於 [Sui 框架][sui-framework] 中的某些專屬函式。我們將在本書的後續內容中多次回到這個概念。

[sui-framework]: ./../programmability/sui-framework.md
[move-stdlib]: ./../move-basics/standard-library.md
[event]: ./../programmability/events.md
[reflection]: ./../move-basics/type-reflection.md
