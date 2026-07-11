---
title: 已棄用：友元 (Friends) | Reference
description: Move 好友參考手冊 (已淘汰)：被 Move 2024 中 public(package) 可見性取代的舊版 friend 語法。
---

# 已棄用：友元 (DEPRECATED: Friends)

注意：此功能已被 [`public(package)`](./functions#visibility) 取代。

`friend` 語法用於聲明受當前模組信賴的模組。受信賴的模組允許呼叫在當前模組中定義的任何具有 `public(friend)` 可見性的函式。有關函式可見性的詳細資訊，請參閱[函式](./functions)中的 _可見性_ 部分。

## 友元宣告

一個模組可以通過友元宣告語句聲明其他模組為友元，格式為

- `friend <address::name>` — 使用完全限定模組名稱的友元宣告，如下例所示

  ```move
  module 0x42::a {
      friend 0x42::b;
  }
  ```

- `friend <module-name-alias>` — 使用模組名稱別名的友元宣告，其中模組別名通過 `use` 語句引入。

  ```move
  module 0x42::a {
      use 0x42::b;
      friend b;
  }
  ```

一個模組可以有多個友元宣告，所有友元模組的聯合形成友元列表。在下面的例子中，`0x42::B` 和 `0x42::C` 都被視為 `0x42::A` 的友元。

```move
module 0x42::a;

friend 0x42::b;
friend 0x42::c;
```

與 `use` 語句不同，`friend` 只能在模組作用域中宣告，不能在表達式區塊作用域中。`friend` 宣告可以位於允許頂層構造（例如 `use`、`function`、`struct` 等）的任何位置。但是，為了可讀性，建議在模組定義的開始附近放置友元宣告。

### 友元宣告規則

友元宣告受以下規則約束：

- 一個模組不能將自身聲明為友元。

  ```move
  module 0x42::m { friend Self; // 錯誤！ }
  //                      ^^^^ 不能將模組本身聲明為友元

  module 0x43::m { friend 0x43::M; // 錯誤！ }
  //                      ^^^^^^^ 不能將模組本身聲明為友元
  ```

- 友元模組必須被編譯器已知

  ```move
  module 0x42::m { friend 0x42::nonexistent; // 錯誤！ }
  //                      ^^^^^^^^^^^^^^^^^ 未綁定的模組 '0x42::nonexistent'
  ```

- 友元模組必須在同一帳戶地址內。

  ```move
  module 0x42::m {}

  module 0x42::n { friend 0x42::m; // 錯誤！ }
  //                      ^^^^^^^ 不能將當前地址外的模組聲明為友元
  ```

- 友元關係不能建立循環模組依賴。

  友元關係中不允許循環，例如關係 `0x2::a` 的友元是 `0x2::b` 的友元是 `0x2::c` 的友元是 `0x2::a` 是不允許的。更一般地說，聲明一個友元模組會向友元模組添加對當前模組的依賴（因為目的是讓友元呼叫當前模組中的函式）。如果該友元模組已經被使用過，無論是直接還是傳遞性地，都會建立一個依賴循環。

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
  //         ^^^^^^ 此友元關係建立了一個依賴循環：'0x2::b' 是 '0x2::a' 的友元，使用 '0x2::c' 是 '0x2::b' 的友元
  }

  module 0x2::c {
      public fun c() {}
  }
  ```

- 一個模組的友元列表不能包含重複項。

  ```move
  module 0x42::a {}

  module 0x42::m {
      use 0x42::a as aliased_a;
      friend 0x42::A;
      friend aliased_a; // 錯誤！
  //         ^^^^^^^^^ 重複的友元宣告 '0x42::a'。模組中的友元宣告必須是唯一的
  }
  ```
