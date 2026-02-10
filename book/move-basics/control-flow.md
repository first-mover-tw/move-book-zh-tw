# 流程控制 (Control Flow)

流程控制語句用於控制程式中執行的流向。它們可用於做出決策、重複執行一段程式碼，或提早退出一段程式碼。Move 包含以下流程控制語句（下文將詳細說明）：

- [`if` 和 `if-else`](#conditional-statements) — 決定是否執行一段程式碼
- [`loop` 和 `while` 迴圈](#repeating-statements-with-loops) — 重複執行一段程式碼
- [`break` 和 `continue` 語句](#exiting-a-loop-early) — 提早退出迴圈
- [`return`](#early-return) 語句 — 提早退出函式

## 條件語句 (Conditional Statements)

`if` 表達式用於在程式中做出決策。它會評估一個 [布林表達式](./expression#literals)，如果表達式為 true，則執行一段程式碼。與 `else` 配合使用時，如果表達式為 false，它可以執行另一段不同的程式碼。

`if` 表達式的語法為：

```move
if (<布林表達式>) <表達式>;
if (<布林表達式>) <表達式> else <表達式>;
```

就像任何其他表達式一樣，如果 `if` 後面還有其他表達式，則需要分號。`else` 關鍵字是選填的，除非將產生的值指派給變數，因為所有分支都必須傳回一個值以確保類型安全。讓我們透過以下範例看看 `if` 表達式在 Move 中是如何運作的：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_condition

```

讓我們看看如何使用 `if` 和 `else` 來為變數指派值：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_else

```

在此範例中，`if` 表達式的值被指派給變數 `y`。如果 `x` 大於 0，`y` 被指派為 1；否則，被指派為 0。`else` 區塊是必要的，因為 `if` 表達式的兩個分支都必須傳回相同類型的值。省略 `else` 區塊會導致編譯錯誤，因為它確保考慮了所有可能的分支並維持了類型安全。

條件表達式是 Move 中最重要的流程控制語句之一。它們評估使用者提供的輸入或儲存的資料以做出決策。一個關鍵的使用案例是 [`assert!` 巨集](./assert-and-abort)，它檢查條件是否為 true，如果不是則中斷執行。我們稍後將詳細探討這一點。

## 使用迴圈重複語句 (Repeating Statements with Loops)

迴圈用於多次執行一段程式碼。Move 有兩種內建的迴圈類型：`loop` 和 `while`。在許多情況下它們可以互換使用，但通常 `while` 用於預先知道迭代次數的情況，而 `loop` 用於預先不知道迭代次數或有多個退出點的情況。

迴圈對於處理集合（如向量）或重複執行程式碼直到滿足特定條件非常有用。但是，請務必小心避免無限迴圈，這會耗盡 Gas 限制並導致交易中斷。

## while 迴圈

只要相關的布林表達式評估為 true，`while` 語句就會重複執行一段程式碼。正如我們在 `if` 中看到的，布林表達式在每次迴圈迭代之前都會被評估。此外，與條件語句一樣，`while` 迴圈也是一個表達式，如果後面還有其他表達式，則需要分號。

`while` 迴圈的語法為：

```move
while (<布林表達式>) { <多個表達式>; };
```

這是一個具有非常簡單條件的 `while` 迴圈範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=while_loop

```

## 無限 loop

現在讓我們想像一種布林表達式始終為 `true` 的情況。例如，如果我們直接將 `true` 傳遞給 `while` 條件。這與 `loop` 語句的功能類似，不同之處在於 `while` 會評估一個條件。

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_while

```

無限 `while` 迴圈（或條件始終為 `true` 的 `while` 迴圈）等同於 `loop`。建立 `loop` 的語法非常直觀：

```move
loop { <多個表達式>; };
```

讓我們使用 `loop` 代替 `while` 來重寫前面的範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_loop

```

無限迴圈在 Move 中很少具有實用性，因為每項運算都會消耗 Gas，無限迴圈必然會導致 Gas 耗盡。如果您發現自己在運用迴圈，請考慮是否有更好的方法，因為許多使用案例可以使用其他流程控制結構更有效地處理。儘管如此，當 `loop` 與 `break` 和 `continue` 語句結合使用時，對於建立受控且靈活的循環行為可能非常有用。

## 提早退出迴圈 (Exiting a Loop Early)

正如我們已經提到的，無限迴圈本身是沒什麼用處的。這就是我們引入 `break` 和 `continue` 語句的原因。它們分別用於提早退出迴圈和跳過當前迭代的剩餘部分。

`break` 語句的語法如下（不含分號）：

```move
break
```

`break` 語句用於停止迴圈的執行並提早退出。它通常與條件語句結合使用，以便在滿足特定條件時退出迴圈。為了說明這一點，讓我們將前面範例中的無限 `loop` 轉換為外觀和行為更像 `while` 迴圈的結構：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=break_loop

```

與 `while` 迴圈幾乎一模一樣，對吧？當 `x` 為 5 時，使用 `break` 語句退出迴圈。如果我們移除 `break` 語句，迴圈將永遠執行下去，就像前面的範例一樣。

## 跳過迭代 (Skipping an Iteration)

`continue` 語句用於跳過當前迭代的剩餘部分並開始下一次迭代。與 `break` 類似，它常與條件語句結合使用，以便在滿足特定條件時跳過迭代的其餘部分。

`continue` 語句的語法如下（不含分號）：

```move
continue
```

下面的範例跳過奇數，僅列印 0 到 10 之間的偶數：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=continue_loop

```

`break` 和 `continue` 語句在 `while` 和 `loop` 迴圈中都可以使用。

## 提早傳回 (Early Return)

`return` 語句用於提早退出 [函式](./function) 並傳回一個值。它通常與條件語句結合使用，以便在滿足特定條件時退出函式。`return` 語句的語法為：

```move
return <表達式>
```

這是一個在滿足特定條件時傳回值的函式範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=return_statement

```

與許多其他語言不同，函式中的最後一個表達式不需要 `return` 語句。函式區塊中的最後一個表達式會自動傳回。但是，當我們想在滿足特定條件時提早退出函式時，`return` 語句非常有用。

## 延伸閱讀

- Move 參考手冊中的 [流程控制 (Control Flow)](./../../reference/control-flow) 章節。
