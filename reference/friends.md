---
title: 朋友 (Friends) | 參考手冊
description: Move 朋友 (friends) 參考手冊（已淘汰）：舊版朋友語法已由 Move 2024 中的 `public(package)` 可見性取代。
keywords:
  - Move
  - Sui
  - Move reference
  - friends
  - reference
questions:
  - How does Friends work in Move?
  - What is the syntax for Friends in Move?
  - What is Friend declaration in Move?
answer: 'Move friends reference (deprecated): the legacy friend syntax replaced by public(package) visibility in Move 2024.'
goal:
  description: 'Reader understands move friends reference (deprecated): the legacy friend syntax replaced by public(package) visibility in Move 2024'
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

# 已淘汰：友元 (DEPRECATED: Friends) {#deprecated-friends}

注意：此功能已由 [`public(package)`](./functions#visibility) 取代。

`friend` 語法用於宣告目前模組所信任的模組。受信任的模組可以呼叫目前模組中任何具有 `public(friend)`
可見性的函式。如需函式可見性的詳細資訊，請參閱
[函式](./functions)中的 _可見性_ 章節。

## 友元宣告 (Friend declaration) {#friend-declaration}

模組可以透過友元宣告陳述式將其他模組宣告為友元，格式如下：

- `friend <address::name>` — 使用完整限定模組名稱的友元宣告，如以下範例所示；或

  ```move
  module 0x42::a {
      friend 0x42::b;
  }
  ```

- `friend <module-name-alias>` — 使用模組名稱別名的友元宣告，其中模組別名是透過 `use` 陳述式引入。

  ```move
  module 0x42::a {
      use 0x42::b;
      friend b;
  }
  ```

一個模組可以有多個友元宣告，所有友元模組的聯集會形成友元清單。在以下範例中，`0x42::B` 和 `0x42::C`
都被視為 `0x42::A` 的友元。

```move
module 0x42::a;

friend 0x42::b;
friend 0x42::c;
```

不同於 `use` 陳述式，`friend` 只能在模組範圍內宣告，不能在運算式區塊範圍內宣告。`friend`
宣告可以位於任何允許頂層建構（例如 `use`、`function`、`struct` 等）的位置。不過，為了可讀性，建議將友元
宣告放在模組定義的開頭附近。

### 友元宣告規則 (Friend declaration rules) {#friend-declaration-rules}

友元宣告須遵守下列規則：

- 模組不能將自身宣告為友元。

  ```move
  module 0x42::m { friend Self; // 錯誤！ }
  //                      ^^^^ 不能將模組自身宣告為友元

  module 0x43::m { friend 0x43::M; // 錯誤！ }
  //                      ^^^^^^^ 不能將模組自身宣告為友元
  ```

- 編譯器必須知道友元模組。

  ```move
  module 0x42::m { friend 0x42::nonexistent; // 錯誤！ }
  //                      ^^^^^^^^^^^^^^^^^ 未繫結的模組 '0x42::nonexistent'
  ```

- 友元模組必須位於相同的帳戶地址內。

  ```move
  module 0x42::m {}

  module 0x42::n { friend 0x42::m; // 錯誤！ }
  //                      ^^^^^^^ 不能將目前地址以外的模組宣告為友元
  ```

- 友元關係不能建立迴圈模組依賴項。

  友元關係不允許迴圈，例如，`0x2::a` 將 `0x2::b` 視為友元，`0x2::b` 將 `0x2::c` 視為友元，
  `0x2::c` 又將 `0x2::a` 視為友元的關係不被允許。更一般地說，宣告友元模組會將目前模組的依賴項加入
  至友元模組（因為其目的是讓友元呼叫目前模組中的函式）。若該友元模組已被直接或間接使用，便會建立
  迴圈依賴項。

  ```move
  module 0x2::a {
      use 0x2::c;
      friend 0x2::b;

      public fun a() {
          c::c()
      }
  }

  module 0x2::b {
      friend 0x2::c; // 錯誤！
  //         ^^^^^^ 此友元關係建立了依賴項循環：'0x2::b' 是 '0x2::a' 的友元，後者使用 '0x2::c'，而 '0x2::c' 是 '0x2::b' 的友元
  }

  module 0x2::c {
      public fun c() {}
  }
  ```

- 模組的友元清單不能包含重複項目。

  ```move
  module 0x42::a {}

  module 0x42::m {
      use 0x42::a as aliased_a;
      friend 0x42::A;
      friend aliased_a; // 錯誤！
  //         ^^^^^^^^^ 重複的友元宣告 '0x42::a'。模組中的友元宣告必須是唯一的
  }
  ```
