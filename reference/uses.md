# 使用宣告 (Uses)

`use` 宣告用於將其他模組中定義的名稱引入當前作用域。這允許您使用縮寫名稱而不是完全限定名稱。

## 基本用法

```move
use <address>::<module name>;
use <address>::<module name> as <module alias>;
use <address>::<module name>::<module member>;
use <address>::<module name>::<module member> as <member alias>;
```

例如：

```move
use std::vector;
use std::option::{Self, Option, some, none};
```

## 別名 (Aliases)

您可以使用 `as` 關鍵字為模組或其成員定義別名。

```move
use std::vector as v;
use std::option::some as s;
```

## 作用域

- **在模組中**: `use` 宣告在整個模組中都可用。
- **在運算式區塊中**: `use` 宣告僅在該區塊內部可用，且必須位於區塊的最開始。

## 遮蔽 (Shadowing)

在運算式區塊中的 `use` 別名可以遮蔽外部作用域的同名別名或成員。

## 命名規則與唯一性

- 別名必須遵循與模組成員相同的命名規則（例如：結構體別名必須以大寫字母開頭）。
- 在同一作用域內，所有別名必須是唯一的。

## 未使用的 Use

未使用的 `use` 宣告或別名會導致編譯警告。
