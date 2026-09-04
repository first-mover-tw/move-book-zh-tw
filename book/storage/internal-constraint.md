---
description: Sui 驗證器 (Sui Verifier) 內部限制：為何儲存操作 (storage operations) 需要型別 (type) 定義於呼叫模組 (calling module) 中
---

# Sui 驗證器：內部約束 (Sui Verifier: Internal Constraint) {#sui-verifier-internal-constraint}

在[內部通行證](./../move-basics/internal-permit)章節中，我們介紹了 _內部型別參數_：只接受呼叫模組中定義之型別的型別參數。在該處，`std::internal::permit<T>()` 使用此規則來產生一個證明值。在 Sui 上，同樣的規則*直接*保護少數幾個關鍵的框架函式——不涉及通行證值——而執行此規則的元件就是 _Sui 驗證器_。

Sui 驗證器是一組位元組碼層級的檢查，會在一般 Move 驗證之上執行，無論是在編譯時期或是套件在鏈上發布時皆然。它的大部分規則都將本章已經描述過的內容形式化——例如[key 能力](./key-ability)章節中的 `id: UID` 首欄位要求。_內部約束_ 是接下來內容中最重要的規則：一個標記了此規則的函式，只能以 _內部_ 型別參數 `T` 呼叫——也就是在呼叫模組中定義的型別。

我們來看一個經典範例——`sui::event` 模組中的 `emit` 函式（在[事件](./../programmability/events)章節中有詳細說明），該函式要求其型別參數必須是呼叫者的內部型別：

```move
module sui::event;

// 如果這個函式被一個未定義 `T` 的模組呼叫，
// Sui 驗證器會在編譯時期發出錯誤。
public native fun emit<T: copy + drop>(event: T);
```

以下是一個對 `emit` 的正確呼叫。型別 `A` 定義於發出呼叫的同一模組中，因此滿足約束條件：

```move file=packages/samples/sources/storage/internal-constraint.move anchor=main

```

但如果以在別處定義的型別呼叫 `emit`——例如來自[標準函式庫](./../move-basics/standard-library)的 `TypeName` 型別——則會被拒絕：

```move
// 這個會失敗！
public fun call_foreign_fail() {
    use std::type_name;

    event::emit(type_name::with_defining_ids<A>());
    // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 無效的 event。
    // 錯誤：`sui::event::emit` 必須以在目前模組中
    // 定義的型別呼叫。
}
```

其效果與我們為[結構體欄位](./../move-basics/struct#field-visibility)所建立、並由 `Permit` 所概括的權責規則相同：定義該型別的模組決定該型別會發生什麼事。對 `emit` 而言，這代表只有定義模組能夠發出其型別的事件；對於下一節中的[儲存函式](./storage-functions)而言，這代表定義模組完全掌控其物件如何進入儲存——除非它透過加入 [`store`](./store-ability) 能力來選擇退出。

## 總結 (Summary) {#summary}

- Sui 驗證器是一組在編譯時期與發布時檢查的位元組碼層級規則。
- 內部約束將函式的型別參數限制為在呼叫模組中定義的型別。
- 它適用於少數幾個關鍵的框架函式：`event::emit`，以及[下一節](./storage-functions)中所涵蓋的受限儲存函式。

## 延伸閱讀 (Further Reading) {#further-reading}

- [內部通行證](./../move-basics/internal-permit)——同樣的規則，可透過 `std::internal` 供任何函式庫使用。
