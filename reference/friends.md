---
title: 已棄用：友元 (Friends) | Reference
description: Move 好友參考手冊 (已淘汰)：被 Move 2024 中 public(package) 可見性取代的舊版 friend 語法。
---

# 【已棄用】：友元 (DEPRECATED: Friends)

注意：此功能已被 [`public(package)`](./functions#visibility) 取代。

`friend` 語法曾用於宣告被當前模組信任的其他模組。受信任的模組允許呼叫當前模組中定義的任何具有 `public(friend)` 能見度的函式。有關函式能見度的詳細資訊，請參見 [函式](./functions) 中的 _能見度（Visibility）_ 章節。

## 友元宣告 (Friend declaration)

模組可以透過友元宣告陳述式將其他模組宣告為友元，格式如下：

- `friend <address::name>` —— 使用完整限定的模組名稱進行友元宣告，如下例所示：

  ```move
  module 0x42::a {
      friend 0x42::b;
  }
  ```

- `friend <module-name-alias>` —— 使用模組名稱別名進行友元宣告，其中的模組別名是透過 `use` 陳述式引入的。

  ```move
  module 0x42::a {
      use 0x42::b;
      friend b;
  }
  ```

一個模組可以有多個友元宣告，所有友元模組的聯集形成友元清單。在下例中，`0x42::B` 和 `0x42::C` 都被視為 `0x42::A` 的友元。

```move
module 0x42::a;

friend 0x42::b;
friend 0x42::c;
```

與 `use` 陳述式不同，`friend` 只能在模組作用域中宣告，而不能在運算式區塊作用域中宣告。`friend` 宣告可以位於任何允許頂層結構（如 `use`、`function`、`struct` 等）的地方。然而，為了可讀性，建議將友元宣告放置在模組定義的開頭附近。

### 友元宣告規則 (Friend declaration rules)

友元宣告須遵循以下規則：

- 模組不能將自己宣告為友元。

  ```move
  module 0x42::m { friend Self; // 錯誤！ }
  //                      ^^^^ 不能將模組本身宣告為友元

  module 0x43::m { friend 0x43::M; // 錯誤！ }
  //                      ^^^^^^^ 不能將模組本身宣告為友元
  ```

- 友元模組必須能被編譯器識別。

  ```move
  module 0x42::m { friend 0x42::nonexistent; // 錯誤！ }
  //                      ^^^^^^^^^^^^^^^^^ 未繫結的模組 '0x42::nonexistent'
  ```

- 友元模組必須位於相同的帳戶地址內。

  ```move
  module 0x42::m {}

  module 0x42::n { friend 0x42::m; // 錯誤！ }
  //                      ^^^^^^^ 不能將當前地址以外的模組宣告為友元
  ```

- 友元關係不能建立環狀 (cyclic) 模組依賴。

  友元關係中不允許環狀關係，例如不允許 `0x2::a` 友元 `0x2::b` 友元 `0x2::c` 友元 `0x2::a` 這樣的關係。更廣義地說，宣告一個友元模組會為該友元模組新增一個對當前模組的依賴（因為目的是讓友元能呼叫當前模組中的函式）。如果該友元模組已被直接或間接使用，則會建立環狀依賴。

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
  //         ^^^^^^ 此友元關係建立了環狀依賴：'0x2::b' 是 '0x2::a' 的友元，後者使用了 '0x2::c'，而 '0x2::c' 是 '0x2::b' 的友元
  }

  module 0x2::c {
      public fun c() {}
  }
  ```

- 模組的友元清單不能包含重複項。

  ```move
  module 0x42::a {}

  module 0x42::m {
      use 0x42::a as aliased_a;
      friend 0x42::A;
      friend aliased_a; // 錯誤！
  //         ^^^^^^^^^ 重複的友元宣告 '0x42::a'。模組中的友元宣告必須唯一
  }
  ```
