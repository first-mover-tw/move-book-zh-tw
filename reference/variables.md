---
title: 'Local Variables and Scope | Reference'
description: 'Move local variables and scope: let bindings, mutability, type annotations, shadowing, and move semantics reference.'
---

# 變數 (Variables)

變數在 Move 中有兩種類型：局部變數 (local variables) 和常數 (constants)。局部變數用於儲存函數內部的數據，而常數用於定義在編譯時確定的固定值。

## 局部變數與作用域 (Locals and Scoping)

局部變數是透過 `let` 關鍵字宣告的。

```move
let x = 0;
let y = x + 1;
```

作用域 (Scope) 定義了變數的可見性。當作用域結束時，在該作用域中宣告的變數將不再可用。

## 運算式區塊 (Expression Blocks) {#expression-blocks}

運算式區塊是由花括號 `{}` 包圍的一系列語句。區塊的最後一個運算式是該區塊的結果值。

## 遮蔽 (Shadowing) {#shadowing}

如果 `let` 宣告了一個與現有變數同名的新變數，則舊變數在該作用域內將無法訪問。這被稱為「遮蔽」。遮蔽可以改變變數的類型。

## 移動與複製 (Move and Copy) {#move-and-copy}

Move 中的所有局部變數可以透過 `move` 或 `copy` 使用。

- **copy**: 建立一個值的新副本。這需要該類型具有 `copy` 能力。
- **move**: 將值從變數中移出而不進行複製。移動後，原變數將不再可用。

### 推斷 (Inference)

編譯器會自動推斷應使用 `move` 還是 `copy`：

- 具有 `copy` 能力的值（和參照）使用 `copy`。
- 其他所有值使用 `move`。
