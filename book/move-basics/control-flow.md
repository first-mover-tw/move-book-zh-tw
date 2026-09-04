---
description: Move 中的控制流程 (Control flow)：if/else 運算式 (if/else expressions)、while 與 loop 結構 (while and loop constructs)，以及 break、continue 和 return 陳述式 (break, continue, and return statements)。
title: 控制流程 (Control Flow)
keywords:
  - Move
  - Sui
  - Move tutorial
  - control
  - flow
questions:
  - What is Control Flow in Move?
  - How do I use Control Flow in Move?
  - What is Conditional Statements in Move?
  - What is Repeating Statements with Loops in Move?
answer: 'Control flow in Move: if/else expressions, while and loop constructs, break, continue, and return statements.'
goal:
  description: 'Reader understands control flow in Move: if/else expressions, while and loop constructs, break, continue, and return statements'
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

# 控制流程 (Control Flow) {#control-flow}

控制流程陳述式決定哪些程式碼要執行、執行多少次，以及何時停止。它們用於
做出決策、重複執行一個程式碼區塊，或提早離開程式碼區塊。Move 包含下列
控制流程陳述式（下方將詳細說明）：

- [`if` 與 `if-else`](#conditional-statements)－決定是否執行一個程式碼區塊
- [`loop` 與 `while` 迴圈](#repeating-statements-with-loops)－重複執行一個程式碼區塊
- [`break` 與 `continue` 陳述式](#exiting-a-loop-early)－提早離開迴圈
- [具標籤的控制流程](#labeled-control-flow)－從巢狀迴圈或區塊中指定外層迴圈或區塊
- [`return`](#early-return) 陳述式－提早離開函式

## 條件陳述式 (Conditional Statements) {#conditional-statements}

`if` 運算式用於在程式中做出決策。它會評估一個
[布林](./primitive-types#booleans)運算式，並在該運算式為 true 時執行一個程式碼區塊。
搭配 `else` 時，若該運算式為 false，則可以執行不同的程式碼區塊。

`if` 運算式的語法如下：

```move
if (<bool_expression>) <expression>;
if (<bool_expression>) <expression> else <expression>;
```

與其他任何運算式一樣，若後方還有其他運算式，`if` 就需要加上分號。`else` 關鍵字為選用，
但當結果值被指派給變數時則不可省略，因為所有分支都必須回傳值以確保型別安全。讓我們透過
以下範例，檢視 Move 中 `if` 運算式的運作方式：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_condition

```

讓我們看看如何使用 `if` 和 `else` 將值指派給變數：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_else

```

在此範例中，`if` 運算式的值會被指派給變數 `y`。如果 `x` 大於
0，`y` 會被指派為值 1；否則會被指派為 0。此處需要 `else` 區塊，
因為 `if` 運算式的兩個分支都必須具有相同型別。省略 `else` 時，
false 分支預設為單元值 `()`，因此，將沒有 `else` 的 `if` 指派給變數
會造成型別錯誤：

```move
let y = if (x > 0) 1;
//      ^^^^^^^^^^^^ 錯誤！預期為 'u64'，但找到 '()'——缺少的
//                   else 分支預設為單元值 `()`。
```

若要在兩個以上的分支間選擇，可以使用 `else if` 串接 `if` 運算式。
分支會由上而下檢查，並採用第一個條件為 true 的分支：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=else_if

```

條件運算式是 Move 中最重要的控制流程陳述式之一。它們會評估使用者提供的輸入或已儲存的資料，
以做出決策。其中一個重要用途是 [`assert!` 巨集](./assert-and-abort)，它會檢查條件是否為 true，
若非 true，便會中止執行。我們會在本章稍後詳細探討它。

## 使用迴圈重複執行陳述式 (Repeating Statements with Loops) {#repeating-statements-with-loops}

迴圈用於多次執行一個原始碼區塊。Move 有兩種內建的迴圈類型：
`loop` 與 `while`。在許多情況下，兩者可以互換使用，但通常在預先知道迭代次數時使用 `while`，而在預先不知道迭代次數或有多個離開點時使用 `loop`。

迴圈適合用來處理集合，例如向量，或重複執行一個原始碼區塊，直到符合特定條件為止。不過，請注意避免無限迴圈，因為這可能耗盡 gas 限制並導致交易中止。

> 實務上，Move 中手寫的迴圈相對少見。對集合進行迭代通常會以較高層級的[巨集](./macros)表示，例如 `do!`、`map!` 與 `fold!`，這些巨集會在[向量](./vector#vector-macros)章節中說明。此處描述的 `loop` 與 `while` 結構是這些巨集所建立於其上的基本元素；當迭代不適合簡單的集合走訪時，它們仍是合適的工具。

## `while` 迴圈 (The `while` Loop) {#the-while-loop}

只要相關的布林運算式評估為 true，`while` 陳述式就會重複執行一個程式碼區塊。如同我們在 `if` 中所見，布林運算式會在迴圈的每次迭代前進行評估。此外，和條件陳述式一樣，`while` 迴圈是一個運算式；若其後還有其他運算式，則需要加上分號。

`while` 迴圈的語法如下：

```move
while (<bool_expression>) { <expressions>; };
```

以下是具有非常簡單條件的 `while` 迴圈範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=while_loop

```

## 無限 `loop` 迴圈 (Infinite `loop`) {#infinite-loop}

現在讓我們想像一個布林運算式永遠為 `true` 的情境。例如，如果我們將 `true` 直接傳入 `while` 條件。這與 `loop` 陳述式的運作方式類似，但 `while` 會評估條件。

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_while

```

無限 `while` 迴圈，或條件永遠為 `true` 的 `while` 迴圈，等同於 `loop`。建立 `loop` 的語法很直接：

```move
loop { <expressions>; };
```

讓我們使用 `loop` 取代 `while`，重寫前一個範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_loop

```

無限迴圈在 Move 中很少實用，因為每項操作都會消耗 gas，而無限迴圈終將導致 gas 耗盡。如果你發現自己正在使用迴圈，請考慮是否有更好的方法，因為許多使用情境可透過其他控制流程結構更有效率地處理。不過，將 `loop` 與 `break` 和 `continue` 陳述式結合使用，或許能建立可控且彈性的迴圈行為。

## 提早離開迴圈 (Exiting a Loop Early) {#exiting-a-loop-early}

如同我們先前提到的，無限迴圈本身相當沒有用。因此，我們引入了 `break` 與 `continue` 陳述式。它們分別用於提早離開迴圈，以及略過目前反覆執行的其餘部分。

`break` 陳述式的語法如下（不含分號）：

```move
break
```

`break` 陳述式用於停止迴圈的執行並提早離開迴圈。它經常與條件陳述式搭配使用，讓迴圈在符合特定條件時離開。為了說明這點，讓我們將前一個範例中的無限 `loop` 改成看起來與運作方式都更接近 `while` 迴圈的形式：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=break_loop

```

幾乎和 `while` 迴圈完全相同，對吧？當 `x` 為 5 時，會使用 `break` 陳述式離開迴圈。若移除 `break` 陳述式，迴圈將會永遠執行，就像前一個範例一樣。

## 跳過迭代 (Skipping an Iteration) {#skipping-an-iteration}

`continue` 陳述式用於跳過目前迭代的其餘部分，並開始下一次迭代。
與 `break` 類似，它會搭配條件陳述式使用，當符合特定條件時跳過該次
迭代的其餘部分。

`continue` 陳述式的語法如下（不含分號）：

```move
continue
```

下列範例會跳過奇數，並且只印出從 0 到 10 的偶數：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=continue_loop

```

`break` 與 `continue` 陳述式都可用於 `while` 和 `loop` 迴圈。

## 具標籤的控制流程 (Labeled Control Flow) {#labeled-control-flow}

預設情況下，`break` 和 `continue` 會作用於包圍它們的最內層迴圈。當迴圈巢狀時，這會造成問題：從內層迴圈中，沒有方法可以跳出外層迴圈。為解決此問題，Move 可讓你為迴圈附加一個*標籤*，然後明確指定 `break` 或 `continue` 要作用的目標。

標籤是前綴為單引號的名稱，放在 `loop` 或 `while` 關鍵字之前。接著，你可以撰寫 `break 'label` 或 `continue 'label`，跳至帶有標籤的迴圈，而非最內層迴圈：

```move
'outer: loop {
    while (condition) {
        // 一次跳出兩個迴圈。
        break 'outer;

        // 跳至外層迴圈的下一次迭代。
        continue 'outer;
    };
};
```

考慮在網格中搜尋：這是一個列的向量，而每一列本身也是向量。找到所尋找的值後，我們希望完全停止掃描，而不只是完成目前這一列。為外層迴圈加上標籤，可讓內層 `while` 迴圈一步中止整個搜尋：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=labeled_loop

```

請注意，`break` 陳述式也會攜帶值：`break false` 和 `break 'search true`。`loop` 是運算式，因此跳出它可產生結果——此處為函式回傳的布林值。這是 `loop` 特有的行為：`while` 迴圈一律求值為單位值 `()`，所以其 `break` 無法攜帶值。若沒有標籤，要跳出兩個迴圈就必須使用額外的旗標變數，並在外層迴圈進行第二次檢查。

### 具標籤的區塊 (Labeled Blocks) {#labeled-blocks}

標籤不限於迴圈。一般區塊 `{ ... }` 也可以加上標籤，然後透過 `return 'label <value>` 提早離開。這適合用來計算具有多個可能提早結束點的值，而無須將邏輯抽取至獨立函式：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=labeled_block

```

此處的 `'result` 區塊會產生值，任何一個 `return 'result` 陳述式都可以提早結束它。這與上方提到的迭代[巨集](./macros)搭配時尤其強大，因為具標籤的區塊可讓 lambda 以結果跳出迭代。

有兩項規則值得記住：

- 標籤只能放在 `loop`、`while` 或區塊 `{}` 上——**不能**放在 `if` 運算式上。若要為條件式加上標籤，請為其周圍的區塊加上標籤（`if` 分支本身就是區塊）。
- `break` 和 `continue` 僅能搭配*迴圈*標籤使用，而 `return` 僅能搭配*區塊*標籤使用。混用它們（例如對區塊標籤使用 `break`）會造成編譯錯誤。

> Move Reference 的[具標籤控制流程 (Labeled Control Flow)](./../../reference/control-flow/labeled-control-flow)章節會更詳細說明這些形式，包括它們與巨集的互動。

## 提早回傳 (Early Return) {#early-return}

`return` 陳述式用於提早離開 [函式](./function) 並回傳值。它通常會與條件陳述式搭配使用，在符合特定條件時離開函式。`return` 陳述式的語法如下：

```move
return <expression>
```

以下是一個在符合特定條件時回傳值的函式範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=return_statement

```

不同於許多其他語言，函式中的最後一個運算式不需要使用 `return` 陳述式。函式區塊中的最後一個運算式會自動回傳。不過，當我們想在符合特定條件時提早離開函式，`return` 陳述式就很有用。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [控制流程](./../../reference/control-flow) 章節。
