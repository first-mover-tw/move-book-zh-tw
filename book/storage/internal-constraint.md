---
description: Sui 驗證器 (Verifier) 的內部限制 (internal constraint)：為何儲存操作 (storage operations) 要求類型 (type) 必須定義於呼叫模組 (calling module) 中。
title: Sui 驗證器 (Verifier)：內部約束 (Internal Constraint)
keywords:
  - Move
  - Sui
  - Move tutorial
  - sui
  - verifier
  - internal
  - constraint
questions:
  - 'What is Sui Verifier: Internal Constraint in Move?'
  - 'How do I use Sui Verifier: Internal Constraint in Move?'
answer: 'The Sui Verifier internal constraint: why storage operations require the type to be defined in the calling module.'
goal:
  description: 'Reader understands the Sui Verifier internal constraint: why storage operations require the type to be defined in the calling module'
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

# Sui 驗證器：內部限制 (Sui Verifier: Internal Constraint) {#sui-verifier-internal-constraint}

在 [內部許可](./../move-basics/internal-permit)章節中，我們介紹了*內部型別
參數*：只接受於呼叫模組中定義之型別的型別參數。在該章節中，
`std::internal::permit<T>()` 使用此規則產生證明值。在 Sui 上，相同規則會*直接*
保護少數關鍵框架函式——不涉及許可值——而負責強制執行此規則的元件便是*Sui 驗證器*。

Sui 驗證器是一組位元碼層級的檢查，會在編譯期間及套件發布至鏈上時，於一般 Move
驗證之上執行。其大部分規則皆將本章先前已說明的內容形式化——例如
[key 能力](./key-ability)章節中的 `id: UID` 第一欄位要求。對接下來內容最重要的是
_內部限制_：標記了此限制的函式，只能以*內部*型別參數 `T` 呼叫——也就是在呼叫模組中
定義的型別。

讓我們看看經典範例：`sui::event` 模組中的 `emit` 函式（於
[事件](./../programmability/events)章節詳細說明），其要求型別參數必須是呼叫端的內部型別：

```move
module sui::event;

// 若從未定義 `T` 的模組呼叫此函式，Sui 驗證器將在編譯時
// 產生錯誤。
public native fun emit<T: copy + drop>(event: T);
```

以下是正確的 `emit` 呼叫。型別 `A` 定義於進行呼叫的相同模組中，因此符合限制：

```move file=packages/samples/sources/storage/internal-constraint.move anchor=main

```

但若以其他位置定義的型別呼叫 `emit`——例如來自
[標準函式庫](./../move-basics/standard-library)的 `TypeName` 型別——則會遭拒絕：

```move
// 此呼叫會失敗！
public fun call_foreign_fail() {
    use std::type_name;

    event::emit(type_name::with_defining_ids<A>());
    // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 無效的事件。
    // 錯誤：呼叫 `sui::event::emit` 時，必須傳入於
    // 目前模組中定義的型別。
}
```

其效果與我們為[結構欄位](./../move-basics/struct#field-visibility)建立、並透過 `Permit`
推廣的權限規則相同：定義型別的模組決定該型別可進行哪些操作。對於 `emit`，這表示只有
定義模組可以發出其型別的事件；對於下一節的[儲存函式](./storage-functions)，則表示定義
模組完全掌控其物件如何進入儲存空間——除非它藉由加入
[`store`](./store-ability)能力選擇退出此限制。

## 總結 (Summary) {#summary}

- Sui 驗證器是一組在編譯時及發布時檢查的位元碼層級規則。
- 內部限制會將函式的型別參數限縮為於呼叫模組中定義的型別。
- 它適用於少數關鍵框架函式：`event::emit`，以及[下一節](./storage-functions)介紹的受限制
  儲存函式。

## 延伸閱讀 (Further Reading) {#further-reading}

- [內部許可](./../move-basics/internal-permit)——透過 `std::internal` 向任何函式庫提供的相同規則。
