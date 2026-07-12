---
title: 布林值 (Bool) | 參考手冊
description: 布林值型別參考 (bool)：true 與 false 字面值、邏輯運算子 (and, or, not)，以及布林運算式語意。
---

# 布林值 (Bool)

`bool` 是 Move 的布林值原生型別，包含 `true` 和 `false` 數值。

## 常值 (Literals)

`bool` 的常值為 `true` 或 `false`。

## 操作

### 邏輯運算

`bool` 支援三種邏輯操作：

| 語法                      | 描述                      | 等效運算式                                                |
| ------------------------- | ------------------------- | --------------------------------------------------------- |
| `&&`                      | 短路邏輯與 (logical and)  | `p && q` 等同於 `if (p) q else false`                     |
| <code>&vert;&vert;</code> | 短路邏輯或 (logical or)   | <code>p &vert;&vert; q</code> 等同於 `if (p) true else q` |
| `!`                       | 邏輯非 (logical negation) | `!p` 等同於 `if (p) false else true`                      |

### 控制流

`bool` 數值用於多個 Move 的控制流結構：

- [`if (bool) { ... }`](./../control-flow/conditionals)
- [`while (bool) { .. }`](./../control-flow/loops)
- [`assert!(bool, u64)`](./../abort-and-assert)

## 所有權 (Ownership)

與語言中內建的其他純量值 (scalar values) 一樣，布林值是隱式可複製的，這意味著它們可以在沒有明確指令（如 [`copy`](.././variables#move-and-copy)）的情況下被複製。
